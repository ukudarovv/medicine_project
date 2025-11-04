from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed all data (organization, staff, services, patients, appointments)'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🌱 Starting to seed all data...'))
        self.stdout.write('')
        
        # 1. Initial data (organization, branches, rooms)
        self.stdout.write(self.style.HTTP_INFO('📋 Step 1/5: Seeding organization and branches...'))
        call_command('seed_initial_data')
        self.stdout.write('')
        
        # 2. Services
        self.stdout.write(self.style.HTTP_INFO('🏥 Step 2/5: Seeding services...'))
        call_command('seed_services')
        self.stdout.write('')
        
        # 3. Staff
        self.stdout.write(self.style.HTTP_INFO('👨‍⚕️ Step 3/5: Seeding staff...'))
        call_command('seed_staff')
        self.stdout.write('')
        
        # 4. Patients
        self.stdout.write(self.style.HTTP_INFO('👥 Step 4/5: Seeding patients...'))
        call_command('seed_patients')
        self.stdout.write('')
        
        # 5. Appointments
        self.stdout.write(self.style.HTTP_INFO('📅 Step 5/6: Seeding appointments...'))
        call_command('seed_appointments')
        self.stdout.write('')
        
        # 6. Visits
        self.stdout.write(self.style.HTTP_INFO('🏥 Step 6/6: Seeding visits...'))
        call_command('seed_visits')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🎉 ALL DATA SEEDED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Organization: Стоматология "Здоровая Улыбка"'))
        self.stdout.write(self.style.SUCCESS('✅ Branches: 2 филиала (Абая, Сатпаева)'))
        self.stdout.write(self.style.SUCCESS('✅ Staff: 5 сотрудников (4 врача, 1 администратор)'))
        self.stdout.write(self.style.SUCCESS('✅ Services: 20 услуг в 10 категориях'))
        self.stdout.write(self.style.SUCCESS('✅ Patients: 10 пациентов'))
        self.stdout.write(self.style.SUCCESS('✅ Appointments: ~26 записей'))
        self.stdout.write(self.style.SUCCESS('✅ Visits: визиты из завершенных записей'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📝 Login credentials:'))
        self.stdout.write(self.style.WARNING('   Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('   Staff: [firstname].[lastname] / password123'))
        self.stdout.write('')

