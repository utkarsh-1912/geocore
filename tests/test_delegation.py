
import requests
import json

# 1. Create a SoilProfile first
print("Creating SoilProfile...")
profile_data = {
    "raw_data": [
        {"Depth from [m]": 0, "Depth to [m]": 5, "qc [MPa]": 10, "Dr [%]": 50, "Soil type": "Sand"},
        {"Depth from [m]": 5, "Depth to [m]": 10, "qc [MPa]": 15, "Dr [%]": 60, "Soil type": "Sand"}
    ],
    "name": "Test Profile Delegation"
}

try:
    res = requests.post("http://127.0.0.1:8000/api/objects/create?type_name=SoilProfile", json=profile_data)
    if res.status_code != 200:
        print("Failed to create profile:", res.text)
        exit(1)
    
    profile_id = res.json()['id']
    print(f"Profile created: {profile_id}")

    # 2. Call plot_with_log using LogPlot-style parameters
    print("Calling plot_with_log with parameters...")
    payload = {
        "moduleId": "general", 
        "functionId": "plot_with_log", # Using the base function ID
        "args": {
            "soilprofile": profile_id,
            "parameters": "qc [MPa], Dr [%]" # Simple string API
        }
    }

    res = requests.post("http://127.0.0.1:8000/api/execute", json=payload)
    
    if res.status_code != 200:
        print("plot_with_log failed:", res.text)
        exit(1)
        
    result = res.json()
    
    if "error" in result:
        print("plot_with_log returned error:", result['error'])
        exit(1)
        
    print("plot_with_log Success!")
    print("Result Type:", result.get('type'))
    if result.get('type') == 'plotly':
        print("Contains Plotly Data:", 'data' in result and 'layout' in result)
        print("Number of traces:", len(result['data']))
    else:
        print("Unexpected result type:", result.get('type'))
        print(json.dumps(result, indent=2))

except Exception as e:
    print(f"Test failed: {e}")
