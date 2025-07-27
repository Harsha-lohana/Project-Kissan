# 🌾 Project Kisan — Empowering Farmers with AI

Project Kisan is an AI-powered Flask-based web application built to support Indian farmers with real-time agricultural insights and services. It leverages voice-based interaction, government scheme automation, mandi price tracking, and crop price prediction to deliver an end-to-end smart solution — even for farmers without smartphones.

---

## 🚀 Features

- 🔊 **Voice-based farmer interaction** (STT + TTS)
- 📈 **Crop price prediction** using AI
- 🏛️ **Auto form submission** to NGOs / Government Schemes
- 💹 **Live mandi price fetch** by state & district
- 🗣️ **Hindi / Local Language** support using Google APIs
- 📱 **Chatbot for real-time help**
- 🧠 **Vertex AI & Gemini** integrated intelligence

---

## 🛠️ Tech Stack

| Layer        | Technology Used                        |
|--------------|----------------------------------------|
| Backend      | Python, Flask                          |
| AI/ML        | Vertex AI, Google Gemini, OpenAI       |
| Voice        | Google Cloud TTS + STT, gTTS           |
| UI           | HTML5, CSS3, JavaScript                |
| Database     | Firebase (Realtime DB / Firestore)     |
| Hosting      | (Optional: Render / Railway / Local)   |

---

## 📂 Folder Structure (Sample)
project-kisan/
├── app.py
├── functions.py
├── templates/
│ └── index.html
├── requirements.txt
├── README.md
└── .gitignore


---

## ⚙️ How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/your-username/project-kisan.git

# 2. Navigate into project folder
cd project-kisan

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Flask App
python app.py

📊 Example Use Case
Farmer speaks: “Show me today's price for cotton in Bhavnagar.”

AI fetches live mandi rates via API.

Farmer says: “Submit crop loan request.”

AI auto-fills govt scheme form and connects to NGO if needed.

🌍 Real-World Impact
✅ Support for farmers without smartphones
✅ Voice-first AI for inclusivity
✅ Real-time price prediction to avoid losses
✅ Bridge between farmers, government & NGOs

🤝 Team AutoNeura — Hackathon Project
Built during Google Agentic AI Day Hackathon 2025
Team Name: AutoNeura
