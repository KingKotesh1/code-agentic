import streamlit as st
import requests
from speech_to_text import transcribe_audio

API_URL = "http://127.0.0.1:8000/diagnose/"

st.title("🎤 AgentClinic with Voice-to-Text")

# Upload audio for symptoms
symptom_audio = st.file_uploader("Upload Symptom Voice (WAV)", type=["wav"])
history_audio = st.file_uploader("Upload History Voice (WAV)", type=["wav"])
test_audio = st.file_uploader("Upload Test Results Voice (WAV)", type=["wav"])

if st.button("🎙️ Transcribe Audio"):
    if symptom_audio:
        with open("symptoms.wav", "wb") as f:
            f.write(symptom_audio.read())
        st.session_state["symptoms"] = transcribe_audio("symptoms.wav")
    if history_audio:
        with open("history.wav", "wb") as f:
            f.write(history_audio.read())
        st.session_state["history"] = transcribe_audio("history.wav")
    if test_audio:
        with open("test.wav", "wb") as f:
            f.write(test_audio.read())
        st.session_state["test_results"] = transcribe_audio("test.wav")

# Show transcribed text
symptoms = st.text_area("Symptoms", value=st.session_state.get("symptoms", ""))
history = st.text_area("Medical History", value=st.session_state.get("history", ""))
test_results = st.text_area("Test Results", value=st.session_state.get("test_results", ""))

if st.button("🔍 Get Diagnosis"):
    if symptoms.strip() and history.strip() and test_results.strip():
        with st.spinner("Processing..."):
            response = requests.post(API_URL, json={
                "symptoms": symptoms,
                "history": history,
                "test_results": test_results
            })

            if response.status_code == 200:
                data = response.json()
                st.subheader("📋 Diagnosis")
                st.json(data["Diagnosis"])
                st.subheader("📊 Test Analysis")
                st.json(data["Test Analysis"])
                st.subheader("✅ Moderation Feedback")
                st.json(data["Moderation Feedback"])
            else:
                st.error("❌ Failed to fetch diagnosis.")
