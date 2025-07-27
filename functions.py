import json
# import os
from conn import connect_firebase
# import whisper
# import sounddevice as sd
# import speech_recognition as sr
# from google.cloud import     texttospeech
import google.generativeai as genai
import re
# Add new Q&A
# from flask import Flask, jsonify
# import firebase_admin
# from firebase_admin import credentials, firestore


# import os

# from google.cloud import texttospeech

# from gtts import gTTS
# import os

genai.configure(api_key="Your_API_Key")

def clean_json_string(response_text):
    # Remove ```json or ``` and ```
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    return cleaned

# model = whisper.load_model("base") 
def get_gemini_response(prompt):
    prompt += """ You are a friendly village helper talking to a farmer.
    Speak in simple language. Answer in same language. Avoid bullet points. Be short and clear.you can ask if you want"""

 
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Error generating response."

query_templates = [
    {
        "id": 0,
        "name": "farm_info",
        "fields": ["crop", "location", "intent", "problem", "solution_needed"]
    },
    {
        "id": 1,
        "name": "emotional_check",
        "fields": ["is_farmer_stressed", "emotional_state", "urgency"]
    },
    {
        "id": 2,
        "name": "scheme_eligibility",
        "fields": ["is_any_problem", "possible_govt_help", "help_type", "location"]
    }
]
def extract_multi_query(user_input, query_templates=query_templates):
    model = genai.GenerativeModel("gemini-1.5-flash")
    results = {}
    
    for q in query_templates:
        fields_prompt = "\n".join([f"- {f}" for f in q["fields"]])
        json_format = "{\n" + "\n".join([f'  "{f}": "..."' for f in q["fields"]]) + "\n}"

        prompt = f"""
        Farmer says: "{user_input}"

        Extract the following fields:
        {fields_prompt}

        Return JSON ONLY in this format:
        {json_format}
        If a field is not available, put null.
        """

        response = model.generate_content(prompt)
        cleaned_json = clean_json_string(response.text)

        try:
            parsed = json.loads(cleaned_json)  # ✅ Proper JSON
            results[q["name"]] = parsed
            act_on_results(parsed, "farmer_123", user_input)  # ✅ Pass parsed dict
        except Exception as e:
            print(f"❌ JSON decode failed: {e}")
            print("→ Raw response was:", response.text)
            results[q["name"]] = {}

    return results

def act_on_results(results, farmer_id, farmer_input):
    emotional_data = results.get("emotional_check", {})
    is_stressed = emotional_data.get("is_farmer_stressed") == "yes"
    print("is it stressed",is_stressed)
    if is_stressed:
        ngo_info = fetch_ngo_email_from_firebase()
        ngo_email = ngo_info.get("email", "emergency@example.com")
        ngo_name = ngo_info.get("name", "Local NGO")

        # Simulate email to NGO
        print(f"📬 Alert sent to NGO: {ngo_name} ({ngo_email})")
        print("Subject:", f"Farmer {farmer_id} might be in distress")
        print("Body:")
        print(f"""
        Farmer ID: {farmer_id}
        Emotional State: {emotional_data.get('emotional_state')}
        Urgency: {emotional_data.get('urgency')}
        Extracted Data: {json.dumps(results, indent=2)}
        """)

    # Government help logic
    if results.get("scheme_eligibility", {}).get("is_any_problem") == "yes":
        gov_suggestion = suggest_gov_scheme_with_gemini(
            farmer_input=farmer_input,
            location=results["scheme_eligibility"].get("location")
        )
        results["scheme_eligibility"]["gov_scheme_suggestion"] = gov_suggestion

    # ✅ Store everything in Firebase
    store_all_data(farmer_id, results)

def fetch_ngo_email_from_firebase():
    db = connect_firebase()
    doc = db.collection("ngo_contacts").document("default").get()
    data = doc.to_dict()
    return {
        "email": data.get("email", "emergency@example.com"),
        "name": data.get("name", "Local NGO")
    }

def suggest_gov_scheme_with_gemini(farmer_input, location=None):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    A farmer from {location or "an unknown location"} says: "{farmer_input}".

    Based on the government schemes in India, suggest a relevant scheme that could help the farmer.

    Include:
    - Scheme name
    - Department (if known)
    - Why it's relevant
    - How the farmer can apply (brief)

    Keep it simple and local-language friendly.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini gov scheme error:", str(e))
        return "Sorry, could not fetch scheme suggestion right now."


def store_all_data(farmer_id, extracted_data):
    db = connect_firebase()
    doc_ref = db.collection("farmer_insights").document(farmer_id)
    doc_ref.set(extracted_data)
def fetch_ngo_email_from_firebase():
    db = connect_firebase()
    doc = db.collection("ngo_contacts").document("default").get()
    return doc.to_dict().get("email", "emergency@example.com")

# Initialize Firebase only once
import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account.json"


def store_convo(collection_name, doc_id, data):
    db = connect_firebase()
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()

    if doc.exists:
        existing_data = doc.to_dict()

        # Append to existing 'history' if exists, otherwise create new
        existing_history = existing_data.get("history", [])
        new_history = data.get("history", [])
        existing_history.extend(new_history)

        # Combine all data, prioritizing new fields and merged history
        merged_data = {**existing_data, **data}
        merged_data["history"] = existing_history
    else:
        merged_data = data

    # Optional: Generate a summary (e.g., count of messages)
    merged_data["summary"] = f"{len(merged_data.get('history', []))} questions asked so far."

    doc_ref.set(merged_data)

# def listen_whisper(lang="hi"):
#     print("Listening with Whisper... Speak now")
#     duration = 5  # seconds
#     fs = 16000
#     filename = "D:/Agentic ai/recorded.wav"



#     try:
#         audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#         sd.wait()

#         # Save the recording
#         import soundfile as sf
#         sf.write(filename, audio, fs, subtype='PCM_16')
#         import time
#         time.sleep(1)  
#         # Ensure file is saved before passing to whisper
#         if not os.path.exists(filename):
#             print("Audio file not found after recording.")
#             return None

#         print("Recorded file saved at:", filename)
#         print("File exists:", os.path.exists(filename))

#         model = whisper.load_model("base") 
#         result = model.transcribe(filename, language=lang)
#         text = result["text"]
#         print("User:", text)
#         return text
#     except Exception as e:
#         print("Whisper error:", e)
#         return None

# def better_tts(text, lang_code="gu-IN", voice_name="gu-IN-Wavenet-A"):
#     tts_client = texttospeech.TextToSpeechClient()
#     synthesis_input = texttospeech.SynthesisInput(text=text)
#     voice = texttospeech.VoiceSelectionParams(language_code=lang_code, name=voice_name)
#     audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

#     response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

#     with open("response.mp3", "wb") as out:
#         out.write(response.audio_content)

#     os.system("start response.mp3")  # Replace with 'afplay' or 'mpg123' on Linux/Mac

#     client = texttospeech.TextToSpeechClient()

#     synthesis_input = texttospeech.SynthesisInput(text=text)

#     voice = texttospeech.VoiceSelectionParams(
#         language_code=lang_code,
#         name=voice_name
#     )

#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3,
#         speaking_rate=0.9
#     )

#     response = client.synthesize_speech(
#         input=synthesis_input, voice=voice, audio_config=audio_config
#     )

#     with open("output.mp3", "wb") as out:
#         out.write(response.audio_content)

#     os.system("start output.mp3")
