"""
EHR (Electronic Health Records) models

Unified model for all patient medical records across organizations
with support for multi-org consent-based access
"""
import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.patients.models import Patient
from apps.org.models import Organization
from apps.core.models import User


class EHRRecord(models.Model):
    """
    Unified electronic health record
    
    This model serves as a unified interface for all patient medical records,
    including visits, diagnoses, prescriptions, lab results, images, etc.
    """
    RECORD_TYPE_CHOICES = [
        ('visit_note', 'Запись визита'),
        ('diagnosis', 'Диагноз'),
        ('prescription', 'Рецепт'),
        ('lab_result', 'Результат анализа'),
        ('image', 'Изображение'),
        ('document', 'Документ'),
        ('procedure', 'Процедура'),
        ('allergy', 'Аллергия'),
        ('vaccination', 'Прививка'),
        ('other', 'Другое'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Patient and organization
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='ehr_records'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='ehr_records',
        help_text='Organization that created this record'
    )
    
    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ehr_records_authored',
        help_text='User who created this record'
    )
    
    # Record type and content
    record_type = models.CharField(
        max_length=50,
        choices=RECORD_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(max_length=500, help_text='Record title/summary')
    payload = models.JSONField(
        default=dict,
        help_text='Record data (structure depends on record_type)'
    )
    
    # Related object (polymorphic reference to existing models)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Type of related object (Visit, PatientFile, etc.)'
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of related object'
    )
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Versioning
    version = models.IntegerField(
        default=1,
        help_text='Version number for this record'
    )
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        help_text='Previous version of this record (if edited)'
    )
    
    # Flags
    is_external = models.BooleanField(
        default=False,
        help_text='Created by external organization (via consent)'
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text='Soft delete flag'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ehr_records'
        verbose_name = 'EHR Record'
        verbose_name_plural = 'EHR Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'record_type', 'created_at']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['record_type', 'created_at']),
            models.Index(fields=['is_deleted', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_record_type_display()} - {self.patient.full_name} ({self.created_at.date()})"
    
    def create_new_version(self, updated_data: dict, user: User):
        """
        Create a new version of this record (for edits)
        
        Args:
            updated_data: New payload data
            user: User making the change
            
        Returns:
            New EHRRecord instance
        """
        new_version = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.organization,
            author=user,
            record_type=self.record_type,
            title=self.title,
            payload=updated_data,
            content_type=self.content_type,
            object_id=self.object_id,
            version=self.version + 1,
            previous_version=self,
            is_external=self.is_external
        )
        return new_version
    
    def soft_delete(self):
        """Soft delete this record"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])


class EHRAdapter:
    """
    Adapter to convert existing models (Visit, PatientFile, etc.) to EHRRecord format
    """
    
    @staticmethod
    def from_visit(visit):
        """Convert Visit to EHRRecord payload"""
        from apps.visits.models import Visit
        
        return {
            'visit_id': str(visit.id),
            'appointment_id': str(visit.appointment.id) if visit.appointment else None,
            'doctor': visit.appointment.employee.full_name if visit.appointment else None,
            'complaints': visit.complaints,
            'diagnosis': visit.diagnosis,
            'treatment': visit.treatment,
            'recommendations': visit.recommendations,
            'status': visit.status,
            'arrived_at': visit.arrived_at.isoformat() if visit.arrived_at else None,
            'started_at': visit.started_at.isoformat() if visit.started_at else None,
            'finished_at': visit.finished_at.isoformat() if visit.finished_at else None,
        }
    
    @staticmethod
    def from_patient_diagnosis(diagnosis):
        """Convert PatientDiagnosis to EHRRecord payload"""
        return {
            'diagnosis_id': diagnosis.id,
            'date': diagnosis.date.isoformat(),
            'diagnosis': diagnosis.diagnosis,
            'icd_code': diagnosis.icd_code.code if diagnosis.icd_code else None,
            'icd_name': str(diagnosis.icd_code) if diagnosis.icd_code else None,
            'type': diagnosis.type,
            'doctor': diagnosis.doctor.full_name if diagnosis.doctor else None,
        }
    
    @staticmethod
    def from_patient_file(file):
        """Convert PatientFile to EHRRecord payload"""
        return {
            'file_id': file.id,
            'file_type': file.file_type,
            'title': file.title,
            'description': file.description,
            'file_url': file.file.url if file.file else None,
            'uploaded_by': file.uploaded_by.get_full_name() if file.uploaded_by else None,
        }
    
    @staticmethod
    def from_medical_examination(exam):
        """Convert MedicalExamination to EHRRecord payload"""
        return {
            'exam_id': exam.id,
            'exam_type': exam.exam_type,
            'exam_date': exam.exam_date.isoformat(),
            'work_profile': exam.work_profile,
            'conclusion': exam.conclusion,
            'fit_for_work': exam.fit_for_work,
            'restrictions': exam.restrictions,
            'next_exam_date': exam.next_exam_date.isoformat() if exam.next_exam_date else None,
            'commission_members': exam.commission_members,
        }

