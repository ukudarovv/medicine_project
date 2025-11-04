"""
Utility functions for marketing module
"""
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
import hashlib


def apply_placeholders_to_message(body, patient, visit=None, appointment=None):
    """
    Apply placeholders to message body
    
    Available placeholders:
    - _ИМЯ_ПАЦИЕНТА_ - patient first name
    - _ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_ - patient first + middle name
    - _ДАТА_ВИЗИТА_ - visit/appointment date
    - _ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_ - online booking link
    """
    placeholders = {
        '_ИМЯ_ПАЦИЕНТА_': patient.first_name,
        '_ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_': f"{patient.first_name} {patient.middle_name}".strip(),
        '_ДАТА_ВИЗИТА_': '',
        '_ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_': getattr(
            settings, 
            'ONLINE_BOOKING_URL', 
            'https://clinic.example.com/booking'
        ),
    }
    
    if visit:
        if hasattr(visit, 'date'):
            placeholders['_ДАТА_ВИЗИТА_'] = visit.date.strftime('%d.%m.%Y')
    elif appointment:
        if hasattr(appointment, 'start_datetime'):
            placeholders['_ДАТА_ВИЗИТА_'] = appointment.start_datetime.strftime('%d.%m.%Y')
    
    result = body
    for placeholder, value in placeholders.items():
        result = result.replace(placeholder, value)
    
    return result


def filter_campaign_audience(organization, filters):
    """
    Filter patients for campaign audience based on provided filters
    
    Filters:
    - tags: list of tags (OR condition)
    - services: list of service IDs
    - last_visit_from/to: date range for last visit
    - birthdate_from/to: date range for birthdays in period
    - is_opt_in: boolean (default True)
    
    Returns: QuerySet of Patient
    """
    from apps.patients.models import Patient
    from apps.visits.models import Visit
    
    patients_query = Patient.objects.filter(organization=organization, is_active=True)
    
    # Opt-in filter (default True for marketing campaigns)
    if filters.get('is_opt_in', True):
        patients_query = patients_query.filter(is_marketing_opt_in=True)
    
    # Tags filter (OR condition - patient has any of the tags)
    if filters.get('tags'):
        patients_query = patients_query.filter(tags__overlap=filters['tags'])
    
    # Services filter (patients who had any of these services)
    if filters.get('services'):
        service_ids = filters['services']
        # Note: This assumes Visit has a services M2M or similar
        # Adjust based on actual Visit model structure
        visit_patients = Visit.objects.filter(
            patient__organization=organization
        ).values_list('patient_id', flat=True).distinct()
        patients_query = patients_query.filter(id__in=visit_patients)
    
    # Last visit date range
    if filters.get('last_visit_from') or filters.get('last_visit_to'):
        visit_query = Visit.objects.filter(patient__organization=organization)
        
        if filters.get('last_visit_from'):
            if isinstance(filters['last_visit_from'], str):
                date_from = datetime.strptime(filters['last_visit_from'], '%Y-%m-%d').date()
            else:
                date_from = filters['last_visit_from']
            visit_query = visit_query.filter(date__gte=date_from)
        
        if filters.get('last_visit_to'):
            if isinstance(filters['last_visit_to'], str):
                date_to = datetime.strptime(filters['last_visit_to'], '%Y-%m-%d').date()
            else:
                date_to = filters['last_visit_to']
            visit_query = visit_query.filter(date__lte=date_to)
        
        patient_ids = visit_query.values_list('patient_id', flat=True).distinct()
        patients_query = patients_query.filter(id__in=patient_ids)
    
    # Birthday in period (for birthday campaigns)
    if filters.get('birthdate_from') or filters.get('birthdate_to'):
        if filters.get('birthdate_from'):
            if isinstance(filters['birthdate_from'], str):
                date_from = datetime.strptime(filters['birthdate_from'], '%Y-%m-%d').date()
            else:
                date_from = filters['birthdate_from']
            
            # Filter by month and day (year-agnostic)
            patients_query = patients_query.filter(
                Q(birth_date__month__gt=date_from.month) |
                Q(birth_date__month=date_from.month, birth_date__day__gte=date_from.day)
            )
        
        if filters.get('birthdate_to'):
            if isinstance(filters['birthdate_to'], str):
                date_to = datetime.strptime(filters['birthdate_to'], '%Y-%m-%d').date()
            else:
                date_to = filters['birthdate_to']
            
            patients_query = patients_query.filter(
                Q(birth_date__month__lt=date_to.month) |
                Q(birth_date__month=date_to.month, birth_date__day__lte=date_to.day)
            )
    
    return patients_query


def calculate_sms_cost(body, num_recipients, price_per_sms):
    """
    Calculate total SMS cost based on body length and number of recipients
    
    Returns: (total_cost, segments_per_message, total_segments)
    """
    from decimal import Decimal
    
    # Detect cyrillic
    is_cyrillic = any('\u0400' <= char <= '\u04FF' for char in body)
    
    # Calculate segments
    max_chars = 70 if is_cyrillic else 160
    max_chars_multi = 67 if is_cyrillic else 153
    
    if len(body) <= max_chars:
        segments_per_message = 1
    else:
        segments_per_message = (len(body) + max_chars_multi - 1) // max_chars_multi
    
    total_segments = num_recipients * segments_per_message
    total_cost = Decimal(str(total_segments)) * Decimal(str(price_per_sms))
    
    return (total_cost, segments_per_message, total_segments)


def hash_message_body(body):
    """Generate SHA256 hash of message body"""
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def validate_audience_filters(filters):
    """
    Validate audience filters structure
    
    Returns: (is_valid, error_message)
    """
    if not isinstance(filters, dict):
        return (False, 'Filters must be a dictionary')
    
    allowed_keys = [
        'tags', 'services', 'last_visit_from', 'last_visit_to',
        'birthdate_from', 'birthdate_to', 'is_opt_in'
    ]
    
    for key in filters.keys():
        if key not in allowed_keys:
            return (False, f'Invalid filter key: {key}')
    
    # Type validation
    if 'tags' in filters and not isinstance(filters['tags'], list):
        return (False, 'tags must be a list')
    
    if 'services' in filters and not isinstance(filters['services'], list):
        return (False, 'services must be a list')
    
    if 'is_opt_in' in filters and not isinstance(filters['is_opt_in'], bool):
        return (False, 'is_opt_in must be a boolean')
    
    return (True, '')

