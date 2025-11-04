from django.core.management.base import BaseCommand
from apps.calendar.models import Appointment
from apps.visits.models import Visit, VisitService
from apps.services.models import Service
from datetime import datetime
import random


class Command(BaseCommand):
    help = 'Seed visits from completed/done appointments'
    
    def handle(self, *args, **kwargs):
        # Get appointments that should have visits
        completed_appointments = Appointment.objects.filter(
            status__in=['done', 'in_progress']
        ).exclude(
            visit__isnull=False  # Don't create duplicate visits
        )
        
        if not completed_appointments.exists():
            self.stdout.write(self.style.WARNING('No completed appointments found'))
            return
        
        services = list(Service.objects.all())
        if not services:
            self.stdout.write(self.style.ERROR('No services found'))
            return
        
        created_count = 0
        for appointment in completed_appointments:
            # Determine visit status based on appointment status
            if appointment.status == 'done':
                visit_status = 'completed'
            elif appointment.status == 'in_progress':
                visit_status = 'in_progress'
            else:
                visit_status = 'draft'
            
            # Create visit
            visit = Visit.objects.create(
                appointment=appointment,
                status=visit_status,
                is_patient_arrived=True,
                arrived_at=appointment.start_datetime,
                comment=f'Визит создан автоматически из записи #{appointment.id}',
                diagnosis='',
                treatment_plan=''
            )
            
            # Add 1-3 random services to completed visits
            if visit_status == 'completed':
                num_services = random.randint(1, 3)
                selected_services = random.sample(services, min(num_services, len(services)))
                
                for service in selected_services:
                    VisitService.objects.create(
                        visit=visit,
                        service=service,
                        qty=1,
                        duration=random.choice([15, 30, 45, 60]),
                        price=service.base_price,
                        discount_percent=random.choice([0, 5, 10]),
                        discount_amount=0,
                        tooth_number=random.choice(['', '11', '21', '36', '46']) if random.random() > 0.5 else ''
                    )
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created visit for appointment #{appointment.id}: '
                    f'{appointment.patient.first_name} {appointment.patient.last_name} '
                    f'({visit.status})'
                )
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Visits seeded successfully! Created {created_count} visits'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total visits in database: {Visit.objects.count()}'
            )
        )

