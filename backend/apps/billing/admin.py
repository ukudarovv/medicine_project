from django.contrib import admin
from .models import Invoice, Payment, CashShift


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'visit', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    raw_id_fields = ['visit']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'method', 'amount', 'status', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    raw_id_fields = ['invoice']


@admin.register(CashShift)
class CashShiftAdmin(admin.ModelAdmin):
    list_display = ['branch', 'opened_by', 'opened_at', 'closed_at']
    list_filter = ['branch', 'opened_at']
    raw_id_fields = ['branch', 'opened_by', 'closed_by']

