#!/usr/bin/env python3
"""
Generate secure random secret keys for Django deployment.
Run this script and copy the keys to your Railway environment variables.
"""

import secrets

def generate_key(length=50):
    """Generate a URL-safe random key."""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("=" * 70)
    print("Django Secret Key Generator")
    print("=" * 70)
    print("\nGenerate these keys for your Railway environment variables:\n")
    
    print("SECRET_KEY:")
    print(generate_key())
    print()
    
    print("JWT_SIGNING_KEY:")
    print(generate_key())
    print()
    
    print("=" * 70)
    print("\n⚠️  IMPORTANT:")
    print("- Never commit these keys to git")
    print("- Use different keys for development and production")
    print("- Store them securely in Railway environment variables")
    print("=" * 70)
