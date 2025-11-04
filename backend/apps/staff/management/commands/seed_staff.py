from django.core.management.base import BaseCommand
from apps.org.models import Organization, Branch
from apps.staff.models import Employee, EmployeeBranch
from datetime import date


class Command(BaseCommand):
    help = 'Seed staff data'
    
    def handle(self, *args, **kwargs):
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found'))
            return
        
        branch = Branch.objects.first()
        if not branch:
            self.stdout.write(self.style.ERROR('No branch found'))
            return
        
        employees_data = [
            {'first_name': 'Айгерім', 'last_name': 'Сейітова', 'position': 'Врач-стоматолог', 'color': '#2196F3'},
            {'first_name': 'Данияр', 'last_name': 'Қасымов', 'position': 'Врач-хирург', 'color': '#F44336'},
            {'first_name': 'Гүлнар', 'last_name': 'Әміршаева', 'position': 'Врач-ортодонт', 'color': '#4CAF50'},
        ]
        
        for data in employees_data:
            emp, created = Employee.objects.get_or_create(
                organization=org,
                first_name=data['first_name'],
                last_name=data['last_name'],
                defaults={
                    'position': data['position'],
                    'phone': '+7701' + str(hash(data['first_name']))[-7:],
                    'hire_date': date(2023, 1, 1),
                    'color': data['color'],
                    'commission_percent': 30,
                }
            )
            
            if created:
                EmployeeBranch.objects.create(employee=emp, branch=branch, is_default=True)
                self.stdout.write(self.style.SUCCESS(f'Created employee: {emp.full_name}'))
        
        self.stdout.write(self.style.SUCCESS('✓ Staff seeded successfully!'))

