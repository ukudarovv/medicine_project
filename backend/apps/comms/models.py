from django.db import models
from apps.patients.models import Patient
from apps.calendar.models import Appointment


class Template(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    key = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'templates'
    
    def __str__(self):
        return f"{self.key} ({self.channel})"


class MessageLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=20)
    template_key = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_logs'
        ordering = ['-created_at']

