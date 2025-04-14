import pandas as pd
import requests
import matplotlib.pyplot as plt

# 🔹 Load Dataset
file_path = "dataset.csv"
df = pd.read_csv(file_path)

# 🔹 Display Columns
print("Dataset Columns:", df.columns)

# 🔹 Identify Columns
symptom_cols = df.columns[1:]  # All columns except 'diseases' (assuming first column is the disease)
actual_diag_col = "diseases"    # The actual diagnosis column

# 🔹 FastAPI Endpoint
api_url = "http://localhost:8000/diagnose/"

# 🔹 Limit to 100 Patients
total_patients = min(100, len(df))  # Run only on 100 patients

# 🔹 Evaluate AI on Multiple Patients
ai_correct = 0

for i in range(total_patients):
    # 🩺 Extract symptoms (where value == 1)
    patient_symptoms = [symptom for symptom in symptom_cols if df.loc[i, symptom] == 1]

    # Convert list of symptoms into a single comma-separated string
    symptoms_str = ", ".join(patient_symptoms)

    diagnosis_request = {
        "symptoms": symptoms_str,  # 🔥 Send as a single string instead of a list
        "history": "",  # No explicit history in dataset
        "test_results": ""  # No explicit test results in dataset
    }
    
    response = requests.post(api_url, json=diagnosis_request)
    
    if response.status_code == 200:
        ai_result = response.json()
        
        # 🛠 Extract AI diagnosis safely
        try:
            ai_diagnosis = ai_result.get("Diagnosis", {}).get("Diagnosis Suggestion", "Unknown")
        except AttributeError:
            ai_diagnosis = "Unknown"

        actual_diagnosis = str(df.loc[i, actual_diag_col])

        print(f"\n🔹 Patient {i+1}")
        print(f"AI Diagnosis: {ai_diagnosis}")
        print(f"Actual Diagnosis: {actual_diagnosis}")

        if ai_diagnosis.lower() == actual_diagnosis.lower():
            ai_correct += 1
    else:
        print(f"❌ Error processing patient {i+1}: {response.text}")

# 🔹 Calculate AI Accuracy
accuracy = (ai_correct / total_patients) * 100
print(f"\n✅ AI Accuracy: {accuracy:.2f}% on {total_patients} Patients")

# 🔹 Generate Accuracy Chart
categories = ['Correct Diagnoses', 'Incorrect Diagnoses']
values = [ai_correct, total_patients - ai_correct]

plt.figure(figsize=(6, 4))
plt.bar(categories, values, color=['green', 'red'])
plt.xlabel("Diagnosis Accuracy")
plt.ylabel("Number of Cases")
plt.title(f"AI Model Performance on {total_patients} Patients")
plt.show()
