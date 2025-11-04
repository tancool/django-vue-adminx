from rest_framework import serializers

from apps.tasks.models import Job


class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		fields = '__all__'

