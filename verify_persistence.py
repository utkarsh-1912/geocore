import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_persistence():
    print("Testing Soil Profile Persistence...")

    # 1. Create a Profile
    payload = {
        "name": "Test Profile Persistence",
        "raw_data": [
            {
                "Depth from [m]": 0,
                "Depth to [m]": 10,
                "Soil type": "Sand",
                "Unit Weight [kN/m3]": 18,
                "Total Unit Weight [kN/m3]": 20,
                "Cohesion [kPa]": 0,
                "Friction Angle [deg]": 35
            }
        ],
        "water_level": 2
    }
    
    print("Creating profile...")
    res = requests.post(f"{BASE_URL}/objects/create?type_name=SoilProfile", json=payload)
    if res.status_code != 200:
        print(f"Failed to create profile: {res.text}")
        return
    
    data = res.json()
    obj_id = data.get("id")
    print(f"Profile created with ID: {obj_id}")

    # 2. Check JSON file existence
    time.sleep(1) # Wait for write
    json_path = os.path.join(os.path.dirname(__file__), "python-backend", "core", "saved_objects.json")
    # Adjust path based on where we run this script. Assuming run from root.
    # Actually state.py saves to 'saved_objects.json' in CWD of backend process usually.
    # The backend is running in python-backend directory based on previous logs? 
    # Let's check where main.py runs. It runs in python-backend. So file is at python-backend/saved_objects.json
    
    json_path = os.path.join("python-backend", "saved_objects.json")
    
    if os.path.exists(json_path):
        print(f"Found saved_objects.json at {json_path}")
        with open(json_path, 'r') as f:
            saved_data = json.load(f)
            found = any(item['id'] == obj_id for item in saved_data)
            if found:
                print("SUCCESS: Profile found in saved_objects.json")
            else:
                print("FAILURE: Profile NOT found in saved_objects.json")
    else:
        print(f"WARNING: saved_objects.json not found at {json_path}. It might be in a different CWD.")

    # 3. View Profile (Get Details)
    print("Fetching profile details...")
    res = requests.get(f"{BASE_URL}/objects/SoilProfile/{obj_id}")
    if res.status_code == 200:
        details = res.json()
        if 'data' in details and len(details['data']) > 0:
            print("SUCCESS: Retrieved profile data for viewing.")
        else:
            print("FAILURE: Profile data missing in details.")
    else:
        print(f"Failed to get details: {res.text}")

    # 4. Delete Profile
    print("Deleting profile...")
    res = requests.delete(f"{BASE_URL}/objects/SoilProfile/{obj_id}")
    if res.status_code == 200:
        print("Profile deleted via API.")
    else:
        print(f"Failed to delete profile: {res.text}")

    # 5. Check if removed from file
    time.sleep(1)
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            saved_data = json.load(f)
            found = any(item['id'] == obj_id for item in saved_data)
            if not found:
                print("SUCCESS: Profile removed from saved_objects.json")
            else:
                print("FAILURE: Profile STILL found in saved_objects.json after delete")

if __name__ == "__main__":
    test_persistence()
