import subprocess
import sys
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
    if len(sys.argv) != 2:
        print("Usage: python main.py <service_name>")
        print("Available services: web_panel, telegram_bot, selenium_automation")
        return

    service = sys.argv[1]
    if service in ["web_panel", "telegram_bot", "selenium_automation"]:
        run_service(service)
    else:
        print(f"Unknown service: {service}")

if __name__ == "__main__":
    main()
