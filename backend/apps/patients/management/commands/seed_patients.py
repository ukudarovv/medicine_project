from django.core.management.base import BaseCommand
from apps.org.models import Organization
from apps.patients.models import Patient
from datetime import date
import random


class Command(BaseCommand):
    help = 'Seed patient data'
    
    def handle(self, *args, **kwargs):
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found'))
            return
        
        patients_data = [
            {'first_name': 'Асель', 'last_name': 'Нұрланова', 'sex': 'F', 'birth_year': 1990},
            {'first_name': 'Бекзат', 'last_name': 'Төлеуов', 'sex': 'M', 'birth_year': 1985},
            {'first_name': 'Гүлім', 'last_name': 'Сағымбаева', 'sex': 'F', 'birth_year': 1995},
            {'first_name': 'Дәулет', 'last_name': 'Мұхтаров', 'sex': 'M', 'birth_year': 1988},
            {'first_name': 'Ерлан', 'last_name': 'Қожахметов', 'sex': 'M', 'birth_year': 1992},
            {'first_name': 'Жанна', 'last_name': 'Әмірова', 'sex': 'F', 'birth_year': 1987},
            {'first_name': 'Зарина', 'last_name': 'Бекмұратова', 'sex': 'F', 'birth_year': 1993},
            {'first_name': 'Ильяс', 'last_name': 'Сейдуллаев', 'sex': 'M', 'birth_year': 1991},
            {'first_name': 'Камила', 'last_name': 'Түсіпова', 'sex': 'F', 'birth_year': 1989},
            {'first_name': 'Марат', 'last_name': 'Қайратов', 'sex': 'M', 'birth_year': 1994},
        ]
        
        created_count = 0
        for idx, data in enumerate(patients_data, 1):
            patient, created = Patient.objects.get_or_create(
                organization=org,
                phone=f'+77011{idx:06d}',
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'birth_date': date(data['birth_year'], random.randint(1, 12), random.randint(1, 28)),
                    'sex': data['sex'],
                    'email': f'{data["first_name"].lower()}@example.com',
                    'tags': ['новый_пациент'],
                    'is_marketing_opt_in': random.choice([True, False]),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created patient: {patient.first_name} {patient.last_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Patients seeded successfully! Created {created_count} new patients, total: {Patient.objects.count()}'))

