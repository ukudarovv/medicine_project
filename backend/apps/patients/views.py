from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, CanAccessPatient
from .models import Patient, Representative, PatientFile
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientSearchSerializer,
    RepresentativeSerializer,
    PatientFileSerializer
)
import re


class PatientViewSet(viewsets.ModelViewSet):
    """
    Patient CRUD with deduplication
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.filter(organization=user.organization)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name/phone/iin
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(iin__icontains=search)
            )
        
        return queryset.select_related('organization').prefetch_related(
            'representatives', 'files'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanAccessPatient()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search for patients by phone or IIN (for deduplication)
        POST /api/v1/patients/search
        {
            "phone": "+77001234567",
            "iin": "123456789012"
        }
        """
        serializer = PatientSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data.get('phone')
        iin = serializer.validated_data.get('iin')
        
        queryset = Patient.objects.filter(organization=request.user.organization)
        
        # Search by phone (normalized)
        if phone:
            normalized = re.sub(r'\D', '', phone)
            queryset = queryset.filter(
                phone__iregex=f'[^0-9]*{normalized}[^0-9]*'
            )
        
        # Search by IIN
        if iin:
            queryset = queryset.filter(iin=iin)
        
        patients = queryset[:10]  # Limit to 10 results
        serializer = PatientListSerializer(patients, many=True)
        
        return Response({
            'found': patients.exists(),
            'count': patients.count(),
            'patients': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        """
        Add balance to patient account
        """
        patient = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        patient.balance += amount
        patient.save(update_fields=['balance'])
        
        return Response({
            'balance': float(patient.balance),
            'message': f'Added {amount} to balance'
        })


class RepresentativeViewSet(viewsets.ModelViewSet):
    """
    Patient representative CRUD
    """
    queryset = Representative.objects.all()
    serializer_class = RepresentativeSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        
        queryset = Representative.objects.filter(
            patient__organization=user.organization
        )
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset


class PatientFileViewSet(viewsets.ModelViewSet):
    """
    Patient file CRUD
    """
    queryset = PatientFile.objects.all()
    serializer_class = PatientFileSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        
        queryset = PatientFile.objects.filter(
            patient__organization=user.organization
        )
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

