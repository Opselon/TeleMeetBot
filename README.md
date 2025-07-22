# TeleMeet Bot

A microservice-based Telegram Bot for Google Meet Screen Sharing, controlled via a web panel.

## How to install dependencies
```
pip install -r requirements.txt
```

## How to run the application
1. **Initialize the database:**
   ```
   python -c "from database import init_db; init_db()"
   ```
2. **Run the web panel:**
   ```
   python app.py
   ```
3. **Open your browser** and navigate to `http://localhost:5001`.

4. **Configure the bot:**
   - Enter your Telegram Bot Token and click "Save Token".
   - Click "Connect Bot" to start the Telegram bot.

5. **Control the bot via the web panel or Telegram commands:**
   - **Web Panel:** Use the forms to deploy the bot to a Meet call, play a YouTube video, or stop the automation.
   - **Telegram:**
     - `/meet <google_meet_link>`: Joins the specified Google Meet call.
     - `/play <youtube_link>`: Plays the YouTube video in the shared screen.
     - `/stop`: Stops the video, stops the screen share, and leaves the call.

## How to use Docker
1. **Build and run the container:**
   ```
   docker-compose up --build
   ```
2. **Access the web panel** at `http://localhost:5001`.
