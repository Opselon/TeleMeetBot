import subprocess
import os

def run_service(service_name):
    """Run a service as a background process."""
    log_file = f"{service_name}.log"
    with open(log_file, "w") as f:
        process = subprocess.Popen(
            ["python", f"services/{service_name}/main.py"],
            stdout=f,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
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
