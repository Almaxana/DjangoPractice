from rest_framework import serializers
from .models import TimeSheetItem, Project


class TimeSheetItemSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(source='project', queryset=Project.objects.all())
    project_name = serializers.CharField(source='project.name', read_only=True)
    worker_username = serializers.CharField(source='worker.username', read_only=True)

    class Meta:
        model = TimeSheetItem
        fields = ['id', 'date', 'project_id', 'hours_number', 'comment', 'worker_username', 'project_name']

    def create(self, validated_data):
        validated_data['worker'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'project' in validated_data:
            instance.project = validated_data['project']
        instance.date = validated_data.get('date', instance.date)
        instance.hours_number = validated_data.get('hours_number', instance.hours_number)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance
