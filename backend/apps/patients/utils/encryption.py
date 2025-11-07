"""
IIN encryption utilities for multi-org patient consent system

Uses AES-256 encryption via Fernet for secure IIN storage
and SHA-256 hashing for fast lookups without decryption.
"""
import hashlib
import base64
from typing import Optional
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken


def get_encryption_key() -> bytes:
    """
    Get encryption key from settings
    If not set, generate a new one (development only)
    """
    key = getattr(settings, 'IIN_ENCRYPTION_KEY', None)
    
    if not key:
        # Development only - generate temporary key
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            'IIN_ENCRYPTION_KEY not set in settings. '
            'Generating temporary key (development only).'
        )
        # Generate a new key and print it
        key = Fernet.generate_key().decode('utf-8')
        logger.warning(f'Generated key (add to .env): IIN_ENCRYPTION_KEY={key}')
    
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    return key


def get_hash_salt() -> str:
    """
    Get salt for hashing from settings
    """
    salt = getattr(settings, 'IIN_HASH_SALT', 'default_salt_change_in_production')
    return salt


def encrypt_iin(iin: str) -> Optional[str]:
    """
    Encrypt IIN using AES-256 (Fernet)
    
    Args:
        iin: Plain IIN string (12 digits)
        
    Returns:
        Base64-encoded encrypted IIN or None if input is empty
    """
    if not iin:
        return None
    
    # Remove any whitespace or dashes
    iin = iin.replace(' ', '').replace('-', '')
    
    try:
        fernet = Fernet(get_encryption_key())
        encrypted = fernet.encrypt(iin.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to encrypt IIN: {e}')
        raise


def decrypt_iin(iin_enc: str) -> Optional[str]:
    """
    Decrypt IIN from encrypted string
    
    Args:
        iin_enc: Encrypted IIN string
        
    Returns:
        Plain IIN string or None if input is empty
    """
    if not iin_enc:
        return None
    
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(iin_enc.encode('utf-8'))
        return decrypted.decode('utf-8')
    except InvalidToken:
        import logging
        logger = logging.getLogger(__name__)
        logger.error('Invalid encryption token - IIN may be corrupted or key changed')
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to decrypt IIN: {e}')
        return None


def hash_iin(iin: str) -> Optional[str]:
    """
    Create SHA-256 hash of IIN for indexing and lookups
    Uses salt from settings for additional security
    
    Args:
        iin: Plain IIN string (12 digits)
        
    Returns:
        Hex-encoded hash or None if input is empty
    """
    if not iin:
        return None
    
    # Remove any whitespace or dashes
    iin = iin.replace(' ', '').replace('-', '')
    
    # Combine with salt
    salt = get_hash_salt()
    salted = f"{salt}{iin}{salt}"
    
    # Hash with SHA-256
    hash_obj = hashlib.sha256(salted.encode('utf-8'))
    return hash_obj.hexdigest()


def mask_iin(iin: str, show_last: int = 4) -> str:
    """
    Mask IIN for display, showing only last N digits
    
    Args:
        iin: Plain IIN string
        show_last: Number of digits to show at the end (default: 4)
        
    Returns:
        Masked IIN like "********1234"
    """
    if not iin:
        return ''
    
    # Remove any whitespace or dashes
    iin = iin.replace(' ', '').replace('-', '')
    
    if len(iin) <= show_last:
        return iin
    
    masked_part = '*' * (len(iin) - show_last)
    visible_part = iin[-show_last:]
    
    return f"{masked_part}{visible_part}"


def verify_iin_hash(iin: str, iin_hash: str) -> bool:
    """
    Verify if IIN matches the provided hash
    
    Args:
        iin: Plain IIN string
        iin_hash: Hash to verify against
        
    Returns:
        True if IIN matches hash, False otherwise
    """
    if not iin or not iin_hash:
        return False
    
    computed_hash = hash_iin(iin)
    return computed_hash == iin_hash

