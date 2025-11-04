from django.db import models
from apps.org.models import Organization


class Patient(models.Model):
    """
    Patient model
    """
    SEX_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    
    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    
    # Contacts
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Identity
    iin = models.CharField(max_length=20, blank=True, db_index=True, help_text='ИИН')
    documents = models.JSONField(default=dict, blank=True, help_text='Документы (паспорт и т.д.)')
    
    # Consents and agreements
    consents = models.JSONField(
        default=dict,
        blank=True,
        help_text='Согласия (обработка данных, фото и т.д.)'
    )
    
    # Financial
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Баланс (предоплата/долг)'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Индивидуальная скидка (%)'
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text='Примечания')
    allergies = models.TextField(blank=True, help_text='Аллергии')
    medical_history = models.TextField(blank=True, help_text='Анамнез')
    
    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['iin']),
            models.Index(fields=['organization', 'phone']),
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    @property
    def age(self):
        """Calculate patient's age"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class Representative(models.Model):
    """
    Patient representative (for minors, elderly, etc.)
    """
    RELATION_CHOICES = [
        ('parent', 'Родитель'),
        ('guardian', 'Опекун'),
        ('spouse', 'Супруг(а)'),
        ('child', 'Ребенок'),
        ('other', 'Другое'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='representatives'
    )
    
    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    
    # Contacts
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Documents
    documents = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_representatives'
        verbose_name = 'Patient Representative'
        verbose_name_plural = 'Patient Representatives'
    
    def __str__(self):
        return f"{self.full_name} ({self.get_relation_display()}) - {self.patient.full_name}"
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


class PatientFile(models.Model):
    """
    Patient files (medical records, images, etc.)
    """
    FILE_TYPES = [
        ('medical_record', 'Medical Record'),
        ('lab_result', 'Lab Result'),
        ('image', 'Image'),
        ('xray', 'X-Ray'),
        ('consent', 'Consent Form'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='other')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='patients/%Y/%m/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_patient_files'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_files'
        verbose_name = 'Patient File'
        verbose_name_plural = 'Patient Files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"

