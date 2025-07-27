
from flask import Flask, request, jsonify,render_template, request, jsonify
import requests

import requests
import speech_recognition as sr
from functions import get_gemini_response, store_convo,  connect_firebase,extract_multi_query
import firebase_admin
from firebase_admin import credentials, firestore
app = Flask(__name__)

# Replace this with your actual API key
API_KEY = '579b464db66ec23bdd000001daf31d06e63a45177110d3d935ad9a24'
BASE_URL = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask-farmer", methods=["POST"])
def ask_farmer():
    try:
        data = request.get_json()
        user_input = data.get("message")
        # farmer_id = data.get("farmer_id")

        # if not user_input or not farmer_id:
        #     return jsonify({"reply": "Missing message or farmer_id"}), 400

        # 1. Gemini A — user-facing reply
        reply = get_gemini_response(user_input)
       
        # 2. Gemini B — background extraction
        structured_data = extract_multi_query(user_input)

        # 3. Save conversation
        store_convo(
    collection_name="conversations",
    doc_id="ramu_123",
    data={
        "history": [{"question": user_input, "answer":reply}]
    }
)

       

        # 4. Store farm data
        if structured_data:
            store_convo(
    collection_name="farm",
    doc_id="ramu_123",
    data=structured_data)

            # db.collection("farm").document(farmer_id).set(structured_data, merge=True)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500


@app.route('/mandi-price', methods=['GET'])
def get_mandi_price():
    

    params = {
        'api-key': API_KEY,
        'format': 'json'  # Change to 'xml' if you want XML response
    }

    # Mapping UI form inputs to exact filter keys expected by the API
    filter_map = {
        'state': 'state.keyword',
        'district': 'district',
        'market': 'market',
        'commodity': 'commodity',
        'variety': 'variety',
        'grade': 'grade'
    }

    # Add filters to the request
    for ui_key, api_filter_key in filter_map.items():
        value = request.args.get(ui_key)
        if value:
            params[f'filters[{api_filter_key}]'] = value

    # Optional pagination
    for pagination_key in ['offset', 'limit']:
        value = request.args.get(pagination_key)
        if value:
            params[pagination_key] = value

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        print("Response status code:", response)
        data = response.json()

        if 'records' in data and data['records']:
            return jsonify(data)
        else:
            return jsonify({
                "message": "😔 No mandi data found for the given filters.",
                "filters_used": params
            }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to fetch data from Mandi API.",
            "details": str(e),
            "params": params
        }), 500


@app.route('/mandi-ui')
def mandi_ui():
    return render_template('mandi_price.html')


@app.route("/farm/home", methods=["GET"])
def farm_home():
    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    # Simulated farmer city (normally you'd get this from the farmer's profile or session)
    farmer_city = "Ahmedabad" 

    # Get alerts from Firebase Firestore    
    db = firestore.client()
    alerts_ref = db.collection("alerts")
    query = alerts_ref.where("city", "==", farmer_city)
    alerts = query.stream()

    # Extract messages from Firebase
    alert_messages = [alert.to_dict().get("message") for alert in alerts if alert.to_dict().get("message")]

    # ❌ This line overrides the real data (remove it)
    # alerts = ["Heavy rain in Nagpur", "Pest alert in Nashik"]

    return render_template("index.html", alerts=alert_messages)



from google.cloud import aiplatform



# Initialize Vertex AI
PROJECT_ID = "project-kisaan-466511"
REGION = "us-central1"  # or the region you deployed in
ENDPOINT_ID = "8659152147503382528"
aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(ENDPOINT_ID)
@app.route("/predict_form")    
def predict_form():     
    return render_template("predict.html")

@app.route("/predict", methods=["POST"])    
def predict_crop():
    try:
        data = request.get_json()
        
        instance = {
            "N": str(data["N"]),
            "P": str(data["P"]),
            "K": str(data["K"]),
            "temperature": str(data["temperature"]),
            "humidity": str(data["humidity"]),
            "ph": str(data["ph"]),
            "rainfall": str(data["rainfall"])
        }
        prediction = endpoint.predict(instances=[instance])

        # Extract only the 'classes' array from prediction result
        predicted_classes = prediction.predictions[0]["classes"]
        print("Predicted classes:", predicted_classes)
        return jsonify({"predicted_classes": predicted_classes})

    except Exception as e:
        print("Prediction error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/farmer-chat", methods=["GET"])
def farmer_chat():
    return render_template("chat.html")
  
# def farmer_voice_chat():
#     user_text = listen_whisper()
#     if not user_text:
#         return jsonify({"error": "Could not understand"}), 400

#     ai_response = get_gemini_response(user_text)
#     better_tts(ai_response)
#     return jsonify({"user_input": user_text, "gemini_reply": ai_response})
if __name__ == '__main__':
    app.run(debug=True)
