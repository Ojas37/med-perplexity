import json
from typing import TypedDict
from langgraph.graph import StateGraph, END

# Import our agents
from personalization_agent import personalization_node
from research_agent import research_node
from safety_agent import safety_agent_node

# 1. Define the State (The Baton passed between agents)
class AgentState(TypedDict):
    patient_id: str
    user_query: str
    patient_profile: dict
    research_findings: str
    safety_check: str
    final_answer: str

# 2. Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("personalize", personalization_node)
workflow.add_node("research", research_node)
workflow.add_node("safety", safety_agent_node)

# Add Edges (The Logic Flow)
workflow.set_entry_point("personalize")
workflow.add_edge("personalize", "research")
workflow.add_edge("research", "safety")
workflow.add_edge("safety", END)

# Compile
app = workflow.compile()

# ==========================================
# 3. HELPER FUNCTION TO RUN SCENARIOS
# ==========================================
def run_scenario(scenario_num, patient_id, query, description):
    """Run a single test scenario and display results."""
    print("\n" + "="*80)
    print(f"📋 SCENARIO {scenario_num}: {description}")
    print("="*80)
    print(f"👤 Patient: {patient_id} | Query: {query}")
    
    # Run the Agents
    result = app.invoke({"patient_id": patient_id, "user_query": query})
    
    # Print Final Report
    print("\n" + "="*80)
    print("      🤖 MED PERPLEXITY CLINICAL DECISION SUPPORT")
    print("="*80)
    print(f"👤 PATIENT PROFILE:")
    print(f"   Name: {result['patient_profile'].get('name', 'N/A')}")
    print(f"   Conditions: {', '.join(result['patient_profile']['conditions'])}")
    print(f"   Current Meds: {', '.join(result['patient_profile']['medications'])}")
    print(f"   Allergies: {', '.join(result['patient_profile']['allergies']) if result['patient_profile']['allergies'] else 'None'}")
    print("-" * 80)
    print(f"📚 AI RESEARCH FINDINGS:")
    print(f"   {result['research_findings'].strip()}")
    print("-" * 80)
    print(f"🛡️ SAFETY VALIDATION:")
    print(f"   {result['safety_check']}")
    print("="*80)
    
    return result

# ==========================================
# 4. RUN MULTIPLE TEST SCENARIOS
# ==========================================
if __name__ == "__main__":
    print("🏥 MED PERPLEXITY: MULTI-AGENT AI SYSTEM STARTUP...")
    print("Powered by: Groq AI + PubMed + ICMR Guidelines\n")
    
    import time
    
    # SCENARIO 1: High-Risk Drug Interaction (CKD + Antibiotic)
    # Expected: System should flag Levofloxacin contraindication
    start_time = time.time()
    run_scenario(
        scenario_num=1,
        patient_id="P001",
        query="Patient has high fever and chest infection. Recommend antibiotics.",
        description="CRITICAL SAFETY CHECK - Kidney Disease + Antibiotic Interaction"
    )
    print(f"\n⏱️ Processing Time: {time.time() - start_time:.2f} seconds")
    
    # SCENARIO 2: Simple Case (Healthy Patient with Migraine)
    # Expected: System should approve standard treatment
    input("\n\n⏸️  Press Enter to run SCENARIO 2...")
    start_time = time.time()
    run_scenario(
        scenario_num=2,
        patient_id="P002",
        query="Patient complains of severe headache and sensitivity to light. Recommend treatment.",
        description="ROUTINE CASE - Migraine Management"
    )
    print(f"\n⏱️ Processing Time: {time.time() - start_time:.2f} seconds")
    
    # SCENARIO 3: Diabetic Patient Asking for Glucose Management
    # Expected: System should recommend Metformin but check for kidney function
    input("\n\n⏸️  Press Enter to run SCENARIO 3...")
    start_time = time.time()
    run_scenario(
        scenario_num=3,
        patient_id="P003",
        query="Patient's HbA1c is elevated at 7.2. Need medication to control blood sugar.",
        description="CHRONIC DISEASE MANAGEMENT - Type 2 Diabetes"
    )
    print(f"\n⏱️ Processing Time: {time.time() - start_time:.2f} seconds")
    
    # Summary
    print("\n" + "="*80)
    print("✅ ALL SCENARIOS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("🎯 Demo Highlights:")
    print("   ✓ Real-time PubMed research integration")
    print("   ✓ AI-powered personalization based on patient history")
    print("   ✓ Multi-layer safety validation (Rule-based + AI)")
    print("   ✓ India-specific guidelines (ICMR compliance)")
    print("   ✓ Generic drug recommendations (Jan Aushadhi)")
    print("="*80)