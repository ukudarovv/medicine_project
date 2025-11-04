from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsBranchMember, IsCashier
from .models import Invoice, Payment, CashShift
from .serializers import InvoiceSerializer, PaymentSerializer, CashShiftSerializer


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

