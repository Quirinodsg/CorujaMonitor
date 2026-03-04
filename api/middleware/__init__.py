"""
Middleware package for Coruja Monitor API
"""

from .waf import WAFMiddleware

__all__ = ['WAFMiddleware']
