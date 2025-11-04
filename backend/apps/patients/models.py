from django.db import models
from django.contrib.postgres.fields import ArrayField
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
    
    # Marketing
    tags = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text='Теги для сегментации (ортодонтия, имплантация и т.д.)'
    )
    is_marketing_opt_in = models.BooleanField(
        default=False,
        help_text='Согласие на маркетинговые рассылки'
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


class PatientPhone(models.Model):
    """
    Additional patient phones
    """
    PHONE_TYPES = [
        ('mobile', 'Мобильный'),
        ('home', 'Домашний'),
        ('work', 'Рабочий'),
        ('other', 'Другой'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='additional_phones'
    )
    phone = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=PHONE_TYPES, default='mobile')
    note = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_phones'
        verbose_name = 'Patient Phone'
        verbose_name_plural = 'Patient Phones'
    
    def __str__(self):
        return f"{self.phone} ({self.get_type_display()}) - {self.patient.full_name}"


class PatientSocialNetwork(models.Model):
    """
    Patient social networks
    """
    NETWORK_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('vk', 'VKontakte'),
        ('other', 'Другое'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='social_networks'
    )
    network = models.CharField(max_length=20, choices=NETWORK_TYPES)
    username = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_social_networks'
        verbose_name = 'Patient Social Network'
        verbose_name_plural = 'Patient Social Networks'
    
    def __str__(self):
        return f"{self.get_network_display()}: {self.username} - {self.patient.full_name}"


class PatientContactPerson(models.Model):
    """
    Patient contact person (emergency contact)
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='contact_persons'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relation = models.CharField(max_length=100, help_text='Степень родства')
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_contact_persons'
        verbose_name = 'Patient Contact Person'
        verbose_name_plural = 'Patient Contact Persons'
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.relation}) - {self.patient.full_name}"


class PatientDisease(models.Model):
    """
    Patient dispensary diseases
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='diseases'
    )
    start_date = models.DateField(help_text='Дата начала наблюдения')
    end_date = models.DateField(null=True, blank=True, help_text='Дата прекращения наблюдения')
    diagnosis = models.TextField(help_text='Диагноз')
    icd_code = models.ForeignKey(
        'services.ICDCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    doctor = models.ForeignKey(
        'staff.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_diseases'
        verbose_name = 'Patient Disease'
        verbose_name_plural = 'Patient Diseases'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.diagnosis} - {self.patient.full_name}"


class PatientDiagnosis(models.Model):
    """
    Final (clarified) diagnoses
    """
    DIAGNOSIS_TYPES = [
        ('1', 'Первичный'),
        ('2', 'Повторный'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='diagnoses'
    )
    date = models.DateField()
    diagnosis = models.TextField(help_text='Заключительный диагноз')
    icd_code = models.ForeignKey(
        'services.ICDCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    type = models.CharField(max_length=1, choices=DIAGNOSIS_TYPES, default='1')
    doctor = models.ForeignKey(
        'staff.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_diagnoses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_diagnoses'
        verbose_name = 'Patient Diagnosis'
        verbose_name_plural = 'Patient Diagnoses'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.diagnosis} ({self.date}) - {self.patient.full_name}"


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


class PatientDoseLoad(models.Model):
    """
    Radiation dose tracking
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dose_loads')
    date = models.DateField()
    study_type = models.CharField(max_length=200, help_text='Вид исследования')
    dose = models.DecimalField(max_digits=10, decimal_places=2, help_text='Эффективная доза, мЗв')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_dose_loads'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.study_type} - {self.dose} мЗв"

