from django.core.management.base import BaseCommand
from apps.org.models import Organization, Branch
from apps.staff.models import Employee, EmployeeBranch, Position
from apps.core.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Seed staff data'
    
    def handle(self, *args, **kwargs):
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found'))
            return
        
        branches = list(Branch.objects.all())
        if not branches:
            self.stdout.write(self.style.ERROR('No branch found'))
            return
        
        # Create positions
        position_doctor, _ = Position.objects.get_or_create(
            organization=org,
            name='Врач-стоматолог'
        )
        position_surgeon, _ = Position.objects.get_or_create(
            organization=org,
            name='Врач-хирург'
        )
        position_orthodontist, _ = Position.objects.get_or_create(
            organization=org,
            name='Врач-ортодонт'
        )
        position_registrar, _ = Position.objects.get_or_create(
            organization=org,
            name='Администратор'
        )
        
        employees_data = [
            {
                'first_name': 'Айгерім',
                'last_name': 'Сейітова',
                'position': position_doctor,
                'color': '#2196F3',
                'phone': '+77011234567',
                'specialization': 'Терапевт',
                'role': 'doctor'
            },
            {
                'first_name': 'Данияр',
                'last_name': 'Қасымов',
                'position': position_surgeon,
                'color': '#F44336',
                'phone': '+77011234568',
                'specialization': 'Хирург',
                'role': 'doctor'
            },
            {
                'first_name': 'Гүлнар',
                'last_name': 'Әміршаева',
                'position': position_orthodontist,
                'color': '#4CAF50',
                'phone': '+77011234569',
                'specialization': 'Ортодонт',
                'role': 'doctor'
            },
            {
                'first_name': 'Ерлан',
                'last_name': 'Нұрланов',
                'position': position_doctor,
                'color': '#9C27B0',
                'phone': '+77011234570',
                'specialization': 'Терапевт',
                'role': 'doctor'
            },
            {
                'first_name': 'Асель',
                'last_name': 'Бекова',
                'position': position_registrar,
                'color': '#FF9800',
                'phone': '+77011234571',
                'specialization': '',
                'role': 'registrar'
            },
        ]
        
        for i, data in enumerate(employees_data):
            # Create user
            username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@healthysmile.kz",
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'organization': org,
                }
            )
            if user_created:
                user.set_password('password123')
                user.save()
            
            emp, created = Employee.objects.get_or_create(
                organization=org,
                first_name=data['first_name'],
                last_name=data['last_name'],
                defaults={
                    'user': user,
                    'position': data['position'],
                    'phone': data['phone'],
                    'hired_at': date(2023, 1, 1),
                    'color': data['color'],
                    'commission_percent': 30,
                    'specialization': data['specialization'],
                    'show_in_schedule': data['role'] == 'doctor',
                    'employment_status': 'active',
                }
            )
            
            if created:
                # Assign to branch
                branch = branches[i % len(branches)]
                EmployeeBranch.objects.create(
                    employee=emp,
                    branch=branch,
                    is_default=True
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created employee: {emp.first_name} {emp.last_name} ({data["position"].name})'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Staff seeded successfully! Created {Employee.objects.count()} employees'))

