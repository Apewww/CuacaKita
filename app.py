import os
import json
import requests
import mimetypes
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
from pywebpush import webpush, WebPushException

# Fix Windows MIME type issue
mimetypes.add_type('application/javascript', '.js')

load_dotenv()
api_key = os.getenv("API_KEY")
vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
vapid_claim_email = os.getenv("VAPID_CLAIM_EMAIL")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
scheduler = APScheduler()

# Subscription Model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(500), nullable=False)
    p256dh = db.Column(db.String(200), nullable=False)
    auth = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), default="Cimahi")
    last_condition = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# Background Tasks
def check_weather_updates():
    with app.app_context():
        print("Checking for weather updates...")
        subs = Subscription.query.all()
        # Group subscriptions by city to minimize API calls
        city_groups = {}
        for sub in subs:
            if sub.city not in city_groups:
                city_groups[sub.city] = []
            city_groups[sub.city].append(sub)
        
        for city, city_subs in city_groups.items():
            try:
                # Fetch current weather
                url = "http://api.weatherapi.com/v1/current.json"
                params = {"key": api_key, "q": city}
                response = requests.get(url, params=params)
                data = response.json()
                
                new_condition = data['current']['condition']['text']
                
                # Check for significant changes
                for sub in city_subs:
                    if sub.last_condition and sub.last_condition != new_condition:
                        # Significant change detection (demo: any change)
                        send_custom_push(sub, {
                            "title": f"Update Cuaca - {city}",
                            "body": f"Cuaca berubah dari {sub.last_condition} menjadi {new_condition}.",
                            "icon": data['current']['condition']['icon'].replace('//', 'https://'),
                            "url": "/"
                        })
                    
                    sub.last_condition = new_condition
                
                db.session.commit()
            except Exception as e:
                print(f"Error checking weather for {city}: {e}")

def send_custom_push(sub, payload):
    try:
        webpush(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            },
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_claim_email}
        )
    except WebPushException as e:
        print(f"Push failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw():
    response = send_from_directory('static', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/api/weather')
def get_weather():
    city = request.args.get('city', 'Cimahi')
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": "City not found or API error"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vapid-public-key')
def get_vapid_public_key():
    return jsonify({"publicKey": vapid_public_key})

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    sub_data = data.get('subscription')
    city = data.get('city', 'Cimahi')
    
    if not sub_data or 'endpoint' not in sub_data:
        return jsonify({"error": "Invalid subscription data"}), 400
    
    exists = Subscription.query.filter_by(endpoint=sub_data['endpoint']).first()
    if not exists:
        new_sub = Subscription(
            endpoint=sub_data['endpoint'],
            p256dh=sub_data['keys']['p256dh'],
            auth=sub_data['keys']['auth'],
            city=city
        )
        db.session.add(new_sub)
        db.session.commit()
    else:
        exists.city = city
        db.session.commit()
    
    return jsonify({"status": "success"})

@app.route('/api/test-push', methods=['POST'])
def test_push():
    if not app.debug:
        return jsonify({"error": "Unauthorized in production"}), 403
        
    subs = Subscription.query.all()
    results = []
    payload = {
        "title": "CuacaKita Update",
        "body": "Ini adalah notifikasi percobaan dari CuacaKita!",
        "icon": "/static/icons/icon-192x192.png",
        "url": "/"
    }
    
    for sub in subs:
        try:
            send_custom_push(sub, payload)
            results.append({"endpoint": sub.endpoint, "status": "sent"})
        except Exception as e:
            results.append({"endpoint": sub.endpoint, "status": "failed", "error": str(e)})
            
    return jsonify({"results": results})

@app.route('/api/debug-subs')
def debug_subs():
    if not app.debug:
        return jsonify({"error": "Unauthorized in production"}), 403
        
    subs = Subscription.query.all()
    return jsonify([{
        "id": s.id,
        "endpoint": s.endpoint,
        "city": s.city,
        "last_condition": s.last_condition
    } for s in subs])

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    
    # Scheduler setup
    app.config['SCHEDULER_API_ENABLED'] = True
    scheduler.init_app(app)
    scheduler.add_job(id='weather_job', func=check_weather_updates, trigger='interval', minutes=30)
    scheduler.start()
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)