from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from apps.core.permissions import IsBranchMember
from openpyxl import Workbook
from datetime import datetime


class AppointmentsReportView(views.APIView):
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get(self, request):
        from apps.calendar.models import Appointment
        user = request.user
        
        appointments = Appointment.objects.filter(
            branch__organization=user.organization
        ).select_related('employee', 'patient').values(
            'id', 'start_datetime', 'employee__first_name', 'employee__last_name',
            'patient__first_name', 'patient__last_name', 'status'
        )
        
        return Response({'appointments': list(appointments)})


class RevenueReportView(views.APIView):
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get(self, request):
        from apps.billing.models import Invoice
        user = request.user
        
        invoices = Invoice.objects.filter(
            visit__appointment__branch__organization=user.organization,
            status='paid'
        ).values('created_at__date', 'amount')
        
        return Response({'revenue': list(invoices)})


class SMSBalanceReportView(views.APIView):
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get(self, request):
        from apps.comms.models import MessageLog
        user = request.user
        
        messages = MessageLog.objects.filter(
            patient__organizations=user.organization
        ).values('created_at__date', 'cost', 'status')
        
        return Response({'sms_usage': list(messages)})


class ExportExcelView(views.APIView):
    permission_classes = [IsAuthenticated, IsBranchMember]
    
    def get(self, request):
        """Export data to Excel"""
        export_type = request.query_params.get('type', 'appointments')
        
        wb = Workbook()
        ws = wb.active
        ws.title = export_type.capitalize()
        
        if export_type == 'appointments':
            from apps.calendar.models import Appointment
            appointments = Appointment.objects.filter(
                branch__organization=request.user.organization
            ).select_related('employee', 'patient')[:100]
            
            ws.append(['ID', 'Date', 'Doctor', 'Patient', 'Status'])
            for apt in appointments:
                ws.append([
                    apt.id,
                    apt.start_datetime.strftime('%Y-%m-%d %H:%M'),
                    apt.employee.full_name,
                    apt.patient.full_name,
                    apt.status
                ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{export_type}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        wb.save(response)
        return response

