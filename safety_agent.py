import json
import os
import requests
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================================
# 1. THE KNOWLEDGE BASE (The "Trap" Database)
# ==========================================
# In a real startup, this would be an API call to a Drug Database.
# For the Hackathon, we hardcode the specific scenario you will demo.

# Dictionary of drugs and the conditions/allergies they clash with
CONTRAINDICATIONS = {
    "metformin": {
        "condition_conflict": ["Chronic Kidney Disease", "CKD", "Renal Failure"],
        "reason": "Risk of lactic acidosis in patients with impaired renal function."
    },
    "ibuprofen": {
        "condition_conflict": ["Peptic Ulcer", "Kidney Disease", "Asthma"],
        "reason": "Can cause acute renal failure or worsen ulcer bleeding."
    },
    "levofloxacin": {
        "condition_conflict": ["Arrhythmia", "Kidney Disease"],
        "reason": "Requires dosage adjustment in renal impairment; risk of QT prolongation."
    }
}

# Dictionary of known severe drug-drug interactions
DRUG_INTERACTIONS = {
    "warfarin": ["aspirin", "ibuprofen"], # Blood thinners + NSAIDs
    "sildenafil": ["nitroglycerin", "isosorbide"] # Nitrates
}

# ==========================================
# 2. THE SAFETY AGENT LOGIC
# ==========================================

