from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, CanAccessVisit
from .models import Visit, VisitService, VisitPrescription, VisitResource
from .serializers import (
    VisitSerializer,
    VisitServiceSerializer,
    VisitPrescriptionSerializer,
    VisitResourceSerializer
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
        from django.utils import timezone
        visit = self.get_object()
        visit.is_patient_arrived = True
        visit.arrived_at = timezone.now()
        visit.save()
        return Response(VisitSerializer(visit).data)


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

