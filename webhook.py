from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GLPI_API_URL = os.environ.get("GLPI_API_URL")
APP_TOKEN = os.environ.get("APP_TOKEN")
USER_TOKEN = os.environ.get("USER_TOKEN")

def start_session():
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}"
    }
    response = requests.get(f"{GLPI_API_URL}/initSession", headers=headers)
    session_token = response.json().get('session_token')
    return session_token

def process_ticket(ticket_id):
    session_token = start_session()
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }
    ticket = requests.get(f"{GLPI_API_URL}/Ticket/{ticket_id}", headers=headers).json()

    if ticket.get("assign_users_id") and ticket.get("assign_groups_id"):
        payload = {
            "input": {
                "id": ticket_id,
                "assign_groups_id": 0
            }
        }
        requests.put(f"{GLPI_API_URL}/Ticket/{ticket_id}", json=payload, headers=headers)

    requests.get(f"{GLPI_API_URL}/killSession", headers=headers)

@app.route("/glpi-webhook", methods=["POST"])
def glpi_webhook():
    data = request.json
    ticket_id = data.get("item", {}).get("id")
    if ticket_id:
        process_ticket(ticket_id)
    return jsonify({"status": "OK"}), 200
