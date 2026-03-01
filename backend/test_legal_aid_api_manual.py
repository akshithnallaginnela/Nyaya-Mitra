"""
Manual test script for legal aid endpoints.

This script tests the legal aid endpoints by making actual HTTP requests
to verify they work correctly.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_search_endpoint():
    """Test the search endpoint."""
    print("\n=== Testing GET /api/legal-aid/search ===")
    
    # Test 1: Search by city
    print("\n1. Search by city (Mumbai):")
    response = requests.get(f"{BASE_URL}/api/legal-aid/search?city=Mumbai")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total results: {data['total']}")
        print(f"Is fallback: {data['is_fallback']}")
        if data['providers']:
            print(f"First provider: {data['providers'][0]['name']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Search by state
    print("\n2. Search by state (Maharashtra):")
    response = requests.get(f"{BASE_URL}/api/legal-aid/search?state=Maharashtra")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total results: {data['total']}")
    
    # Test 3: Search with multiple criteria
    print("\n3. Search with multiple criteria:")
    response = requests.get(
        f"{BASE_URL}/api/legal-aid/search?city=Mumbai&case_type=Criminal Law&language=Hindi"
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total results: {data['total']}")
    
    # Test 4: Search with no results (should return national helplines)
    print("\n4. Search with no results (fallback to national helplines):")
    response = requests.get(f"{BASE_URL}/api/legal-aid/search?city=NonExistentCity")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total results: {data['total']}")
        print(f"Is fallback: {data['is_fallback']}")
        if data['providers']:
            print(f"First helpline: {data['providers'][0]['name']}")


def test_detail_endpoint():
    """Test the provider detail endpoint."""
    print("\n\n=== Testing GET /api/legal-aid/{id} ===")
    
    # First, get a provider ID from search
    response = requests.get(f"{BASE_URL}/api/legal-aid/search?city=Mumbai")
    if response.status_code == 200:
        data = response.json()
        if data['providers']:
            provider_id = data['providers'][0]['id']
            print(f"\nGetting details for provider ID: {provider_id}")
            
            # Get provider details
            detail_response = requests.get(f"{BASE_URL}/api/legal-aid/{provider_id}")
            print(f"Status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                provider = detail_response.json()
                print(f"Name: {provider['name']}")
                print(f"Organization type: {provider['organization_type']}")
                print(f"Specializations: {provider['specializations']}")
                print(f"Languages: {provider['languages_supported']}")
                print(f"Contact info: {provider['contact_info']}")
                print(f"Availability: {provider['availability']}")
                
                # Count contact methods
                contact_methods = sum(
                    1 for v in provider['contact_info'].values() if v is not None
                )
                print(f"Number of contact methods: {contact_methods}")
            else:
                print(f"Error: {detail_response.text}")
        else:
            print("No providers found to test detail endpoint")
    else:
        print(f"Error getting providers: {response.text}")
    
    # Test with invalid ID
    print("\n\nTesting with invalid ID:")
    response = requests.get(f"{BASE_URL}/api/legal-aid/00000000-0000-0000-0000-000000000000")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("Correctly returned 404 for invalid ID")


def test_response_structure():
    """Test that responses have correct structure."""
    print("\n\n=== Testing Response Structure ===")
    
    response = requests.get(f"{BASE_URL}/api/legal-aid/search")
    if response.status_code == 200:
        data = response.json()
        
        # Check top-level fields
        required_fields = ['providers', 'total', 'is_fallback']
        print("\nChecking top-level fields:")
        for field in required_fields:
            present = field in data
            print(f"  {field}: {'✓' if present else '✗'}")
        
        # Check provider fields
        if data['providers']:
            provider = data['providers'][0]
            provider_fields = [
                'id', 'name', 'organization_type', 'specializations',
                'languages_supported', 'city', 'state', 'is_verified'
            ]
            print("\nChecking provider fields:")
            for field in provider_fields:
                present = field in provider
                print(f"  {field}: {'✓' if present else '✗'}")


if __name__ == "__main__":
    print("=" * 60)
    print("Legal Aid API Manual Test")
    print("=" * 60)
    print("\nMake sure the FastAPI server is running on http://localhost:8000")
    print("and the database has been seeded with legal aid providers.")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("\n✓ Server is running")
            
            test_search_endpoint()
            test_detail_endpoint()
            test_response_structure()
            
            print("\n" + "=" * 60)
            print("Tests completed!")
            print("=" * 60)
        else:
            print("\n✗ Server is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Make sure it's running on http://localhost:8000")
