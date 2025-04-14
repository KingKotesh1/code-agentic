import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

# 🔹 Load API Key
load_dotenv()
API_KEY = "AIzaSyCDkHAz83d5AbSaj-Rf9ApLTcvGPr-xJkM"
if not API_KEY:
    raise ValueError("❌ Gemini API key not found. Set GEMINI_API_KEY in .env")

# 🔹 Initialize Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API_KEY)

# 📌 Request Models
class DiagnoseRequest(BaseModel):
    symptoms: str
    history: str
    test_results: str

# 🔹 AI Agent Functions
def extract_json(response):
    """Extract JSON from AI response."""
    if hasattr(response, "content"):
        raw_content = response.content.strip("`json\n")  # Remove any markdown formatting
    else:
        raw_content = str(response)

    try:
        return json.loads(raw_content)  # Convert to dictionary
    except json.JSONDecodeError:
        return {"error": "Invalid AI response format", "raw_response": raw_content}

def doctor_assistant(prompt: str) -> dict:
    """Generate diagnosis response in structured JSON format."""
    response = llm.invoke(f"""
    You are an AI doctor assistant. Given the input:
    {prompt}

    Format the response as JSON:
    {{
      "Diagnosis Suggestion": "Primary diagnosis here",
      "Alternative Possibilities": ["Alternative 1", "Alternative 2"],
      "Confidence Score": "80%",
      "Recommended Tests": ["Test 1", "Test 2"],
      "Suggested Treatment Approach": "Treatment plan details",
      "Doctor's Final Review Needed": "Yes"
    }}
    """)
    return extract_json(response)

def measurement_agent(prompt: str) -> dict:
    """Analyze test results and suggest further actions."""
    response = llm.invoke(f"""
    You are an AI specializing in medical test analysis. Given:
    {prompt}

    Format response as JSON:
    {{
      "Test Findings": "Key observations from test results",
      "Potential Implications": ["Implication 1", "Implication 2"],
      "Recommended Follow-ups": ["Follow-up 1", "Follow-up 2"],
      "Confidence Score": "75%"
    }}
    """)
    return extract_json(response)

def moderator_agent(prompt: str) -> dict:
    """Ensure AI-generated medical advice follows compliance standards."""
    response = llm.invoke(f"""
    You are a medical AI ensuring compliance with healthcare standards.
    {prompt}

    Format response as JSON:
    {{
      "Validation Result": "Valid/Invalid",
      "Reasoning": "Explanation for validation result",
      "Suggested Improvements": ["Improvement 1", "Improvement 2"],
      "Final Recommendation": "Seek Further Review / Approved"
    }}
    """)
    return extract_json(response)

# 📌 FastAPI App
app = FastAPI()

@app.post("/diagnose/")
async def diagnose(request: DiagnoseRequest):
    """Runs doctor assistant + test analysis + moderation automatically."""
    try:
        print("🔄 Running Multi-Agent Diagnosis Pipeline...")

        # Step 1: Initial Diagnosis
        diagnosis_prompt = f"Patient Symptoms: {request.symptoms}. History: {request.history}. Diagnose the condition."
        diagnosis = doctor_assistant(diagnosis_prompt)
        print("🔍 Diagnosis Response:", diagnosis)

        # Step 2: Analyze Test Results
        analysis_prompt = f"Test Results: {request.test_results}. Provide analysis and further steps."
        analysis = measurement_agent(analysis_prompt)
        print("🔍 Test Analysis Response:", analysis)

        # Step 3: Moderator Validates Advice
        moderation_prompt = f"Check if the following diagnosis is valid: {diagnosis}"
        moderation = moderator_agent(moderation_prompt)
        print("🔍 Moderation Response:", moderation)

        return {
            "Diagnosis": diagnosis,
            "Test Analysis": analysis,
            "Moderation Feedback": moderation
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run FastAPI Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
