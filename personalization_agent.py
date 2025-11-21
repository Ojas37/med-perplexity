import json

def personalization_node(state):
    """
    Reads patient_id from state, fetches profile from patients.json,
    and updates the 'patient_profile' in the state.
    """
    print("\n--- 👤 AGENT 1: FETCHING ABDM RECORD ---")
    
    patient_id = state.get("patient_id")
    
    try:
        # Open the local "database" file
        with open("patients.json", "r") as f:
            db = json.load(f)
            
        data = db.get(patient_id)
        
        if data:
            # Format a complete summary for the downstream agents with all available data
            summary = {
                "name": data["name"],
                "age": data.get("age", "N/A"),
                "gender": data.get("gender", "N/A"),
                "conditions": data["conditions"],
                "medications": data["medications"],
                "allergies": data["allergies"],
                "vitals": data.get("vitals", {}),
                "recent_labs": data.get("recent_labs", "No recent labs"),
                # Create comprehensive lab summary
                "lab_flags": f"Creatinine: {data.get('vitals', {}).get('creatinine', 'N/A')}, eGFR: {data.get('vitals', {}).get('eGFR', 'N/A')}"
            }
            print(f"Found Record: {data['name']} | Conditions: {data['conditions']}")
            return {"patient_profile": summary}
        else:
            print(f"Error: Patient ID {patient_id} not found.")
            return {"patient_profile": {"conditions": [], "allergies": [], "medications": []}}
            
    except FileNotFoundError:
        print("Error: patients.json file not found.")
        return {"patient_profile": {"error": "Database Missing"}}