def check_drug_interactions_api(drug_name):
    """
    Check drug interactions using free RxNav API (FDA database).
    Returns list of interactions or None if API fails.
    """
    try:
        # RxNav interaction API
        url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={drug_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Parse interaction data (simplified)
            return data.get("fullInteractionTypeGroup", [])
        
        return None
    except Exception as e:
        print(f"Drug API Error: {e}")
        return None


def safety_agent_node(state):
    """
    AI-powered safety validation with rule-based fallback.
    Uses Groq LLM + local contraindication database.
    """
    
    print("\n--- 🛡️ AGENT 3: SAFETY GUARDRAIL ANALYZING ---")
    
    # 1. Unpack the state
    proposed_treatment_text = state.get("research_findings", "")
    patient_profile = state.get("patient_profile", {})
    
    # Extract comprehensive patient data
    patient_conditions = patient_profile.get("conditions", [])
    patient_allergies = patient_profile.get("allergies", [])
    current_meds = patient_profile.get("medications", [])
    vitals = patient_profile.get("vitals", {})
    age = patient_profile.get("age", "Unknown")
    gender = patient_profile.get("gender", "Unknown")
    lab_flags = patient_profile.get("lab_flags", "")
    recent_labs = patient_profile.get("recent_labs", "")

    # 2. Rule-based checks (Fast, guaranteed to catch known issues)
    warnings = []
    is_safe = True
    
    proposed_lower = proposed_treatment_text.lower()

    # Check allergies
    for drug in CONTRAINDICATIONS.keys():
        if drug in proposed_lower:
            if any(drug in allergy.lower() for allergy in patient_allergies):
                warnings.append(f"CRITICAL: Patient is allergic to {drug.upper()}.")
                is_safe = False

    # Check disease contraindications
    for drug, info in CONTRAINDICATIONS.items():
        if drug in proposed_lower:
            conflicts = info["condition_conflict"]
            for condition in patient_conditions:
                if any(c.lower() in condition.lower() for c in conflicts):
                    warnings.append(f"CONTRAINDICATION: {drug.upper()} + {condition}. {info['reason']}")
                    is_safe = False

    # Check drug-drug interactions
    for drug, interacting_drugs in DRUG_INTERACTIONS.items():
        if drug in proposed_lower:
            for med in current_meds:
                if any(interacting in med.lower() for interacting in interacting_drugs):
                    warnings.append(f"INTERACTION: {drug.upper()} interacts with {med}.")
                    is_safe = False

    # 3. AI-powered deep analysis using Groq
    try:
        print("Running AI safety analysis...")
        
        prompt = f"""You are an expert clinical pharmacology AI safety validator for Indian hospitals, trained on ICMR protocols and Indian drug safety standards.

PROPOSED TREATMENT PLAN:
{proposed_treatment_text}

COMPLETE PATIENT PROFILE:
- Age: {age} years | Gender: {gender}
- Medical Conditions: {', '.join(patient_conditions) if patient_conditions else 'None'}
- Current Medications: {', '.join(current_meds) if current_meds else 'None'}
- Known Allergies: {', '.join(patient_allergies) if patient_allergies else 'None'}
- Laboratory Values: {vitals}
- Lab Summary: {lab_flags}
- Recent Lab Report: {recent_labs}

AUTOMATED SAFETY CHECKS ALREADY PERFORMED:
{chr(10).join(warnings) if warnings else "✓ No contraindications detected by rule-based system"}

YOUR TASK AS FINAL SAFETY VALIDATOR:
You have access to the patient's COMPLETE medical record including all lab values. Perform a comprehensive safety analysis:

1. Cross-reference proposed medications against patient's specific lab values (creatinine, eGFR, liver function, etc.)
2. Validate dosage appropriateness for patient's age, weight, and organ function
3. Check for drug-drug interactions with current medications
4. Verify no allergy conflicts
5. Assess if any dosage adjustments needed based on renal/hepatic function
6. Consider patient's comorbidities and their impact on drug metabolism

CONFIDENCE SCORING GUIDANCE:
- 95-100%: All data available, no concerns, standard dosing appropriate
- 85-94%: Minor precautions needed but treatment is safe
- 70-84%: Moderate concerns, dosage adjustment recommended
- Below 70%: Significant safety concerns, alternative treatment suggested

OUTPUT FORMAT (Be specific and use the available lab data):
SAFETY STATUS: [SAFE/WARNING/CRITICAL]
CONFIDENCE: [85-100% - Be confident when lab data supports your assessment]
ANALYSIS: [3-4 sentences with specific reference to lab values and clinical rationale]
RECOMMENDATIONS: [Specific dosage adjustments OR confirm treatment is safe as proposed]"""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical safety AI trained on Indian pharmacology guidelines and ICMR protocols. Be conservative and flag any potential safety concerns."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,  # Very low temperature for safety-critical analysis
            max_tokens=400
        )
        
        ai_analysis = chat_completion.choices[0].message.content
        
        # Combine rule-based and AI analysis
        if warnings:
            final_msg = f"⚠️ SAFETY WARNINGS DETECTED:\n\n"
            final_msg += "🔴 RULE-BASED CHECKS:\n"
            final_msg += "\n".join([f"  • {w}" for w in warnings])
            final_msg += f"\n\n🤖 AI DEEP ANALYSIS:\n{ai_analysis}"
        else:
            final_msg = f"✅ RULE-BASED CHECKS: PASSED\n\n🤖 AI SAFETY ANALYSIS:\n{ai_analysis}"
        
        print(f"✓ Safety analysis complete.")
        
        return {"safety_check": final_msg, "final_answer": final_msg}
        
    except Exception as e:
        print(f"⚠ AI Analysis failed: {e}. Using rule-based results only.")
        
        # Fallback to rule-based only
        if is_safe:
            safety_msg = "✅ SAFETY CHECK PASSED: No contraindications found against patient profile."
        else:
            safety_msg = "⚠️ SAFETY WARNINGS DETECTED:\n" + "\n".join([f"- {w}" for w in warnings])
        
        return {"safety_check": safety_msg, "final_answer": safety_msg}


# ==========================================
# 3. TEST HARNESS (Run this file directly)
# ==========================================
if __name__ == "__main__":
    # Mock Input 1: A Safe Scenario
    safe_input = {
        "research_findings": "I recommend starting Paracetamol 500mg for the fever.",
        "patient_profile": {
            "conditions": ["Hypertension"],
            "allergies": ["Penicillin"],
            "medications": ["Amlodipine"]
        }
    }
    
    # Mock Input 2: The "Trap" Scenario (Metformin + Kidney Disease)
    danger_input = {
        "research_findings": "Based on guidelines, Metformin 500mg is the first-line therapy.",
        "patient_profile": {
            "conditions": ["Chronic Kidney Disease (Stage 3)"],
            "allergies": ["Sulfa drugs"],
            "medications": ["Lisinopril"]
        }
    }

    print("Test 1 (Should be Safe):")
    print(safety_agent_node(safe_input)["safety_check"])
    
    print("\n" + "="*30 + "\n")
    
    print("Test 2 (Should Fail):")
    print(safety_agent_node(danger_input)["safety_check"])