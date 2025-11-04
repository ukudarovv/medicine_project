from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.http import HttpResponse
from apps.core.permissions import IsBranchMember, CanAccessVisit
from .models import Visit, VisitService, VisitPrescription, VisitResource, VisitFile
from .serializers import (
    VisitSerializer,
    VisitServiceSerializer,
    VisitPrescriptionSerializer,
    VisitResourceSerializer,
    VisitFileSerializer
)


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    # Temporarily disabled for development
    # permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        # TODO: Enable organization filtering in production
        # user = self.request.user
        # return Visit.objects.filter(
        #     appointment__branch__organization=user.organization
        # ).select_related('appointment__patient', 'appointment__employee')
        return Visit.objects.all().select_related('appointment__patient', 'appointment__employee', 'appointment__branch')
    
    def get_permissions(self):
        # Temporarily disabled for development
        # if self.action in ['retrieve', 'update', 'partial_update']:
        #     return [IsAuthenticated(), CanAccessVisit()]
        # return super().get_permissions()
        return []
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_arrived(self, request, pk=None):
        """Mark patient as arrived"""
        from django.utils import timezone
        visit = self.get_object()
        visit.is_patient_arrived = True
        visit.arrived_at = timezone.now()
        visit.save(update_fields=['is_patient_arrived', 'arrived_at'])
        return Response(VisitSerializer(visit).data)
    
    @action(detail=True, methods=['get'])
    def print_extract(self, request, pk=None):
        """Print visit extract"""
        from datetime import datetime
        visit = self.get_object()
        
        context = {
            'visit': visit,
            'patient': visit.appointment.patient,
            'organization': visit.appointment.branch.organization,
            'doctor': visit.appointment.employee,
            'current_date': datetime.now().strftime('%d.%m.%Y'),
            'prescriptions': visit.prescriptions.all(),
        }
        
        html = render_to_string('visit_extract.html', context)
        
        # Return HTML (can be converted to PDF with WeasyPrint or similar)
        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = f'inline; filename="visit_{visit.id}_extract.html"'
        return response
    
    @action(detail=True, methods=['post'])
    def upload_file(self, request, pk=None):
        """Upload file to visit"""
        visit = self.get_object()
        
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'File is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        visit_file = VisitFile.objects.create(
            visit=visit,
            file=file_obj,
            file_type=request.data.get('file_type', 'other'),
            title=request.data.get('title', file_obj.name),
            description=request.data.get('description', ''),
            uploaded_by=request.user
        )
        
        serializer = VisitFileSerializer(visit_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VisitServiceViewSet(viewsets.ModelViewSet):
    queryset = VisitService.objects.all()
    serializer_class = VisitServiceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        visit_id = self.request.query_params.get('visit')
        queryset = VisitService.objects.filter(
            visit__appointment__branch__organization=user.organization
        )
        if visit_id:
            queryset = queryset.filter(visit_id=visit_id)
        return queryset.select_related('service', 'icd')


class VisitPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = VisitPrescription.objects.all()
    serializer_class = VisitPrescriptionSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        visit_id = self.request.query_params.get('visit')
        queryset = VisitPrescription.objects.filter(
            visit__appointment__branch__organization=user.organization
        )
        if visit_id:
            queryset = queryset.filter(visit_id=visit_id)
        return queryset


class VisitResourceViewSet(viewsets.ModelViewSet):
    queryset = VisitResource.objects.all()
    serializer_class = VisitResourceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        visit_id = self.request.query_params.get('visit')
        queryset = VisitResource.objects.filter(
            visit__appointment__branch__organization=user.organization
        )
        if visit_id:
            queryset = queryset.filter(visit_id=visit_id)
        return queryset.select_related('resource')


class VisitFileViewSet(viewsets.ModelViewSet):
    """ViewSet for visit files"""
    queryset = VisitFile.objects.all()
    serializer_class = VisitFileSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        visit_id = self.request.query_params.get('visit')
        queryset = VisitFile.objects.filter(
            visit__appointment__branch__organization=user.organization
        )
        if visit_id:
            queryset = queryset.filter(visit_id=visit_id)
        return queryset.select_related('uploaded_by')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

