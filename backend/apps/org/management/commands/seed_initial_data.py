from django.core.management.base import BaseCommand
from apps.org.models import Organization, Branch, Room, ClinicInfo
from apps.core.models import User


class Command(BaseCommand):
    help = 'Seed initial organization and branch data'
    
    def handle(self, *args, **kwargs):
        # Create organization
        org, created = Organization.objects.get_or_create(
            name='Стоматология "Здоровая Улыбка"',
            defaults={
                'sms_sender': 'HealthySmile'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
            
            # Create clinic info
            ClinicInfo.objects.create(
                organization=org,
                inn='1234567890',
                kpp='123456789',
                ogrn='1234567890123',
                legal_name='ООО "Здоровая Улыбка"',
                legal_address='г. Алматы, ул. Абая, 150',
                website='https://healthysmile.kz',
                support_email='info@healthysmile.kz',
                support_phone='+77017777777',
                license_number='№ 12345',
            )
        
        # Create branches
        branch1, created = Branch.objects.get_or_create(
            organization=org,
            name='Филиал на Абая',
            defaults={
                'address': 'г. Алматы, ул. Абая, 150',
                'phone': '+77017777777',
                'email': 'abay@healthysmile.kz',
                'timezone': 'Asia/Almaty'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created branch: {branch1.name}'))
            
            # Create rooms
            Room.objects.create(branch=branch1, name='Кабинет 1', color='#2196F3', order=1)
            Room.objects.create(branch=branch1, name='Кабинет 2', color='#4CAF50', order=2)
            Room.objects.create(branch=branch1, name='Кабинет 3', color='#FF9800', order=3)
        
        branch2, created = Branch.objects.get_or_create(
            organization=org,
            name='Филиал на Сатпаева',
            defaults={
                'address': 'г. Алматы, ул. Сатпаева, 90',
                'phone': '+77017777778',
                'email': 'satpayev@healthysmile.kz',
                'timezone': 'Asia/Almaty'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created branch: {branch2.name}'))
            Room.objects.create(branch=branch2, name='Кабинет 1', color='#9C27B0', order=1)
            Room.objects.create(branch=branch2, name='Кабинет 2', color='#00BCD4', order=2)
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@healthysmile.kz',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
                role='owner',
                organization=org
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        
        self.stdout.write(self.style.SUCCESS('✓ Initial data seeded successfully!'))

