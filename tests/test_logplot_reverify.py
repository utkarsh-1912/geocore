
import requests
import json
import traceback

try:
    # 1. Create a SoilProfile
    print("Creating SoilProfile...")
    profile_data = {
        "raw_data": [
            {"Depth from [m]": 0, "Depth to [m]": 5, "qc [MPa]": 10, "Dr [%]": 50, "Soil type": "Sand"},
            {"Depth from [m]": 5, "Depth to [m]": 10, "qc [MPa]": 15, "Dr [%]": 60, "Soil type": "Sand"}
        ],
        "name": "Test Profile LogPlot"
    }

    res = requests.post("http://127.0.0.1:8000/api/objects/create?type_name=SoilProfile", json=profile_data)
    if res.status_code != 200:
        print("Failed to create profile:", res.text)
        exit(1)
    
    profile_id = res.json()['id']
    print(f"Profile created: {profile_id}")

    # 2. Call LogPlot
    print("Calling LogPlot...")
    payload = {
        "moduleId": "general", 
        "functionId": "LogPlot", 
        "args": {
            "soilprofile": profile_id,
            "parameters": "qc [MPa], Dr [%]"
        }
    }

    res = requests.post("http://127.0.0.1:8000/api/execute", json=payload)
    
    if res.status_code != 200:
        print("LogPlot failed:", res.text)
        exit(1)
        
    result = res.json()
    if "error" in result:
        print("LogPlot returned error:", result['error'])
        exit(1)
        
    print("LogPlot Success!")

except Exception:
    traceback.print_exc()
