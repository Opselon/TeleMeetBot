from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import database

app = Flask(__name__)
app.secret_key = 'supersecretkey'

TELEGRAM_BOT_API_URL = "http://telegram_bot:5002"
SELENIUM_AUTOMATION_API_URL = "http://selenium_automation:5003"

@app.route('/')
def index():
    telegram_token = database.get_config('telegram_token')
    meet_url = database.get_config('meet_url')
    youtube_url = database.get_config('youtube_url')
    return render_template('index.html', telegram_token=telegram_token, meet_url=meet_url, youtube_url=youtube_url)

@app.route('/save_token', methods=['POST'])
def save_token():
    token = request.form['token']
    database.set_config('telegram_token', token)
    flash('Telegram token saved successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/connect_bot', methods=['POST'])
def connect_bot():
    response = requests.post(f"{TELEGRAM_BOT_API_URL}/start")
    if response.status_code == 200:
        flash('Telegram bot connected successfully.', 'success')
    else:
        flash(f'Failed to connect Telegram bot: {response.text}', 'danger')
    return redirect(url_for('index'))

@app.route('/deploy', methods=['POST'])
def deploy():
    meet_url = request.form['meet_url']
    database.set_config('meet_url', meet_url)
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/join_meet", json={"meet_url": meet_url})
    if response.status_code == 200:
        flash('Deploying bot to Google Meet.', 'info')
    else:
        flash(f'Failed to deploy bot: {response.text}', 'danger')
    return redirect(url_for('index'))

@app.route('/play', methods=['POST'])
def play():
    youtube_url = request.form['youtube_url']
    database.set_config('youtube_url', youtube_url)
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/play_youtube", json={"youtube_url": youtube_url})
    if response.status_code == 200:
        flash('Playing YouTube video.', 'info')
    else:
        flash(f'Failed to play video: {response.text}', 'danger')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    response = requests.post(f"{SELENIUM_AUTOMATION_API_URL}/stop")
    if response.status_code == 200:
        flash('Stopping automation and leaving the meeting.', 'info')
    else:
        flash(f'Failed to stop automation: {response.text}', 'danger')
    return redirect(url_for('index'))

@app.route('/status')
def status():
    try:
        telegram_response = requests.get(f"{TELEGRAM_BOT_API_URL}/status")
        telegram_status = telegram_response.json().get('status', 'offline')
    except requests.exceptions.RequestException:
        telegram_status = 'offline'

    try:
        selenium_response = requests.get(f"{SELENIUM_AUTOMATION_API_URL}/status")
        selenium_status = selenium_response.json().get('status', 'offline')
    except requests.exceptions.RequestException:
        selenium_status = 'offline'

    return jsonify({
        'telegram_bot': telegram_status,
        'selenium_automation': selenium_status
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
