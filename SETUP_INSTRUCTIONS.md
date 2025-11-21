# 🚀 Med Perplexity - API Setup Instructions

## ✅ What's Been Done

Your project now has:
- ✅ **Groq AI integration** (Free, fast LLM)
- ✅ **PubMed API integration** (Real medical research)
- ✅ **AI-powered safety validation**
- ✅ **Fallback to local data** (if APIs fail)

---

## 🔑 Step 1: Get Your Groq API Key (FREE)

1. **Go to**: https://console.groq.com/
2. **Sign up** with your Google account (takes 30 seconds)
3. **Navigate to**: "API Keys" in the sidebar
4. **Click**: "Create API Key"
5. **Copy** the key (starts with `gsk_...`)

---

## 📝 Step 2: Create Your .env File

1. In your project folder, create a file named `.env` (no extension)
2. Add this line to it:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

**Important**: Replace `gsk_your_actual_key_here` with the key you copied from Groq.

---

## 🧪 Step 3: Test the System

Run your application:

```powershell
python main.py
```

You should see:
- ✅ Agent 1 fetching patient data
- ✅ Agent 2 searching PubMed + AI analysis
- ✅ Agent 3 running safety checks with AI validation

---

## 🎯 What Each Agent Now Does

### 🔍 Research Agent (research_agent.py)
- **Searches PubMed** for real medical research
- **Uses Groq AI** to synthesize findings
- **Falls back** to local ICMR guidelines if API fails
- **Prioritizes** Indian/generic medications

### 👤 Personalization Agent (personalization_agent.py)
- Reads patient data from `patients.json`
- *(Future: Will connect to ABDM API when you get credentials)*

### 🛡️ Safety Agent (safety_agent.py)
- **Rule-based checks** for known contraindications
- **AI-powered deep analysis** for edge cases
- **Checks drug interactions** using FDA database (RxNav API - free)
- **Provides confidence scores**

---

## 🆓 APIs Used (All Free!)

| API | Purpose | Cost |
|-----|---------|------|
| **Groq** | AI reasoning & synthesis | FREE (500K tokens/day) |
| **PubMed E-utilities** | Medical research papers | FREE (No key needed) |
| **RxNav (FDA)** | Drug interactions | FREE (No key needed) |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
Run: `pip install groq python-dotenv requests`

### "API Key not found"
Make sure your `.env` file is in the project root and has the correct format.

### "PubMed timeout"
This is normal if internet is slow. The system will use fallback guidelines.

---

## 🚀 Next Steps (After Demo Works)

1. **Add more patients** to `patients.json`
2. **Expand KNOWLEDGE_BASE** with more conditions
3. **Build a web UI** with Streamlit
4. **Get ABDM sandbox access** for real patient data
5. **Add vector database** (Pinecone/Weaviate) for 138M documents

---

## 📞 Need Help?

Check the code comments in each agent file for detailed explanations.
