#!/usr/bin/env python3
"""
Test script to verify Flask API endpoints are working correctly
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_home():
    """Test the home endpoint"""
    print("\n=== Testing HOME endpoint ===")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_predict():
    """Test the predict endpoint"""
    print("\n=== Testing PREDICT endpoint ===")
    test_comments = {
        "comments": [
            {"text": "This is great!", "timestamp": "2024-01-12T10:00:00Z"},
            {"text": "I love this", "timestamp": "2024-01-12T10:05:00Z"},
            {"text": "This is terrible", "timestamp": "2024-01-12T10:10:00Z"}
        ]
    }
    try:
        response = requests.post(
            f"{API_URL}/predict_with_timestamps",
            json=test_comments,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_language_detection():
    """Test the language detection endpoint"""
    print("\n=== Testing LANGUAGE DETECTION endpoint ===")
    test_comments = {
        "comments": [
            "This is great!",
            "Esto es excelente",
            "C'est fantastique",
            "Das ist großartig"
        ]
    }
    try:
        response = requests.post(
            f"{API_URL}/detect_languages",
            json=test_comments,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Language detection chart generated successfully!")
            print(f"Response size: {len(response.content)} bytes")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FLASK API ENDPOINT TESTS")
    print("=" * 50)
    
    results = {
        "Home": test_home(),
        "Predict": test_predict(),
        "Language Detection": test_language_detection(),
    }
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Check Flask backend.")
