from django.db import models
from django.utils import timezone


class Job(models.Model):
	TRIGGER_CHOICES = (
		('cron', 'Cron'),
		('interval', 'Interval'),
		('date', 'Once'),
	)

	name = models.CharField(max_length=100, unique=True, verbose_name='任务名称')
	description = models.CharField(max_length=255, blank=True, default='', verbose_name='描述')
	func_path = models.CharField(max_length=255, verbose_name='函数路径')  # e.g. apps.tasks.examples:demo_task
	trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='cron', verbose_name='触发类型')

	# cron fields
	cron_second = models.CharField(max_length=64, blank=True, default='0')
	cron_minute = models.CharField(max_length=64, blank=True, default='*')
	cron_hour = models.CharField(max_length=64, blank=True, default='*')
	cron_day = models.CharField(max_length=64, blank=True, default='*')
	cron_month = models.CharField(max_length=64, blank=True, default='*')
	cron_day_of_week = models.CharField(max_length=64, blank=True, default='*')

	# interval
	interval_seconds = models.PositiveIntegerField(default=60)

	# date
	once_run_at = models.DateTimeField(null=True, blank=True)

	args = models.JSONField(default=list, blank=True)
	kwargs = models.JSONField(default=dict, blank=True)
	enabled = models.BooleanField(default=True)
	job_id = models.CharField(max_length=128, blank=True, default='', editable=False)
	last_run_at = models.DateTimeField(null=True, blank=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = '定时任务'
		verbose_name_plural = '定时任务'

	def __str__(self):
		return self.name

