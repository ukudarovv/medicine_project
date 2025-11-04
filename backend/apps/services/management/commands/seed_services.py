from django.core.management.base import BaseCommand
from apps.org.models import Organization
from apps.services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Seed services and categories'
    
    def handle(self, *args, **kwargs):
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found. Run seed_initial_data first.'))
            return
        
        # Categories
        categories = {
            'Терапия': ['Лечение кариеса', 'Лечение пульпита', 'Лечение периодонтита', 'Реставрация зуба'],
            'Хирургия': ['Удаление зуба', 'Удаление зуба мудрости', 'Имплантация', 'Костная пластика'],
            'Ортопедия': ['Коронка металлокерамическая', 'Коронка циркониевая', 'Винир', 'Протез съемный'],
            'Ортодонтия': ['Брекет-система', 'Элайнеры', 'Ретейнер', 'Пластинка'],
            'Гигиена': ['Проф. чистка', 'Отбеливание ZOOM', 'Air Flow', 'Фторирование'],
            'Диагностика': ['Консультация', 'Рентген', 'КТ', 'Панорамный снимок'],
        }
        
        for cat_name, services in categories.items():
            category, created = ServiceCategory.objects.get_or_create(
                organization=org,
                name=cat_name,
                defaults={'code': cat_name[:3].upper()}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {cat_name}'))
            
            # Create services
            for idx, svc_name in enumerate(services, 1):
                Service.objects.get_or_create(
                    organization=org,
                    code=f'{category.code}{idx:02d}',
                    defaults={
                        'name': svc_name,
                        'category': category,
                        'base_price': 10000 + (idx * 1000),
                        'unit': 'service',
                        'default_duration': 30,
                        'vat_rate': 12,
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Services seeded successfully!'))

