from rest_framework import serializers
from .models import Invoice, Payment, CashShift


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'method', 'amount', 'provider', 'ext_id', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'visit', 'number', 'amount', 'paid_amount', 'status', 'payments', 'created_at']
        read_only_fields = ['id', 'created_at']


class CashShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashShift
        fields = ['id', 'branch', 'opened_by', 'closed_by', 'opened_at', 'closed_at', 'opening_balance', 'closing_balance']
        read_only_fields = ['id', 'opened_at']

