from django.core.management.base import BaseCommand
from apps.org.models import Organization, Branch
from apps.calendar.models import Appointment
from apps.staff.models import Employee
from apps.patients.models import Patient
from apps.services.models import Service
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed appointments data'
    
    def handle(self, *args, **kwargs):
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found'))
            return
        
        branches = list(Branch.objects.all())
        if not branches:
            self.stdout.write(self.style.ERROR('No branches found'))
            return
        
        employees = list(Employee.objects.filter(show_in_schedule=True))
        if not employees:
            self.stdout.write(self.style.ERROR('No employees found'))
            return
        
        patients = list(Patient.objects.all())
        if not patients:
            self.stdout.write(self.style.ERROR('No patients found'))
            return
        
        # Create appointments for the next 7 days
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        created_count = 0
        for day in range(-2, 7):  # Include 2 days in the past
            current_date = start_date + timedelta(days=day)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Create 3-5 appointments per day
            num_appointments = random.randint(3, 5)
            
            for i in range(num_appointments):
                hour = 9 + i * 2  # Every 2 hours
                duration = random.choice([30, 60, 90])  # Duration in minutes
                start_time = current_date.replace(hour=hour)
                end_time = start_time + timedelta(minutes=duration)
                
                # Choose random employee, patient, branch
                employee = random.choice(employees)
                patient = random.choice(patients)
                branch = random.choice(branches)
                
                # Determine status based on date
                if day < 0:  # Past appointments
                    status = random.choice(['done', 'no_show', 'canceled'])
                elif day == 0:  # Today
                    status = random.choice(['confirmed', 'in_progress'])
                else:  # Future appointments
                    status = random.choice(['booked', 'confirmed'])
                
                appointment, created = Appointment.objects.get_or_create(
                    branch=branch,
                    employee=employee,
                    patient=patient,
                    start_datetime=start_time,
                    defaults={
                        'end_datetime': end_time,
                        'status': status,
                        'note': f'Плановая запись',
                        'is_primary': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created appointment: {patient.first_name} {patient.last_name} '
                            f'→ {employee.first_name} {employee.last_name} ({start_time.strftime("%Y-%m-%d %H:%M")})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Appointments seeded successfully! Created {created_count} appointments'
            )
        )

