from rest_framework import serializers
from .models import Template, MessageLog


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'channel', 'key', 'subject', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'patient', 'appointment', 'channel', 'template_key', 'text', 'cost', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

