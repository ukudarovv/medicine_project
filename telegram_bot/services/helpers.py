"""
Helper functions
"""
from datetime import datetime, date
from typing import Optional


def format_date(date_obj: date, language: str = 'ru') -> str:
    """Format date for display"""
    months_ru = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    
    months_kk = {
        1: 'қаңтар', 2: 'ақпан', 3: 'наурыз', 4: 'сәуір',
        5: 'мамыр', 6: 'маусым', 7: 'шілде', 8: 'тамыз',
        9: 'қыркүйек', 10: 'қазан', 11: 'қараша', 12: 'желтоқсан'
    }
    
    months = months_kk if language == 'kk' else months_ru
    
    return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"


def parse_date(date_str: str) -> Optional[date]:
    """Parse date from string"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def validate_phone(phone: str) -> str:
    """Validate and format phone number"""
    # Remove all non-digit characters
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Kazakhstan phone number should be 11 digits (7XXXXXXXXXX)
    if len(digits) == 10:
        digits = '7' + digits
    
    if len(digits) != 11 or not digits.startswith('7'):
        raise ValueError('Invalid phone number')
    
    return f"+{digits}"


def format_price(amount: float, currency: str = 'KZT') -> str:
    """Format price for display"""
    if currency == 'KZT':
        return f"{amount:,.0f} ₸"
    return f"{amount:,.2f} {currency}"


def generate_ics_file(appointment: dict) -> str:
    """Generate ICS calendar file content"""
    from datetime import datetime, timedelta
    
    # Parse date and time
    apt_date = datetime.strptime(appointment['date'], '%Y-%m-%d').date()
    apt_time = datetime.strptime(appointment['time_from'], '%H:%M:%S').time()
    start_dt = datetime.combine(apt_date, apt_time)
    
    # Duration (default 30 minutes)
    duration = timedelta(minutes=30)
    end_dt = start_dt + duration
    
    # Format for ICS
    start_str = start_dt.strftime('%Y%m%dT%H%M%S')
    end_str = end_dt.strftime('%Y%m%dT%H%M%S')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Medicine ERP//Telegram Bot//EN
BEGIN:VEVENT
UID:{appointment['id']}@medicine-erp
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:Прием у врача {appointment.get('doctor_name', '')}
DESCRIPTION:Услуга: {appointment.get('service_name', '')}
LOCATION:{appointment.get('branch_address', '')}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    return ics_content

