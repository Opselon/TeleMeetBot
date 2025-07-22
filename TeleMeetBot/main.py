import customtkinter as ctk
import threading
import configparser
from datetime import datetime
from telegram_bot import TelegramBot
from selenium_automation import SeleniumAutomation

class TeleMeetBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TeleMeet Bot Control Panel")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Column
        self.left_frame = ctk.CTkFrame(self, width=400)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_propagate(False)

        # Telegram Token Section
        self.token_label = ctk.CTkLabel(self.left_frame, text="Telegram Bot Token")
        self.token_label.pack(pady=5)
        self.token_entry = ctk.CTkEntry(self.left_frame, show="*")
        self.token_entry.pack(pady=5, padx=10, fill="x")
        self.connect_button = ctk.CTkButton(self.left_frame, text="Save & Connect", command=self.save_and_connect)
        self.connect_button.pack(pady=10)

        # Manual Control Section
        self.meet_url_label = ctk.CTkLabel(self.left_frame, text="Google Meet URL")
        self.meet_url_label.pack(pady=5)
        self.meet_url_entry = ctk.CTkEntry(self.left_frame)
        self.meet_url_entry.pack(pady=5, padx=10, fill="x")

        self.youtube_url_label = ctk.CTkLabel(self.left_frame, text="YouTube Video URL")
        self.youtube_url_label.pack(pady=5)
        self.youtube_url_entry = ctk.CTkEntry(self.left_frame)
        self.youtube_url_entry.pack(pady=5, padx=10, fill="x")

        self.deploy_button = ctk.CTkButton(self.left_frame, text="Deploy Bot to Meet", state="disabled", command=self.deploy_bot)
        self.deploy_button.pack(pady=10)
        self.play_button = ctk.CTkButton(self.left_frame, text="Play Video in Meet", state="disabled", command=self.play_video)
        self.play_button.pack(pady=10)
        self.stop_button = ctk.CTkButton(self.left_frame, text="Stop Bot & Leave Meet", command=self.stop_bot)
        self.stop_button.pack(pady=10)

        # Right Column
        self.right_frame = ctk.CTkFrame(self, width=400)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_propagate(False)

        self.log_box = ctk.CTkTextbox(self.right_frame, state="disabled", width=380, height=580)
        self.log_box.pack(padx=10, pady=10)

        self.automation = SeleniumAutomation(self.log)
        self.load_config()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] [{level}] {message}\n")
        self.log_box.configure(state="disabled")

    def save_and_connect(self):
        token = self.token_entry.get()
        if not token:
            self.log("Telegram token cannot be empty.", "ERROR")
            return

        config = configparser.ConfigParser()
        config["telegram"] = {"token": token}
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        self.log("Telegram token saved successfully.")

        self.connect_bot(token)

    def connect_bot(self, token):
        try:
            self.bot = TelegramBot(token, self, self.log)
            self.bot_thread = threading.Thread(target=self.bot.run, daemon=True)
            self.bot_thread.start()
            self.log("Telegram bot connected successfully.")
            self.deploy_button.configure(state="normal")
        except Exception as e:
            self.log(f"Failed to connect Telegram bot: {e}", "ERROR")

    def load_config(self):
        config = configparser.ConfigParser()
        if config.read("config.ini"):
            token = config.get("telegram", "token", fallback=None)
            if token:
                self.token_entry.insert(0, token)
                self.log("Loaded Telegram token from config.")
                self.connect_bot(token)

    def deploy_bot(self):
        meet_url = self.meet_url_entry.get()
        if not meet_url:
            self.log("Google Meet URL cannot be empty.", "ERROR")
            return

        threading.Thread(target=self._deploy_bot_thread, args=(meet_url,), daemon=True).start()

    def _deploy_bot_thread(self, meet_url):
        if self.automation.join_meet(meet_url):
            self.play_button.configure(state="normal")
        else:
            self.log("Failed to join the meeting.", "ERROR")

    def play_video(self):
        youtube_url = self.youtube_url_entry.get()
        if not youtube_url:
            self.log("YouTube Video URL cannot be empty.", "ERROR")
            return

        threading.Thread(target=self._play_video_thread, args=(youtube_url,), daemon=True).start()

    def _play_video_thread(self, youtube_url):
        self.automation.play_youtube_video(youtube_url)
        self.automation.share_screen()

    def stop_bot(self):
        threading.Thread(target=self.automation.stop_automation, daemon=True).start()
        self.play_button.configure(state="disabled")


if __name__ == "__main__":
    app = TeleMeetBotApp()
    app.mainloop()
