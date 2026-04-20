#!/usr/bin/env python
import requests
import json

# Test login endpoint
try:
    response = requests.post('http://localhost:8000/api/auth/login/', json={
        'car_number': 'TEST-1234',
        'password': 'wrongpass',
        'role': 'User'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
