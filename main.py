import subprocess
import os
import sys

def run_service(service_name):
    """Run a service as a background process."""
    log_file = f"{service_name}.log"
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    with open(log_file, "w") as f:
        process = subprocess.Popen(
            ["python", f"services/{service_name}/main.py"],
            stdout=f,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
            preexec_fn=None if sys.platform == "win32" else os.setsid
        )
    print(f"Service '{service_name}' started with PID {process.pid}. Log file: {log_file}")

def main():
    """Main function to control the services."""
    if not os.path.exists(".env"):
        telegram_token = input("Please enter your Telegram Bot Token: ")
        with open(".env", "w") as f:
            f.write(f"TELEGRAM_TOKEN={telegram_token}")
        print("Telegram Bot Token saved to .env file.")

    services = ["web_panel", "telegram_bot", "selenium_automation"]
    for service in services:
        run_service(service)

if __name__ == "__main__":
    main()
