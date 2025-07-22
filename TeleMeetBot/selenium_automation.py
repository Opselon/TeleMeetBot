import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumAutomation:
    def __init__(self, logger):
        self.logger = logger
        self.driver = None

    def start_driver(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_experimental_option("autoSelectDesktopCaptureSource", "YouTube")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger("Chrome driver started successfully.")
            return True
        except Exception as e:
            self.logger(f"Failed to start Chrome driver: {e}", "ERROR")
            return False

    def join_meet(self, meet_url):
        if not self.driver:
            self.start_driver()

        self.driver.get(meet_url)
        time.sleep(5) # Allow time for the page to load

        try:
            # Dismiss any initial pop-ups
            dismiss_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Dismiss')]"))
            )
            dismiss_button.click()
            self.logger("Dismissed initial pop-up.")
        except:
            self.logger("No dismiss button found, continuing...")

        try:
            # Enter a random name
            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Your name']"))
            )
            name_input.send_keys("ScreenShare Bot 742")
            self.logger("Entered a random name.")
        except:
            self.logger("Could not find name input field.", "WARN")

        try:
            # Join the meeting
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Ask to join')] | //button[contains(., 'Join now')]"))
            )
            join_button.click()
            self.logger("Successfully joined the meeting.")
            return True
        except Exception as e:
            self.logger(f"Could not join the meeting: {e}", "ERROR")
            return False

    def play_youtube_video(self, youtube_url):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(youtube_url)
        self.logger("Opened YouTube video in a new tab.")

        try:
            play_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Play (k)']"))
            )
            play_button.click()
            self.logger("Playing YouTube video.")
        except Exception as e:
            self.logger(f"Could not play YouTube video: {e}", "ERROR")

    def share_screen(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        try:
            present_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Present now')]"))
            )
            present_button.click()
            self.logger("Clicked 'Present now' button.")
        except Exception as e:
            self.logger(f"Could not find 'Present now' button: {e}", "ERROR")
            return

        try:
            tab_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'A Chrome tab')]"))
            )
            tab_option.click()
            self.logger("Selected 'A Chrome tab' for presentation.")
        except Exception as e:
            self.logger(f"Could not select 'A Chrome tab': {e}", "ERROR")

    def stop_automation(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger("Browser closed and automation stopped.")
