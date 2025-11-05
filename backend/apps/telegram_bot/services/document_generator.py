"""
Document generation service for bot
"""
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from apps.telegram_bot.models import BotDocument


class DocumentGenerator:
    """
    Generate PDF documents for patients via bot
    """
    
    @staticmethod
    def generate_direction(patient, visit, language='ru'):
        """
        Generate direction (направление) PDF
        
        Args:
            patient: Patient instance
            visit: Visit instance
            language: 'ru' or 'kk'
        
        Returns:
            BotDocument instance
        """
        template_name = 'reports/direction.html'  # Use existing template
        
        context = {
            'patient': patient,
            'visit': visit,
            'date': datetime.now(),
            'language': language
        }
        
        html_string = render_to_string(template_name, context)
        
        # Generate PDF
        filename = f"direction_{patient.id}_{visit.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        file_path = os.path.join('bot_documents', str(patient.id), filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Generate PDF
        HTML(string=html_string).write_pdf(full_path)
        
        # Create BotDocument record
        expires_at = datetime.now() + timedelta(hours=48)  # 48 hour TTL
        
        doc = BotDocument.objects.create(
            patient=patient,
            document_type='direction',
            file_path=file_path,
            title=f"Направление от {datetime.now().strftime('%d.%m.%Y')}",
            language=language,
            expires_at=expires_at,
            related_visit=visit
        )
        
        return doc
    
    @staticmethod
    def generate_tax_certificate(patient, year, language='ru'):
        """
        Generate tax deduction certificate
        """
        from apps.billing.models import Payment
        
        # Get payments for the year
        payments = Payment.objects.filter(
            patient=patient,
            created_at__year=year,
            status='paid'
        )
        
        total_amount = sum(p.amount for p in payments)
        
        template_name = 'reports/tax_certificate.html'
        
        context = {
            'patient': patient,
            'year': year,
            'payments': payments,
            'total_amount': total_amount,
            'date': datetime.now(),
            'language': language
        }
        
        html_string = render_to_string(template_name, context)
        
        # Generate PDF
        filename = f"tax_cert_{patient.id}_{year}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        file_path = os.path.join('bot_documents', str(patient.id), filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        HTML(string=html_string).write_pdf(full_path)
        
        expires_at = datetime.now() + timedelta(hours=48)
        
        doc = BotDocument.objects.create(
            patient=patient,
            document_type='tax',
            file_path=file_path,
            title=f"Справка для налогового вычета за {year} год",
            language=language,
            expires_at=expires_at
        )
        
        return doc
    
    @staticmethod
    def cleanup_expired_documents():
        """
        Mark expired documents (Celery task)
        """
        now = datetime.now()
        expired_docs = BotDocument.objects.filter(
            expires_at__lt=now,
            is_expired=False
        )
        
        count = expired_docs.update(is_expired=True)
        return count

