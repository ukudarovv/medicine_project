from rest_framework import serializers
from .models import Invoice, Payment, CashShift, TaxDeductionCertificate, PaymentProvider
from apps.patients.serializers import PatientSerializer
from apps.staff.serializers import EmployeeSerializer


class PaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'method', 'method_display', 'amount', 'provider', 
                  'ext_id', 'status', 'status_display', 'qr_code_url', 'redirect_url', 
                  'callback_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvoiceDetailSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='visit.appointment.patient.full_name', read_only=True)
    patient_iin = serializers.CharField(source='visit.appointment.patient.iin', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'visit', 'number', 'amount', 'paid_amount', 'status', 'status_display',
                  'patient_name', 'patient_iin', 'payments', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'visit', 'number', 'amount', 'paid_amount', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class CashShiftSerializer(serializers.ModelSerializer):
    opened_by_name = serializers.CharField(source='opened_by.full_name', read_only=True)
    closed_by_name = serializers.CharField(source='closed_by.full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    is_open = serializers.SerializerMethodField()
    
    class Meta:
        model = CashShift
        fields = ['id', 'branch', 'branch_name', 'opened_by', 'opened_by_name', 
                  'closed_by', 'closed_by_name', 'opened_at', 'closed_at', 
                  'opening_balance', 'closing_balance', 'is_open']
        read_only_fields = ['id', 'opened_at', 'opened_by']
    
    def get_is_open(self, obj):
        return obj.closed_at is None


class TransactionSerializer(serializers.Serializer):
    """Unified transaction serializer for billing page"""
    id = serializers.IntegerField()
    date = serializers.DateTimeField()
    type = serializers.CharField()  # 'income' or 'expense'
    category = serializers.CharField()
    description = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.CharField()
    patient = serializers.CharField(required=False)
    status = serializers.CharField()
    invoice_number = serializers.CharField(required=False)


class TaxDeductionCertificateSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_iin = serializers.CharField(source='patient.iin', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TaxDeductionCertificate
        fields = ['id', 'patient', 'patient_name', 'patient_iin', 'year', 'total_amount',
                  'services_list', 'certificate_number', 'issued_date', 'issued_by',
                  'issued_by_name', 'status', 'status_display', 'created_at']
        read_only_fields = ['id', 'certificate_number', 'created_at']


class PaymentProviderSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_type_display', read_only=True)
    
    class Meta:
        model = PaymentProvider
        fields = ['id', 'organization', 'provider_type', 'provider_display', 'merchant_id',
                  'api_key', 'api_secret', 'webhook_url', 'is_active', 'is_test_mode',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True}
        }

