import requests
from uuid import uuid4

# Test endpoint
API_BASE_URL = "http://localhost:5000"  # Update this to your actual backend URL

def test_correlation_id_flow():
    """
    This script tests the correlation ID flow by:
    1. Making a request to the backend with a custom correlation ID
    2. Verifying that the correlation ID is returned in the response
    """
    print("Testing correlation ID flow...")
    
    # Generate a test correlation ID
    test_correlation_id = str(uuid4())
    print(f"Generated test correlation ID: {test_correlation_id}")
    
    # Make a request to the health endpoint with the correlation ID
    headers = {"X-Correlation-ID": test_correlation_id}
    try:
        response = requests.get(f"{API_BASE_URL}/health/detailed", headers=headers)
        
        # Check if the response has our correlation ID
        if response.ok:
            response_correlation_id = response.headers.get("X-Correlation-ID")
            print(f"Response status: {response.status_code}")
            print(f"Response correlation ID: {response_correlation_id}")
            
            if response_correlation_id == test_correlation_id:
                print("✅ SUCCESS: Correlation ID was properly propagated!")
            else:
                print("❌ FAILURE: Correlation ID was not correctly propagated.")
                
            # Show the response content
            print("\nResponse content:")
            print(response.json())
        else:
            print(f"❌ Request failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error making request: {str(e)}")

if __name__ == "__main__":
    test_correlation_id_flow() 