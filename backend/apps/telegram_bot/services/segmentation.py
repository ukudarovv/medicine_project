"""
Patient segmentation for broadcasts
"""
from datetime import datetime, date
from django.db.models import Q, Count
from apps.patients.models import Patient
from apps.visits.models import Visit


class PatientSegmentation:
    """
    Filter patients based on segmentation criteria
    """
    
    @staticmethod
    def filter_patients(organization, filters):
        """
        Apply filters to get patient queryset
        
        Args:
            organization: Organization instance
            filters: dict with filter criteria
                - age_min, age_max: int
                - sex: 'M' or 'F'
                - services: list of service IDs
                - tags: list of tags
                - osms_status: 'insured' or 'not_insured'
                - last_visit_from, last_visit_to: date
                - min_visits: int (minimum number of visits)
        
        Returns:
            QuerySet of Patient
        """
        patients = Patient.objects.filter(organization=organization)
        
        # Only patients with telegram link
        patients = patients.filter(telegram_link__is_active=True)
        
        # Only patients who consented to marketing
        patients = patients.filter(
            Q(is_marketing_opt_in=True) |
            Q(telegram_link__consents_json__marketing=True)
        )
        
        # Age filter
        if 'age_min' in filters or 'age_max' in filters:
            today = date.today()
            
            if 'age_min' in filters:
                age_min = filters['age_min']
                max_birth_date = date(today.year - age_min, today.month, today.day)
                patients = patients.filter(birth_date__lte=max_birth_date)
            
            if 'age_max' in filters:
                age_max = filters['age_max']
                min_birth_date = date(today.year - age_max - 1, today.month, today.day)
                patients = patients.filter(birth_date__gte=min_birth_date)
        
        # Sex filter
        if 'sex' in filters and filters['sex']:
            patients = patients.filter(sex=filters['sex'])
        
        # Tags filter
        if 'tags' in filters and filters['tags']:
            for tag in filters['tags']:
                patients = patients.filter(tags__contains=[tag])
        
        # OSMS status filter
        if 'osms_status' in filters and filters['osms_status']:
            patients = patients.filter(osms_status=filters['osms_status'])
        
        # Service filter (patients who used specific services)
        if 'services' in filters and filters['services']:
            patients = patients.filter(
                visits__service_id__in=filters['services']
            ).distinct()
        
        # Last visit date filter
        if 'last_visit_from' in filters or 'last_visit_to' in filters:
            visit_filter = Q()
            
            if 'last_visit_from' in filters:
                visit_filter &= Q(visits__visit_date__gte=filters['last_visit_from'])
            
            if 'last_visit_to' in filters:
                visit_filter &= Q(visits__visit_date__lte=filters['last_visit_to'])
            
            patients = patients.filter(visit_filter).distinct()
        
        # Minimum visits filter
        if 'min_visits' in filters and filters['min_visits']:
            patients = patients.annotate(
                visit_count=Count('visits')
            ).filter(visit_count__gte=filters['min_visits'])
        
        return patients.distinct()
    
    @staticmethod
    def count_recipients(organization, filters):
        """
        Count how many patients match the filters
        """
        return PatientSegmentation.filter_patients(organization, filters).count()

