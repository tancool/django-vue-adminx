from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from django.utils.module_loading import import_string
from django.utils import timezone

from .models import Job

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
	global _scheduler
	if _scheduler is None:
		_scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))
	return _scheduler


def start_scheduler() -> None:
	scheduler = get_scheduler()
	if not scheduler.running:
		scheduler.start()


def _build_trigger(job: Job):
	if job.trigger_type == 'cron':
		return CronTrigger(
			second=job.cron_second or '0',
			minute=job.cron_minute or '*',
			hour=job.cron_hour or '*',
			day=job.cron_day or '*',
			month=job.cron_month or '*',
			day_of_week=job.cron_day_of_week or '*',
		)
	elif job.trigger_type == 'interval':
		return IntervalTrigger(seconds=max(1, job.interval_seconds))
	else:
		return DateTrigger(run_date=job.once_run_at or timezone.now())


def _import_func(func_path: str):
	return import_string(func_path)


def add_or_update_job(job: Job) -> None:
	scheduler = get_scheduler()
	if not job.enabled:
		remove_job(job)
		return
	trigger = _build_trigger(job)
	func = _import_func(job.func_path)
	job_id = job.job_id or f'task-{job.pk}'
	# remove existing
	try:
		scheduler.remove_job(job_id)
	except Exception:
		pass
	scheduler.add_job(
		func=func,
		trigger=trigger,
		args=job.args or [],
		kwargs=job.kwargs or {},
		id=job_id,
		replace_existing=True,
	)
	if job.job_id != job_id:
		Job.objects.filter(pk=job.pk).update(job_id=job_id)


def remove_job(job: Job) -> None:
	if not job.job_id:
		return
	try:
		get_scheduler().remove_job(job.job_id)
	except Exception:
		pass


def sync_all_jobs_from_db() -> None:
	for job in Job.objects.filter(enabled=True):
		try:
			add_or_update_job(job)
		except Exception:
			# skip broken jobs
			continue


def run_job_now(job: Job) -> None:
	func = _import_func(job.func_path)
	func(*(job.args or []), **(job.kwargs or {}))
	Job.objects.filter(pk=job.pk).update(last_run_at=timezone.now())

