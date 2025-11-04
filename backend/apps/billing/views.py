from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from apps.core.permissions import IsBranchMember, IsCashier
from .models import Invoice, Payment, CashShift, PaymentProvider, TaxDeductionCertificate
from .serializers import (
    InvoiceSerializer, InvoiceDetailSerializer, PaymentSerializer, 
    CashShiftSerializer, TransactionSerializer, TaxDeductionCertificateSerializer,
    PaymentProviderSerializer
)
import csv
from datetime import datetime, timedelta
from decimal import Decimal


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(visit__appointment__branch__organization=user.organization)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('visit__appointment__patient')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get billing statistics for dashboard"""
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Default to current month
        if not start_date or not end_date:
            now = timezone.now()
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        # Get payments (income)
        payments = Payment.objects.filter(
            invoice__visit__appointment__branch__organization=user.organization,
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='completed'
        )
        
        total_income = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # For expenses, we'd need an expense model - for now return 0
        total_expense = Decimal('0')
        
        # Get cash balance (sum of all completed cash payments)
        cash_balance = Payment.objects.filter(
            invoice__visit__appointment__branch__organization=user.organization,
            method='cash',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Payment method breakdown
        payment_methods = payments.values('method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'total_profit': total_income - total_expense,
            'cash_balance': cash_balance,
            'payment_methods': payment_methods,
            'period': {
                'start': start_date,
                'end': end_date
            }
        })
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get all transactions (payments) in unified format"""
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Get payments as income transactions
        payments = Payment.objects.filter(
            invoice__visit__appointment__branch__organization=user.organization
        ).select_related(
            'invoice__visit__appointment__patient',
            'invoice'
        )
        
        if start_date:
            payments = payments.filter(created_at__gte=start_date)
        if end_date:
            payments = payments.filter(created_at__lte=end_date)
        
        transactions = []
        for payment in payments:
            patient = payment.invoice.visit.appointment.patient
            transactions.append({
                'id': payment.id,
                'date': payment.created_at,
                'type': 'income',
                'category': 'Оплата услуг',
                'description': f'Счёт #{payment.invoice.number}',
                'amount': payment.amount,
                'method': payment.get_method_display(),
                'patient': patient.full_name,
                'status': payment.get_status_display(),
                'invoice_number': payment.invoice.number
            })
        
        # Sort by date descending
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


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
        queryset = CashShift.objects.filter(branch__organization=user.organization)
        
        # Filter for active (open) shifts
        if self.request.query_params.get('active') == 'true':
            queryset = queryset.filter(closed_at__isnull=True)
        
        return queryset.select_related('branch', 'opened_by', 'closed_by')
    
    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a cash shift"""
        shift = self.get_object()
        
        if shift.closed_at:
            return Response(
                {'error': 'Смена уже закрыта'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        closing_balance = request.data.get('closing_balance')
        if closing_balance is None:
            return Response(
                {'error': 'closing_balance is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shift.closed_at = timezone.now()
        shift.closed_by = request.user
        shift.closing_balance = closing_balance
        shift.save()
        
        serializer = self.get_serializer(shift)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current open shift for user's branch"""
        user = request.user
        branch_id = request.query_params.get('branch')
        
        if not branch_id:
            return Response(
                {'error': 'branch parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shift = CashShift.objects.filter(
            branch_id=branch_id,
            branch__organization=user.organization,
            closed_at__isnull=True
        ).first()
        
        if shift:
            serializer = self.get_serializer(shift)
            return Response(serializer.data)
        else:
            return Response({'shift': None})
    
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
    serializer_class = TaxDeductionCertificateSerializer
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


class PaymentProviderViewSet(viewsets.ModelViewSet):
    """
    Payment provider configuration management (Sprint 4)
    """
    queryset = PaymentProvider.objects.all()
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get_queryset(self):
        user = self.request.user
        return PaymentProvider.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

