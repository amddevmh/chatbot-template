#!/usr/bin/env python3
"""
Generate a development token for testing
"""
import asyncio
from app.auth.security import create_dev_token

def main():
    """Generate and print a development token"""
    token = create_dev_token()
    print("\n=== DEVELOPMENT TOKEN ===")
    print(f"Bearer {token}")
    print("=========================\n")
    print("This token is mapped to the 'dev_test_user' account.")
    print("Use it in the Authorization header for API requests:")
    print("Authorization: Bearer <token>")

if __name__ == "__main__":
    main()
