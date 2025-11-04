import pytest
from datetime import datetime, timedelta
from apps.calendar.models import Appointment


@pytest.mark.django_db
class TestAppointments:
    """Test appointment endpoints"""
    
    def test_create_appointment(self, authenticated_client, branch, employee, patient):
        """Test creating appointment"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        data = {
            'branch': branch.id,
            'employee': employee.id,
            'patient': patient.id,
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat(),
            'status': 'booked'
        }
        
        response = authenticated_client.post('/api/v1/calendar/appointments', data)
        
        assert response.status_code == 201
        assert response.data['status'] == 'booked'
    
    def test_list_appointments(self, authenticated_client, branch, employee, patient):
        """Test listing appointments"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        Appointment.objects.create(
            branch=branch,
            employee=employee,
            patient=patient,
            start_datetime=start,
            end_datetime=end,
            status='booked'
        )
        
        response = authenticated_client.get('/api/v1/calendar/appointments')
        
        assert response.status_code == 200
        assert len(response.data['results']) > 0
    
    def test_appointment_conflict_detection(self, authenticated_client, branch, employee, patient):
        """Test appointment conflict detection"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        # Create first appointment
        Appointment.objects.create(
            branch=branch,
            employee=employee,
            patient=patient,
            start_datetime=start,
            end_datetime=end,
            status='booked'
        )
        
        # Try to create overlapping appointment
        data = {
            'branch': branch.id,
            'employee': employee.id,
            'patient': patient.id,
            'start_datetime': (start + timedelta(minutes=30)).isoformat(),
            'end_datetime': (end + timedelta(minutes=30)).isoformat(),
            'status': 'booked'
        }
        
        response = authenticated_client.post('/api/v1/calendar/appointments', data)
        
        assert response.status_code == 400

