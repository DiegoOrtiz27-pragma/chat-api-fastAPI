"""
Configures the rate limiting functionality for the application.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Identifies clients by their IP address.
limiter = Limiter(key_func=get_remote_address)