import requests
import time
import os
import sys


BASE_URL = "http://localhost:8000"


if len(sys.argv) > 1:
    TEST_FILE = sys.argv[1]
else:
    TEST_FILE = "test_document.txt"


if not os.path.exists(TEST_FILE):
    with open(TEST_FILE, "w") as f:
        f.write("This is a sample document for heavy processing tests.")

def test_async_workflow():
    print(f"--- Starting Async Workflow Test ---")
    
    
    print(f"\n1. Uploading file: {TEST_FILE}...")
    with open(TEST_FILE, "rb") as f:
        response = requests.post(f"{BASE_URL}/upload", files={"file": f})
    
    if response.status_code != 202:
        print(f"FAILED: Upload failed: {response.text}")
        return
    
    data = response.json()
    job_id = data["job_id"]
    print(f"SUCCESS: Upload successful! Received Job ID: {job_id}")
    print(f"Server Message: {data['message']}")

    
    print(f"\n2. Polling for status (every 2 seconds)...")
    
    while True:
        status_response = requests.get(f"{BASE_URL}/status/{job_id}")
        if status_response.status_code != 200:
            print(f"FAILED: Status check failed: {status_response.text}")
            break
            
        status_data = status_response.json()
        status = status_data["status"]
        progress = status_data["progress"]
        
        print(f"STATUS: {status.upper()} | Progress: {progress}%")
        
        if status == "completed":
            print(f"\nCOMPLETED: Job Finished Successfully!")
            print(f"DATE: Completed at: {status_data['completed_at']}")
            print(f"URL: Result URL: {status_data['result_url']}")
            break
        elif status == "failed":
            print(f"FAILED: Job failed: {status_data.get('error')}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    try:
        test_async_workflow()
    except Exception as e:
        print(f"Error during test: {e}")
        print("INFO: Make sure async_microservice.py is running on port 8000")
