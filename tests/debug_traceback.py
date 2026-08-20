
import requests
import json
import traceback

try:
    # 1. Create a SoilProfile first
    profile_data = {
        "raw_data": [
            {"Depth from [m]": 0, "Depth to [m]": 5, "qc [MPa]": 10, "Dr [%]": 50, "Soil type": "Sand"},
            {"Depth from [m]": 5, "Depth to [m]": 10, "qc [MPa]": 15, "Dr [%]": 60, "Soil type": "Sand"}
        ],
        "name": "Test Profile Delegation"
    }

    res = requests.post("http://127.0.0.1:8000/api/objects/create?type_name=SoilProfile", json=profile_data)
    if res.status_code != 200:
        print("Failed to create profile:", res.text)
        exit(1)
    
    profile_id = res.json()['id']
    print(f"Profile created: {profile_id}")

    # 2. Call plot_with_log using LogPlot-style parameters
    payload = {
        "moduleId": "general", 
        "functionId": "plot_with_log", # Using the base function ID
        "args": {
            "soilprofile": profile_id,
            "parameters": "qc [MPa], Dr [%]" # Simple string API
        }
    }

    res = requests.post("http://127.0.0.1:8000/api/execute", json=payload)
    result = res.json()
    
    output = ""
    if res.status_code != 200:
        output += "Backend returned non-200:\n"
        output += res.text + "\n"
    else:
        result = res.json()
        if "error" in result:
            output += "plot_with_log returned error:\n"
            output += result['error'] + "\n"
        else:
            output += "Success\n"
            
    with open("tests/debug_final.txt", "w", encoding="utf-8") as f:
        f.write(output)

except Exception:
    with open("tests/debug_final.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
