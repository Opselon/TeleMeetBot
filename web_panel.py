from flask import Flask, render_template, request, redirect, url_for, flash
import database
import threading
from selenium_automation import SeleniumAutomation
from telegram_bot import TelegramBot

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize Selenium and Telegram Bot so they can be controlled from the web panel
selenium_automation = None
telegram_bot = None
bot_thread = None

def log_to_web_console(message, level="INFO"):
    # In a real-world scenario, you'd use a more robust logging solution
    print(f"[{level}] {message}")

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
    global telegram_bot, bot_thread
    token = database.get_config('telegram_token')
    if not token:
        flash('Telegram token is not set.', 'danger')
        return redirect(url_for('index'))

    try:
        telegram_bot = TelegramBot(token, None, log_to_web_console) # App is None for now
        bot_thread = threading.Thread(target=telegram_bot.run, daemon=True)
        bot_thread.start()
        flash('Telegram bot connected successfully.', 'success')
    except Exception as e:
        flash(f'Failed to connect Telegram bot: {e}', 'danger')

    return redirect(url_for('index'))

@app.route('/deploy', methods=['POST'])
def deploy():
    global selenium_automation
    meet_url = request.form['meet_url']
    database.set_config('meet_url', meet_url)

    if not selenium_automation:
        selenium_automation = SeleniumAutomation(log_to_web_console)

    threading.Thread(target=selenium_automation.join_meet, args=(meet_url,), daemon=True).start()
    flash('Deploying bot to Google Meet.', 'info')
    return redirect(url_for('index'))

@app.route('/play', methods=['POST'])
def play():
    global selenium_automation
    youtube_url = request.form['youtube_url']
    database.set_config('youtube_url', youtube_url)

    if not selenium_automation or not selenium_automation.driver:
        flash('Bot is not deployed to a meeting yet.', 'danger')
        return redirect(url_for('index'))

    threading.Thread(target=selenium_automation.play_youtube_video, args=(youtube_url,), daemon=True).start()
    threading.Thread(target=selenium_automation.share_screen, daemon=True).start()
    flash('Playing YouTube video.', 'info')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    global selenium_automation
    if selenium_automation:
        threading.Thread(target=selenium_automation.stop_automation, daemon=True).start()
        selenium_automation = None
        flash('Stopping automation and leaving the meeting.', 'info')
    else:
        flash('Automation is not running.', 'warning')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
