from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# === Replace these with your credentials ===
API_KEY = "KvzobjkwbNuSsRR2HigTJIrWTGsg_QsFOl8kLl57zoed"
DEPLOYMENT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/e05f883b-627a-4a83-accd-d59331600923/ai_service_stream?version=2021-05-01"  # e.g., https://us-south.ml.cloud.ibm.com/ml/v4/deployments/xxxx/agent

# === Get IAM Token ===
def get_access_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Auth Error:", response.text)
        return None

# === Call Watsonx Agent ===
def call_watsonx(role, experience, query):
    token = get_access_token()
    if not token:
        return "Error: Authentication failed. Check API key."

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
    "messages": [
        {
            "role": "user",
            "content": f"Role: {role}\nExperience: {experience} years\nQuery: {query}"
        }
    ]
}

    response = requests.post(DEPLOYMENT_URL, headers=headers, json=payload)
    print("DEBUG:", response.status_code, response.text)

    if response.status_code == 200:
        try:
            return response.json()["results"][0]["generated_text"]
        except Exception:
            return "Error: Unexpected response format."
    else:
        return f"Error {response.status_code}: {response.text}"


# === Flask Routes ===
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        role = request.form.get("role")
        experience = request.form.get("experience")
        query = request.form.get("query")
        result = call_watsonx(role, experience, query)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
