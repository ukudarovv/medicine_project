from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from apps.core.permissions import IsBranchMember, IsCashier
from .models import Invoice, Payment, CashShift, PaymentProvider, TaxDeductionCertificate
from .serializers import InvoiceSerializer, PaymentSerializer, CashShiftSerializer
import csv
from datetime import datetime


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(visit__appointment__branch__organization=user.organization)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsCashier]
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(invoice__visit__appointment__branch__organization=user.organization)


class CashShiftViewSet(viewsets.ModelViewSet):
    queryset = CashShift.objects.all()
    serializer_class = CashShiftSerializer
    permission_classes = [IsAuthenticated, IsCashier]
    
    def get_queryset(self):
        user = self.request.user
        return CashShift.objects.filter(branch__organization=user.organization)
    
    @action(detail=False, methods=['get'])
    def export_1c(self, request):
        """
        Export payments to 1C format (CSV) - Sprint 4
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get payments for period
        payments = Payment.objects.filter(
            invoice__visit__appointment__branch__organization=request.user.organization,
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='completed'
        ).select_related(
            'invoice__visit__appointment__patient',
            'invoice__visit__appointment__employee'
        )
        
        # Create CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="1c_export_{start_date}_{end_date}.csv"'
        
        # Add BOM for UTF-8 Excel compatibility
        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Дата',
            'Номер счета',
            'Пациент',
            'Услуга/Описание',
            'Сумма (KZT)',
            'Способ оплаты',
            'Врач',
            'Статус'
        ])
        
        for payment in payments:
            visit = payment.invoice.visit
            patient = visit.appointment.patient
            employee = visit.appointment.employee
            
            # Get services from visit
            services = ', '.join([s.service.name for s in visit.services.all()[:3]])
            if visit.services.count() > 3:
                services += '...'
            
            writer.writerow([
                payment.created_at.strftime('%d.%m.%Y %H:%M'),
                payment.invoice.number,
                patient.full_name,
                services or 'Без услуг',
                float(payment.amount),
                payment.get_method_display(),
                employee.full_name,
                payment.get_status_display()
            ])
        
        return response


# ==================== Sprint 4: Payment Providers & Tax Certificates ====================


class TaxDeductionCertificateViewSet(viewsets.ModelViewSet):
    """
    Tax deduction certificates management (Sprint 4)
    """
    queryset = TaxDeductionCertificate.objects.all()
    serializer_class = None  # Will create serializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.request.query_params.get('patient')
        queryset = TaxDeductionCertificate.objects.filter(
            patient__organization=user.organization
        )
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.select_related('patient', 'issued_by')
    
    def perform_create(self, serializer):
        certificate = serializer.save(issued_by=self.request.user)
        # Generate certificate number if not set
        if not certificate.certificate_number:
            certificate.generate_number()
            certificate.save(update_fields=['certificate_number'])

