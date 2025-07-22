from flask import Flask, jsonify, request
import threading
from selenium_automation import SeleniumAutomation
import os

app = Flask(__name__)

selenium_automation = None

def log_to_console(message, level="INFO"):
    print(f"[{level}] {message}")

@app.route('/join_meet', methods=['POST'])
def join_meet():
    global selenium_automation
    meet_url = request.json.get('meet_url')
    if not meet_url:
        return jsonify({"error": "meet_url is required"}), 400

    if not selenium_automation:
        selenium_automation = SeleniumAutomation(log_to_console)

    threading.Thread(target=selenium_automation.join_meet, args=(meet_url,), daemon=True).start()
    return jsonify({"message": "Deploying bot to Google Meet."})

@app.route('/play_youtube', methods=['POST'])
def play_youtube():
    global selenium_automation
    youtube_url = request.json.get('youtube_url')
    if not youtube_url:
        return jsonify({"error": "youtube_url is required"}), 400

    if not selenium_automation or not selenium_automation.driver:
        return jsonify({"error": "Bot is not deployed to a meeting yet."}), 400

    threading.Thread(target=selenium_automation.play_youtube_video, args=(youtube_url,), daemon=True).start()
    threading.Thread(target=selenium_automation.share_screen, daemon=True).start()
    return jsonify({"message": "Playing YouTube video."})

@app.route('/stop', methods=['POST'])
def stop():
    global selenium_automation
    if selenium_automation:
        threading.Thread(target=selenium_automation.stop_automation, daemon=True).start()
        selenium_automation = None
        return jsonify({"message": "Stopping automation and leaving the meeting."})
    else:
        return jsonify({"error": "Automation is not running."}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
