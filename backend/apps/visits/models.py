from django.db import models
from apps.calendar.models import Appointment
from apps.services.models import Service, ICDCode
from apps.org.models import Resource


class Visit(models.Model):
    """
    Visit model - actual patient visit based on appointment
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершён'),
        ('canceled', 'Отменён'),
    ]
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='visit'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    comment = models.TextField(blank=True, help_text='Комментарий врача')
    is_patient_arrived = models.BooleanField(default=False, help_text='Пациент пришёл')
    arrived_at = models.DateTimeField(null=True, blank=True)
    
    # Medical data
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_visits'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'visits'
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Visit #{self.id} - {self.appointment.patient.full_name}"


class VisitService(models.Model):
    """
    Service performed during visit
    """
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='visit_services'
    )
    icd = models.ForeignKey(
        ICDCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visit_services'
    )
    
    # Quantities and pricing
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    duration = models.IntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Dental specific
    tooth_number = models.CharField(max_length=10, blank=True, help_text='Номер зуба')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'visit_services'
        verbose_name = 'Visit Service'
        verbose_name_plural = 'Visit Services'
    
    def __str__(self):
        return f"{self.service.name} - {self.visit}"
    
    @property
    def total_price(self):
        """Calculate total price after discount"""
        subtotal = self.price * self.qty
        return subtotal - self.discount_amount - (subtotal * self.discount_percent / 100)


class VisitPrescription(models.Model):
    """
    Prescription issued during visit
    """
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    medication = models.CharField(max_length=500)
    dosage = models.CharField(max_length=200)
    frequency = models.CharField(max_length=200)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'visit_prescriptions'
        verbose_name = 'Visit Prescription'
        verbose_name_plural = 'Visit Prescriptions'
    
    def __str__(self):
        return f"{self.medication} - {self.visit}"


class VisitResource(models.Model):
    """
    Resources used during visit
    """
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE
    )
    used_time = models.IntegerField(help_text='Usage time in minutes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'visit_resources'
        verbose_name = 'Visit Resource'
        verbose_name_plural = 'Visit Resources'
    
    def __str__(self):
        return f"{self.resource.name} - {self.visit}"

