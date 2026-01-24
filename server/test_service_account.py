#!/usr/bin/env python3
"""
Test script for service account authentication.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.auth.service_account import get_service_token, validate_service_token
from app.core.auth.jwt import verify_token, extract_roles, is_service_account


def test_service_account():
    """Test service account token acquisition and validation."""
    print("=" * 60)
    print("Testing Service Account Authentication")
    print("=" * 60)
    
    try:
        # Get service account token
        print("\n1. Acquiring service account token...")
        token = get_service_token("test_service")
        print(f"✓ Token acquired successfully")
        print(f"  Token (first 50 chars): {token[:50]}...")
        
        # Verify token
        print("\n2. Verifying token...")
        payload = verify_token(token)
        print(f"✓ Token verified successfully")
        
        # Check if it's a service account
        print("\n3. Checking service account status...")
        is_service = is_service_account(payload)
        print(f"✓ Is service account: {is_service}")
        
        if not is_service:
            print("✗ ERROR: Token is not from a service account!")
            return False
        
        # Extract roles
        print("\n4. Extracting roles...")
        roles = extract_roles(payload)
        print(f"✓ Roles: {roles}")
        
        # Display token info
        print("\n5. Token Information:")
        print(f"  Subject: {payload.get('sub')}")
        print(f"  Authorized Party: {payload.get('azp')}")
        print(f"  Preferred Username: {payload.get('preferred_username')}")
        print(f"  Issuer: {payload.get('iss')}")
        print(f"  Audience: {payload.get('aud')}")
        print(f"  Expires At: {payload.get('exp')}")
        
        # Check for client roles
        print("\n6. Client Roles:")
        resource_access = payload.get('resource_access', {})
        for client, access in resource_access.items():
            client_roles = access.get('roles', [])
            print(f"  {client}: {client_roles}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_service_account()
    sys.exit(0 if success else 1)
