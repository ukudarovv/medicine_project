"""
KATO (Kazakhstan Administrative Territorial Objects) utilities
"""
import json
import os
from pathlib import Path


class KATOHelper:
    """Helper class for working with KATO addresses"""
    
    _kato_data = None
    
    @classmethod
    def load_kato_data(cls):
        """Load KATO data from fixture file"""
        if cls._kato_data is None:
            fixture_path = Path(__file__).parent / 'fixtures' / 'kato.json'
            if fixture_path.exists():
                with open(fixture_path, 'r', encoding='utf-8') as f:
                    cls._kato_data = json.load(f)
            else:
                cls._kato_data = []
        return cls._kato_data
    
    @classmethod
    def get_regions(cls):
        """Get all regions (level 1)"""
        data = cls.load_kato_data()
        return [item for item in data if item.get('level') == 1]
    
    @classmethod
    def get_districts(cls, parent_code):
        """Get districts for a specific region/city"""
        data = cls.load_kato_data()
        return [item for item in data if item.get('parent') == parent_code]
    
    @classmethod
    def get_by_code(cls, code):
        """Get KATO item by code"""
        data = cls.load_kato_data()
        for item in data:
            if item.get('code') == code:
                return item
        return None
    
    @classmethod
    def format_address(cls, kato_address):
        """
        Format KATO address dict into readable string
        
        Args:
            kato_address: dict with keys region, district, city, street, building, apartment
        
        Returns:
            Formatted address string
        """
        if not kato_address:
            return ''
        
        parts = []
        
        if kato_address.get('region'):
            parts.append(kato_address['region'])
        
        if kato_address.get('district'):
            parts.append(kato_address['district'])
        
        if kato_address.get('city'):
            parts.append(kato_address['city'])
        
        if kato_address.get('street'):
            parts.append(kato_address['street'])
        
        if kato_address.get('building'):
            building_str = f"д. {kato_address['building']}"
            if kato_address.get('apartment'):
                building_str += f", кв. {kato_address['apartment']}"
            parts.append(building_str)
        
        return ', '.join(parts)

