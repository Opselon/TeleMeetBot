# TeleMeet Bot

A microservice-based Telegram Bot for Google Meet Screen Sharing, controlled via a web panel.

## How to install dependencies
```
pip install -r requirements.txt
```

## How to run the application
1. **Run the desired service:**
   ```
   python main.py <service_name>
   ```
   Replace `<service_name>` with one of the following: `web_panel`, `telegram_bot`, `selenium_automation`.

## How to use Docker
1. **Build and run the container:**
   ```
   docker-compose up --build
   ```
2. **Access the web panel** at `http://localhost:5001`.
