"""
IIN (Individual Identification Number) validation for Kazakhstan
"""
from datetime import date
import re


def validate_iin(iin: str) -> dict:
    """
    Validate Kazakhstan IIN (12 digits)
    
    IIN format: YYMMDD XXXX C Y
    - YYMMDD: birth date (year, month, day)
    - XXXX: sequential number
    - C: century indicator (1-6)
    - Y: checksum digit
    
    Returns:
        dict with keys:
        - valid (bool): whether IIN is valid
        - birth_date (date): extracted birth date if valid
        - sex (str): 'M' for male, 'F' for female
        - error (str): error message if invalid
    """
    result = {
        'valid': False,
        'birth_date': None,
        'sex': None,
        'error': None
    }
    
    # Clean IIN (remove spaces and dashes)
    iin_clean = re.sub(r'[\s\-]', '', str(iin))
    
    # Check format: exactly 12 digits
    if not re.match(r'^\d{12}$', iin_clean):
        result['error'] = 'ИИН должен содержать ровно 12 цифр'
        return result
    
    # Extract birth date from first 6 digits (YYMMDD)
    year_short = int(iin_clean[0:2])
    month = int(iin_clean[2:4])
    day = int(iin_clean[4:6])
    century_indicator = int(iin_clean[6])
    
    # Determine century based on 7th digit
    # 1,2 - 19th century (1800-1899)
    # 3,4 - 20th century (1900-1999)
    # 5,6 - 21st century (2000-2099)
    if century_indicator in [1, 2]:
        year = 1800 + year_short
    elif century_indicator in [3, 4]:
        year = 1900 + year_short
    elif century_indicator in [5, 6]:
        year = 2000 + year_short
    else:
        result['error'] = f'Неверный индикатор века: {century_indicator}'
        return result
    
    # Extract sex (7th digit: odd=male, even=female)
    result['sex'] = 'M' if century_indicator % 2 == 1 else 'F'
    
    # Validate date
    try:
        birth_date = date(year, month, day)
        result['birth_date'] = birth_date
    except ValueError:
        result['error'] = f'Неверная дата рождения: {year:04d}-{month:02d}-{day:02d}'
        return result
    
    # Check if birth date is not in the future
    if birth_date > date.today():
        result['error'] = 'Дата рождения не может быть в будущем'
        return result
    
    # Validate checksum using modified Luhn algorithm for IIN
    checksum = calculate_iin_checksum(iin_clean)
    expected_checksum = int(iin_clean[11])
    
    if checksum != expected_checksum:
        result['error'] = f'Неверная контрольная сумма (ожидается {checksum}, получено {expected_checksum})'
        return result
    
    result['valid'] = True
    return result


def calculate_iin_checksum(iin: str) -> int:
    """
    Calculate IIN checksum using Kazakhstan algorithm
    
    Uses two sets of weight coefficients:
    - First pass: [1,2,3,4,5,6,7,8,9,10,11]
    - Second pass (if needed): [3,4,5,6,7,8,9,10,11,1,2]
    """
    weights1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    weights2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]
    
    # First pass
    sum1 = sum(int(iin[i]) * weights1[i] for i in range(11))
    checksum = sum1 % 11
    
    # If remainder is 10, use second pass
    if checksum == 10:
        sum2 = sum(int(iin[i]) * weights2[i] for i in range(11))
        checksum = sum2 % 11
        
        # If still 10, it's invalid
        if checksum == 10:
            return -1  # Invalid
    
    return checksum

