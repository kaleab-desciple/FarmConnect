"""
Rate Limiting Middleware
Advisory Service - Farm Connect AgriManagement
"""
import os
from typing import Optional

# Try to import optional dependencies
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    # Get Redis URL from environment
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Create Redis-backed limiter
    limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)
    _SLOWAPI_AVAILABLE = True
    
except ImportError:
    _SLOWAPI_AVAILABLE = False
    limiter = None


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


class SpamPreventionService:
    """Service for spam detection and prevention"""
    
    def __init__(self, db=None):
        self.db = db
    
    async def check_content(
        self,
        content: str,
        user_id: str,
        content_type: str = "thread"
    ) -> dict:
        """
        Check content for spam indicators.
        
        Returns:
            is_spam: bool
            score: float (0-100)
            reasons: list of detected issues
        """
        # Check for spam patterns
        issues = detect_spam(content)
        
        # Check user's recent activity
        recent_count = await self._get_user_recent_count(user_id, content_type)
        
        # Calculate spam score
        score = 0
        reasons = []
        
        for issue in issues:
            score += 25
            reasons.append(issue)
        
        if recent_count > 10:
            score += 20
            reasons.append({
                "type": "rapid_posting",
                "message": f"User has posted {recent_count} {content_type}s recently"
            })
        
        is_spam = score >= 50
        
        return {
            "is_spam": is_spam,
            "score": min(score, 100),
            "reasons": reasons,
            "action": "flag" if is_spam else "approve"
        }
    
    async def _get_user_recent_count(
        self,
        user_id: str,
        content_type: str,
        minutes: int = 30
    ) -> int:
        """Get user's recent content count"""
        # TODO: Implement with Redis counter
        return 0
    
    async def flag_for_review(
        self,
        user_id: str,
        content_id: str,
        content_type: str,
        reasons: list
    ):
        """Flag content for moderator review"""
        # TODO: Create report for moderation queue
        pass
    
    async def auto_reject(
        self,
        content_id: str,
        content_type: str,
        reasons: list
    ):
        """Auto-reject content due to spam"""
        # TODO: Reject and notify user
        pass

