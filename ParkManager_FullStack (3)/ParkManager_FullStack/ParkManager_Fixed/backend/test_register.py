#!/usr/bin/env python
import requests
import json

# Test registration endpoint
print("Testing account creation...")
try:
    response = requests.post('http://localhost:8000/api/auth/register/', json={
        'car_number': 'TES-9999',
        'name': 'John Doe',
        'password': 'password123',
        'phone': '+8801712345678',
        'email': 'john@example.com'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ Account created successfully!")
        # Try to login with the new account
        print("\nTesting login with new account...")
        login_resp = requests.post('http://localhost:8000/api/auth/login/', json={
            'car_number': 'TES-9999',
            'password': 'password123',
            'role': 'User'
        })
        print(f"Login Status: {login_resp.status_code}")
        print(f"Login Response: {json.dumps(login_resp.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
