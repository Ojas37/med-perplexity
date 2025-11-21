import os
import requests
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fallback Knowledge Base (used if APIs fail)
KNOWLEDGE_BASE = {
    "infection": """
    [SOURCE: ICMR Guidelines for Antimicrobial Use 2024]
    For Community-Acquired Pneumonia (bacterial):
    - First Line: Amoxicillin 500mg TDS.
    - Alternative (if allergic): Azithromycin 500mg OD.
    - Severe/Comorbid: Levofloxacin 750mg OD (Caution in Renal Failure).
    """,
    "diabetes": """
    [SOURCE: ICMR Guidelines for Management of Type 2 Diabetes 2018]
    - First Line: Metformin 500mg BD.
    - Contraindication: Avoid Metformin if eGFR < 30 mL/min (Kidney Disease).
    - Target HbA1c: < 7.0%.
    """,
    "pain": """
    [SOURCE: Standard Treatment Guidelines India]
    For Acute Pain:
    - Mild: Paracetamol 500mg.
    - Moderate: Ibuprofen 400mg (Avoid in CKD/Ulcers).
    - Severe: Tramadol 50mg.
    """
}

def search_pubmed(query, max_results=3):
    """
    Search PubMed for relevant medical research articles.
    Returns formatted citations and abstracts.
    """
    try:
        # Step 1: Search PubMed for article IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_data = search_response.json()
        
        if "esearchresult" not in search_data or not search_data["esearchresult"].get("idlist"):
            return None
        
        ids = search_data["esearchresult"]["idlist"]
        
        # Step 2: Fetch article details
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml"
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        
        if fetch_response.status_code == 200:
            return fetch_response.text[:2000]  # Return first 2000 chars of XML
        
        return None
        
    except Exception as e:
        print(f"PubMed API Error: {e}")
        return None

def research_node(state):
    """
    Uses PubMed API + Groq LLM to research treatment guidelines.
    Falls back to local knowledge base if APIs fail.
    """
    print("\n--- 📚 AGENT 2: RESEARCHING MEDICAL LITERATURE ---")
    
    query = state.get("user_query", "")
    patient_profile = state.get("patient_profile", {})
    
    # Extract comprehensive patient context
    conditions = patient_profile.get("conditions", [])
    conditions_str = ", ".join(conditions) if conditions else "general patient"
    vitals = patient_profile.get("vitals", {})
    age = patient_profile.get("age", "Unknown")
    gender = patient_profile.get("gender", "Unknown")
    recent_labs = patient_profile.get("recent_labs", "No recent labs")
    
    # Step 1: Search PubMed
    print("Searching PubMed database...")
    pubmed_results = search_pubmed(f"{query} India guidelines treatment")
    
    # Step 2: Use Groq LLM to synthesize findings
    try:
        # Build highly detailed context-aware prompt
        prompt = f"""You are an expert clinical decision support AI for Indian healthcare, trained on ICMR guidelines and Indian pharmacology standards.

COMPLETE PATIENT PROFILE:
- Age: {age} years | Gender: {gender}
- Medical Conditions: {conditions_str}
- Current Medications: {', '.join(patient_profile.get('medications', []))}
- Known Allergies: {', '.join(patient_profile.get('allergies', [])) if patient_profile.get('allergies') else 'None'}
- Lab Values: {vitals}
- Recent Lab Report: {recent_labs}

CLINICAL QUERY: {query}

RESEARCH DATA AVAILABLE:
- PubMed Results: {pubmed_results if pubmed_results else "Limited"}
- ICMR Guidelines: Available for reference

YOUR TASK:
Provide a detailed, evidence-based treatment recommendation that:
1. References specific ICMR/Indian clinical guidelines
2. Lists 2-3 medications with exact dosages appropriate for THIS patient's age and conditions
3. Prioritizes Jan Aushadhi (generic) alternatives with approximate costs
4. Includes specific precautions based on the patient's lab values and comorbidities
5. Explains the clinical rationale briefly

OUTPUT FORMAT (150 words max):
**Clinical Recommendation:**
[Medication recommendations with dosages]

**Precautions:**
[Specific to this patient's profile]

**Evidence Basis:**
[ICMR guideline reference or clinical evidence]"""

        print("Analyzing with AI medical reasoning...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian medical AI trained on ICMR guidelines. Provide evidence-based, India-specific treatment recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Groq's current medical-capable model
            temperature=0.3,  # Lower temperature for more consistent medical advice
            max_tokens=500
        )
        
        findings = chat_completion.choices[0].message.content
        print(f"✓ Research Complete. AI-generated clinical recommendation ready.")
        
        return {"research_findings": findings}
        
    except Exception as e:
        print(f"⚠ API Error: {e}. Using fallback knowledge base.")
        
        # Fallback to hardcoded guidelines
        query_lower = query.lower()
        if "infection" in query_lower or "fever" in query_lower or "cough" in query_lower:
            findings = KNOWLEDGE_BASE["infection"]
        elif "sugar" in query_lower or "diabetes" in query_lower:
            findings = KNOWLEDGE_BASE["diabetes"]
        elif "pain" in query_lower or "headache" in query_lower:
            findings = KNOWLEDGE_BASE["pain"]
        else:
            findings = "No specific guidelines found. Recommend specialist consultation."
        
        return {"research_findings": findings}