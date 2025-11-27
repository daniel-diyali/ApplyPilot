# backend/app/core/validators.py
import re
from urllib.parse import urlparse
from typing import Optional

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    # Check if it's 10-15 digits
    return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15

def validate_text_length(text: str, min_length: int = 10, max_length: int = 50000) -> bool:
    """Validate text length"""
    return min_length <= len(text.strip()) <= max_length

def sanitize_text(text: str) -> str:
    """Basic text sanitization"""
    return text.strip()[:50000]  # Limit to 50k chars