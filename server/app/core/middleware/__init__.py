"""
Middleware modules for the application.
"""
import os
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from typing import Optional
import logging
import traceback

# Try to import slowapi with Redis backend
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    # Get Redis URL from environment
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Create Redis-backed limiter
    limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)
    _SLOWAPI_AVAILABLE = True
    
except ImportError as e:
    limiter = None
    _SLOWAPI_AVAILABLE = False
    _IMPORT_ERROR = str(e)


def setup_middleware(app: FastAPI):
    """
    Setup middleware like CORS, logging, etc.
    """
    # Example: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Example: simple request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger = logging.getLogger("app.requests")
        logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Exception in request: {e}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": str(e)}
            )


def _check_slowapi():
    """Helper to check if slowapi is available"""
    if not _SLOWAPI_AVAILABLE:
        raise ImportError(
            "slowapi is required for rate limiting. "
            "Install it with: pip install slowapi"
        )


class RateLimitMiddleware:
    """Rate limiting configuration for advisory endpoints"""
    
    # Default rate limits
    DEFAULT = "default"
    
    # Stricter limits for write operations
    WRITE = "write"
    
    # Most strict for search
    SEARCH = "search"
    
    # Auth and upload limits
    AUTH = "auth"
    UPLOAD = "upload"
    
    # Limits per endpoint type
    LIMITS = {
        DEFAULT: "100/hour",
        WRITE: "20/minute",
        SEARCH: "30/minute",
        AUTH: "5/minute",
        UPLOAD: "10/hour"
    }
    
    @classmethod
    def get_limit_key(cls, endpoint_type: str = DEFAULT) -> str:
        """Get rate limit string for endpoint type"""
        return cls.LIMITS.get(endpoint_type, cls.LIMITS[cls.DEFAULT])


# Spam detection patterns
SPAM_PATTERNS = {
    # Excessive links
    "excessive_links": {
        "pattern": r'https?://[^\s]+[^\s]*[^\s]+',
        "max_count": 2,
        "message": "Too many links in content"
    },
    # All caps
    "all_caps": {
        "pattern": r'^[A-Z\s\d]{20,}$',
        "message": "Content appears to be all caps"
    },
    # Repeated characters
    "repeated_chars": {
        "pattern": r'(.)\1{5,}',
        "message": "Repeated characters detected"
    },
    # Promotional language
    "promotional": {
        "pattern": r'(?i)(buy now|click here|free offer|limited time)',
        "message": "Promotional content not allowed"
    },
    # Suspicious domains
    "suspicious_domains": [
        r'bit\.ly',
        r'tinyurl\.com',
        r'goo\.gl'
    ]
}


def detect_spam(content: str, patterns: dict = SPAM_PATTERNS) -> list:
    """
    Detect potential spam in content.
    
    Returns list of detected spam indicators.
    """
    import re
    from collections import Counter
    
    detected = []
    
    # Check for excessive links
    links = re.findall(r'https?://[^\s]+', content)
    if len(links) > patterns["excessive_links"]["max_count"]:
        detected.append({
            "type": "excessive_links",
            "message": patterns["excessive_links"]["message"],
            "count": len(links)
        })
    
    # Check for all caps
    if re.search(patterns["all_caps"]["pattern"], content):
        detected.append({
            "type": "all_caps",
            "message": patterns["all_caps"]["message"]
        })
    
    # Check for repeated characters
    if re.search(patterns["repeated_chars"]["pattern"], content):
        detected.append({
            "type": "repeated_chars",
            "message": patterns["repeated_chars"]["message"]
        })
    
    # Check for promotional language
    if re.search(patterns["promotional"]["pattern"], content):
        detected.append({
            "type": "promotional",
            "message": patterns["promotional"]["message"]
        })
    
    # Check for suspicious domains
    for domain_pattern in patterns["suspicious_domains"]:
        if re.search(domain_pattern, content):
            detected.append({
                "type": "suspicious_domain",
                "message": f"Suspicious link detected"
            })
            break
    
    return detected


__all__ = [
    "setup_middleware",
    "limiter",
    "RateLimitMiddleware",
    "detect_spam",
    "SPAM_PATTERNS"
]
