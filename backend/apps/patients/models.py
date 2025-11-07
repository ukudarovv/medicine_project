from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from apps.org.models import Organization
from .utils.encryption import encrypt_iin, decrypt_iin, hash_iin, mask_iin


class Patient(models.Model):
    """
    Patient model
    """
    SEX_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    
    organizations = models.ManyToManyField(
        Organization,
        related_name='patients',
        help_text='Организации, в которых зарегистрирован пациент'
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
    iin = models.CharField(max_length=20, blank=True, db_index=True, help_text='ИИН (legacy, use iin_enc for new records)')
    iin_enc = models.TextField(blank=True, help_text='Encrypted IIN (AES-256 via Fernet)')
    iin_hash = models.CharField(max_length=64, blank=True, db_index=True, help_text='SHA-256 hash of IIN for lookups')
    iin_verified = models.BooleanField(default=False, help_text='ИИН верифицирован')
    iin_verified_at = models.DateTimeField(null=True, blank=True, help_text='Дата верификации ИИН')
    documents = models.JSONField(default=dict, blank=True, help_text='Документы (паспорт и т.д.)')
    
    # KZ Address (KATO)
    kato_address = models.JSONField(
        default=dict,
        blank=True,
        help_text='Адрес по КАТО (region, district, city, street, building, apartment, kato_code, coordinates)'
    )
    
    # OSMS (Kazakhstan medical insurance)
    OSMS_STATUS_CHOICES = [
        ('insured', 'Застрахован'),
        ('not_insured', 'Не застрахован'),
    ]
    OSMS_CATEGORY_CHOICES = [
        ('employee', 'Наемный работник'),
        ('self_employed', 'ИП/Самозанятый'),
        ('socially_vulnerable', 'Социально уязвимый'),
        ('civil_servant', 'Бюджетник'),
        ('pensioner', 'Пенсионер'),
        ('other', 'Другое'),
    ]
    osms_status = models.CharField(
        max_length=20,
        choices=OSMS_STATUS_CHOICES,
        blank=True,
        help_text='Статус ОСМС'
    )
    osms_category = models.CharField(
        max_length=30,
        choices=OSMS_CATEGORY_CHOICES,
        blank=True,
        help_text='Категория плательщика ОСМС'
    )
    osms_verified_at = models.DateTimeField(null=True, blank=True, help_text='Дата проверки статуса ОСМС')
    
    # Consents and agreements
    consents = models.JSONField(
        default=dict,
        blank=True,
        help_text='Согласия (обработка данных, фото и т.д.)'
    )
    
    # Marketing
    tags = models.JSONField(
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
            models.Index(fields=['iin_hash']),
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def organization(self):
        """
        Get primary organization (first one added) for backward compatibility
        """
        return self.organizations.first()
    
    def has_organization(self, organization):
        """
        Check if patient belongs to specific organization
        """
        return self.organizations.filter(id=organization.id).exists()
    
    def add_organization(self, organization):
        """
        Add organization to patient
        """
        if not self.has_organization(organization):
            self.organizations.add(organization)
            return True
        return False
    
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
    
    @property
    def iin_decrypted(self):
        """Get decrypted IIN (use with caution - only for authorized users)"""
        if self.iin_enc:
            return decrypt_iin(self.iin_enc)
        return self.iin  # Fallback to legacy plain IIN
    
    @property
    def iin_masked(self):
        """Get masked IIN for display"""
        iin = self.iin_decrypted
        return mask_iin(iin) if iin else ''
    
    def set_iin(self, plain_iin: str):
        """
        Set IIN with automatic encryption and hashing
        
        Args:
            plain_iin: Plain IIN string (12 digits)
        """
        if plain_iin:
            # Remove whitespace and dashes
            plain_iin = plain_iin.replace(' ', '').replace('-', '')
            
            # Encrypt and hash
            self.iin_enc = encrypt_iin(plain_iin)
            self.iin_hash = hash_iin(plain_iin)
            
            # Keep legacy field for backward compatibility (will be removed in Phase 4)
            self.iin = plain_iin
        else:
            self.iin_enc = ''
            self.iin_hash = ''
            self.iin = ''
    
    def save(self, *args, **kwargs):
        """Override save to auto-encrypt IIN if needed"""
        # If iin is set but iin_enc is not, encrypt it
        if self.iin and not self.iin_enc:
            self.set_iin(self.iin)
        
        super().save(*args, **kwargs)


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


class ConsentHistory(models.Model):
    """
    Consent history for audit purposes (KZ compliance)
    """
    CONSENT_TYPE_CHOICES = [
        ('personal_data', 'Обработка персональных данных'),
        ('medical_intervention', 'Медицинское вмешательство'),
        ('sms_marketing', 'SMS-рассылки'),
        ('whatsapp_marketing', 'WhatsApp-рассылки'),
    ]
    STATUS_CHOICES = [
        ('accepted', 'Принято'),
        ('revoked', 'Отозвано'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consent_history'
    )
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, help_text='User agent браузера')
    accepted_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='accepted_consents',
        help_text='Пользователь, который зафиксировал согласие'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consent_history'
        verbose_name = 'Consent History'
        verbose_name_plural = 'Consent Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'consent_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_consent_type_display()} ({self.get_status_display()})"


# ==================== Sprint 3: Medical Examinations ====================


class MedicalExamination(models.Model):
    """
    Medical examination (occupational/periodic) - Sprint 3
    Медосмотр (производственный/периодический)
    """
    EXAM_TYPES = [
        ('preliminary', 'Предварительный'),
        ('periodic', 'Периодический'),
        ('extraordinary', 'Внеочередной'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_examinations'
    )
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    exam_date = models.DateField(help_text='Дата проведения осмотра')
    work_profile = models.TextField(blank=True, help_text='Профиль работы, условия труда')
    conclusion = models.TextField(blank=True, help_text='Заключение комиссии')
    fit_for_work = models.BooleanField(default=True, help_text='Годен к работе')
    restrictions = models.TextField(blank=True, help_text='Ограничения и рекомендации')
    next_exam_date = models.DateField(null=True, blank=True, help_text='Дата следующего осмотра')
    
    # Commission members stored as JSON
    commission_members = models.JSONField(
        default=list,
        blank=True,
        help_text='Члены комиссии: [{"doctor_id": 1, "specialty": "Терапевт", "conclusion": "..."}]'
    )
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_examinations'
        verbose_name = 'Medical Examination'
        verbose_name_plural = 'Medical Examinations'
        ordering = ['-exam_date']
        indexes = [
            models.Index(fields=['patient', 'exam_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_exam_type_display()} ({self.exam_date})"


class MedExamPastDisease(models.Model):
    """
    Past diseases for medical examination - Sprint 3
    Перенесенные заболевания
    """
    examination = models.ForeignKey(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='past_diseases'
    )
    icd_code = models.ForeignKey(
        'services.ICDCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    disease_name = models.CharField(max_length=300, help_text='Название заболевания')
    year = models.IntegerField(help_text='Год заболевания')
    note = models.TextField(blank=True)
    
    class Meta:
        db_table = 'medexam_past_diseases'
        verbose_name = 'Medical Exam Past Disease'
        verbose_name_plural = 'Medical Exam Past Diseases'
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.disease_name} ({self.year})"


class MedExamVaccination(models.Model):
    """
    Vaccinations for medical examination - Sprint 3
    Прививки
    """
    examination = models.ForeignKey(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='vaccinations'
    )
    vaccine_type = models.CharField(max_length=200, help_text='Тип вакцины')
    date = models.DateField(help_text='Дата прививки')
    revaccination_date = models.DateField(null=True, blank=True, help_text='Дата ревакцинации')
    serial_number = models.CharField(max_length=100, blank=True, help_text='Серия и номер вакцины')
    note = models.TextField(blank=True)
    
    class Meta:
        db_table = 'medexam_vaccinations'
        verbose_name = 'Medical Exam Vaccination'
        verbose_name_plural = 'Medical Exam Vaccinations'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.vaccine_type} ({self.date})"


class MedExamLabTest(models.Model):
    """
    Laboratory and instrumental tests for medical examination - Sprint 3
    Лабораторные и инструментальные исследования
    """
    TEST_TYPES = [
        ('blood_general', 'ОАК (Общий анализ крови)'),
        ('blood_biochem', 'Биохимия крови'),
        ('urine', 'ОАМ (Общий анализ мочи)'),
        ('ecg', 'ЭКГ'),
        ('xray', 'Рентгенография'),
        ('fluorography', 'Флюорография'),
        ('spirometry', 'Спирометрия'),
        ('audiometry', 'Аудиометрия'),
        ('vision_test', 'Проверка зрения'),
        ('other', 'Другое'),
    ]
    
    examination = models.ForeignKey(
        MedicalExamination,
        on_delete=models.CASCADE,
        related_name='lab_tests'
    )
    test_type = models.CharField(max_length=30, choices=TEST_TYPES)
    test_name = models.CharField(max_length=200, blank=True, help_text='Название исследования')
    result = models.TextField(help_text='Результат исследования')
    performed_date = models.DateField(help_text='Дата проведения')
    file = models.ForeignKey(
        PatientFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medexam_lab_tests',
        help_text='Прикрепленный файл с результатами'
    )
    
    class Meta:
        db_table = 'medexam_lab_tests'
        verbose_name = 'Medical Exam Lab Test'
        verbose_name_plural = 'Medical Exam Lab Tests'
        ordering = ['-performed_date']
    
    def __str__(self):
        return f"{self.get_test_type_display()} ({self.performed_date})"


# ==================== Sprint 3: Treatment Plans ====================


class TreatmentPlan(models.Model):
    """
    Treatment plan - Sprint 3
    План лечения
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активный'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='treatment_plans'
    )
    title = models.CharField(max_length=300, help_text='Название плана лечения')
    description = models.TextField(blank=True, help_text='Описание плана')
    
    # Pricing
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Общая стоимость плана'
    )
    total_cost_frozen = models.BooleanField(
        default=False,
        help_text='Цены зафиксированы (не изменяются при изменении прайса)'
    )
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField(help_text='Дата начала лечения')
    end_date = models.DateField(null=True, blank=True, help_text='Дата окончания лечения')
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_treatment_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_plans'
        verbose_name = 'Treatment Plan'
        verbose_name_plural = 'Treatment Plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"
    
    def calculate_total_cost(self):
        """Calculate total cost from all stages"""
        total = sum(
            stage.calculate_total_cost()
            for stage in self.stages.all()
        )
        return total


class TreatmentStage(models.Model):
    """
    Treatment plan stage - Sprint 3
    Этап плана лечения
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
    ]
    
    plan = models.ForeignKey(
        TreatmentPlan,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    order = models.IntegerField(default=0, help_text='Порядковый номер этапа')
    title = models.CharField(max_length=300, help_text='Название этапа')
    description = models.TextField(blank=True, help_text='Описание этапа')
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_stages'
        verbose_name = 'Treatment Stage'
        verbose_name_plural = 'Treatment Stages'
        ordering = ['plan', 'order']
    
    def __str__(self):
        return f"{self.plan.patient.full_name} - {self.title} (этап {self.order})"
    
    def calculate_total_cost(self):
        """Calculate total cost from all items in stage"""
        total = sum(item.calculate_total() for item in self.items.all())
        return total


class TreatmentStageItem(models.Model):
    """
    Service/product in treatment stage - Sprint 3
    Услуга/товар в этапе плана
    """
    stage = models.ForeignKey(
        TreatmentStage,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Связанная услуга из прайса'
    )
    description = models.CharField(max_length=500, help_text='Описание услуги/товара')
    
    # Quantities
    qty_planned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        help_text='Запланированное количество'
    )
    qty_completed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Выполненное количество'
    )
    
    # Pricing (frozen from plan creation)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, help_text='Цена за единицу')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Dental specific
    tooth_number = models.CharField(max_length=10, blank=True, help_text='Номер зуба (для стоматологии)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'treatment_stage_items'
        verbose_name = 'Treatment Stage Item'
        verbose_name_plural = 'Treatment Stage Items'
        ordering = ['stage', 'id']
    
    def __str__(self):
        return f"{self.description} x{self.qty_planned}"
    
    def calculate_total(self):
        """Calculate total price for this item"""
        subtotal = self.unit_price * self.qty_planned
        discount = subtotal * (self.discount_percent / 100)
        return subtotal - discount
    
    @property
    def completion_percent(self):
        """Calculate completion percentage"""
        if self.qty_planned == 0:
            return 0
        return float(self.qty_completed / self.qty_planned * 100)


class TreatmentPlanTemplate(models.Model):
    """
    Treatment plan template - Sprint 3
    Шаблон плана лечения
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='treatment_plan_templates'
    )
    name = models.CharField(max_length=300, help_text='Название шаблона')
    description = models.TextField(blank=True, help_text='Описание шаблона')
    
    # Template data: structure of stages and items
    template_data = models.JSONField(
        default=dict,
        help_text='Структура этапов и услуг: {"stages": [{"title": "...", "items": [...]}]}'
    )
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_plan_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_plan_templates'
        verbose_name = 'Treatment Plan Template'
        verbose_name_plural = 'Treatment Plan Templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class PatientVerification(models.Model):
    """
    SMS verification for patient registration
    Временное хранение данных для верификации пациента через SMS
    """
    # Temp data before verification
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='patient_verifications'
    )
    phone = models.CharField(max_length=20, db_index=True)
    verification_code = models.CharField(max_length=6)
    patient_data = models.JSONField(help_text='Temporary patient data before verification')
    
    # Status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0, help_text='Number of verification attempts')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Code expiration time')
    
    class Meta:
        db_table = 'patient_verifications'
        verbose_name = 'Patient Verification'
        verbose_name_plural = 'Patient Verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'is_verified']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.phone} - {'Verified' if self.is_verified else 'Pending'}"
    
    def is_expired(self):
        """Check if verification code is expired"""
        return timezone.now() > self.expires_at
    
    def verify(self, code):
        """Verify the code"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
        
        if self.is_expired():
            return False, 'Код истек. Запросите новый код.'
        
        if self.attempts > 3:
            return False, 'Превышено количество попыток. Запросите новый код.'
        
        if self.verification_code == code:
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save(update_fields=['is_verified', 'verified_at'])
            return True, 'Код подтвержден'
        
        return False, f'Неверный код. Осталось попыток: {3 - self.attempts}'
