"""
Views for EHR (Electronic Health Records) API
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from apps.consent.permissions import CanViewExternalRecords
from .models import EHRRecord
from .serializers import (
    EHRRecordSerializer,
    EHRRecordListSerializer,
    PatientEHRSummarySerializer
)


class EHRRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EHR records with consent-based access control
    """
    serializer_class = EHRRecordSerializer
    permission_classes = [IsAuthenticated, CanViewExternalRecords]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EHRRecordListSerializer
        return EHRRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        org = user.organization
        
        if not org:
            return EHRRecord.objects.none()
        
        # Base queryset - own records
        queryset = EHRRecord.objects.filter(
            organization=org,
            is_deleted=False
        )
        
        # Check if including external records
        include_external = self.request.query_params.get('include_external', 'false').lower() == 'true'
        
        if include_external:
            # Get active grants
            active_grants = self.request.get_active_grants()
            granted_patient_ids = active_grants.values_list('patient_id', flat=True)
            
            # Include records from other orgs for patients we have access to
            external_records = EHRRecord.objects.filter(
                patient_id__in=granted_patient_ids,
                is_deleted=False
            ).exclude(organization=org)
            
            # Combine own and external records
            queryset = queryset | external_records
        
        # Filter by patient if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            # Check access to this patient
            access_check = self.request.check_patient_access(patient_id, 'read_records')
            
            if not access_check['has_access']:
                return EHRRecord.objects.none()
            
            queryset = queryset.filter(patient_id=patient_id)
            
            # Log access
            self.request.log_patient_access(
                patient_id=patient_id,
                action='read',
                object_type='EHRRecord',
                details={'query_params': dict(self.request.query_params)}
            )
        
        # Filter by record type if provided
        record_type = self.request.query_params.get('record_type')
        if record_type:
            queryset = queryset.filter(record_type=record_type)
        
        return queryset.select_related(
            'patient', 'organization', 'author'
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Serializer will handle organization and author assignment
        # Also checks if this is an external write
        serializer.save()
        
        # Log creation
        instance = serializer.instance
        self.request.log_patient_access(
            patient_id=instance.patient_id,
            action='write',
            object_type='EHRRecord',
            object_id=str(instance.id),
            details={
                'record_type': instance.record_type,
                'title': instance.title
            }
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check access
        access_check = request.check_patient_access(instance.patient_id, 'read_records')
        
        if not access_check['has_access']:
            return Response(
                {'error': 'У вас нет доступа к этой записи'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log access
        request.log_patient_access(
            patient_id=instance.patient_id,
            action='read',
            object_type='EHRRecord',
            object_id=str(instance.id)
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if this is own record (external records cannot be edited, only versioned)
        if instance.organization != request.user.organization:
            return Response(
                {'error': 'Невозможно редактировать записи других организаций'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create new version instead of updating
        serializer = self.get_serializer(data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        new_version = instance.create_new_version(
            updated_data=serializer.validated_data.get('payload', instance.payload),
            user=request.user
        )
        
        # Log update
        request.log_patient_access(
            patient_id=instance.patient_id,
            action='write',
            object_type='EHRRecord',
            object_id=str(new_version.id),
            details={'previous_version_id': str(instance.id)}
        )
        
        result_serializer = self.get_serializer(new_version)
        return Response(result_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if this is own record
        if instance.organization != request.user.organization:
            return Response(
                {'error': 'Невозможно удалить записи других организаций'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        instance.soft_delete()
        
        # Log deletion
        request.log_patient_access(
            patient_id=instance.patient_id,
            action='write',
            object_type='EHRRecord',
            object_id=str(instance.id),
            details={'action': 'soft_delete'}
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def patient_summary(self, request):
        """
        Get summary of patient's EHR records across organizations
        """
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {'error': 'patient_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check access
        access_check = request.check_patient_access(patient_id, 'read_summary')
        if not access_check['has_access']:
            return Response(
                {'error': 'У вас нет доступа к этому пациенту'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.patients.models import Patient
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Пациент не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all accessible records for this patient
        own_records = EHRRecord.objects.filter(
            patient_id=patient_id,
            organization=request.user.organization,
            is_deleted=False
        )
        
        # Get external records if have access
        external_records = EHRRecord.objects.filter(
            patient_id=patient_id,
            is_deleted=False
        ).exclude(organization=request.user.organization)
        
        # Filter external records by grants
        active_grants = request.get_active_grants().filter(patient_id=patient_id)
        if not active_grants.exists():
            external_records = EHRRecord.objects.none()
        
        # Build summary
        total_records = own_records.count() + external_records.count()
        organizations = list(set(
            list(own_records.values_list('organization__name', flat=True)) +
            list(external_records.values_list('organization__name', flat=True))
        ))
        
        all_records = list(own_records) + list(external_records)
        last_updated = max([r.created_at for r in all_records]) if all_records else None
        
        summary = {
            'patient_id': patient.id,
            'patient_name': patient.full_name,
            'total_records': total_records,
            'own_records': own_records.count(),
            'external_records': external_records.count(),
            'organizations': organizations,
            'last_updated': last_updated
        }
        
        serializer = PatientEHRSummarySerializer(summary)
        return Response(serializer.data)

