# TeleMeet Bot

A microservice-based Telegram Bot for Google Meet Screen Sharing, controlled via a web panel.

## How to install dependencies
```
pip install -r requirements.txt
```

## How to run the application
1. **Run the main application:**
   ```
   python main.py
   ```
2. **If you are running the application for the first time, you will be prompted to enter your Telegram Bot Token.**
3. **All services (`web_panel`, `telegram_bot`, `selenium_automation`) will be started automatically.**

## How to use Docker
1. **Build and run the container:**
   ```
   docker-compose up --build
   ```
2. **Access the web panel** at `http://localhost:5001`.
