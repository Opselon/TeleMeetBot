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

            # The following option is removed as it's not reliable and
            # requires specific setup. Manual selection of the tab to share is better.
            # chrome_options.add_experimental_option("autoSelectDesktopCaptureSource", "YouTube")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger("Chrome driver started successfully.")
            return True
        except Exception as e:
            self.logger(f"Failed to start Chrome driver: {e}", "ERROR")
            return False

    def join_meet(self, meet_url):
        if not self.driver:
            if not self.start_driver():
                return False

        self.driver.get(meet_url)
        time.sleep(5) # Allow time for the page to load

        try:
            # Click "Join now" or "Ask to join"
            join_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Ask to join')] | //button[contains(., 'Join now')]"))
            )
            join_button.click()
            self.logger("Successfully joined the meeting.")
            return True
        except Exception as e:
            self.logger(f"Could not join the meeting: {e}", "ERROR")
            # Try to dismiss any pop-ups that might be in the way
            try:
                self.driver.find_element(By.XPATH, "//button[contains(text(), 'Dismiss')]").click()
                time.sleep(2)
                join_button.click()
                self.logger("Successfully joined the meeting after dismissing a pop-up.")
                return True
            except:
                pass # Already logged the main error
            return False

    def play_youtube_video(self, youtube_url):
        if not self.driver:
            self.logger("Driver not started. Cannot play video.", "ERROR")
            return

        # Open YouTube in a new tab
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(youtube_url)
        self.logger(f"Opened YouTube video in a new tab: {youtube_url}")

        # Wait for the video to load and play it
        try:
            play_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button"))
            )
            play_button.click()
            self.logger("Playing YouTube video.")
        except Exception as e:
            self.logger(f"Could not play YouTube video: {e}", "ERROR")

    def share_screen(self):
        if not self.driver:
            self.logger("Driver not started. Cannot share screen.", "ERROR")
            return

        self.driver.switch_to.window(self.driver.window_handles[0]) # Switch back to Meet tab

        try:
            present_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Present now')]"))
            )
            present_button.click()
            self.logger("Clicked 'Present now' button.")
        except Exception as e:
            self.logger(f"Could not find 'Present now' button: {e}", "ERROR")
            return

        try:
            # Select "A Chrome tab" for sharing
            tab_option = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'A Chrome tab')] | //div[contains(text(), 'Chrome Tab')]"))
            )
            tab_option.click()
            self.logger("Selected 'A Chrome tab' for presentation.")
            # Manual selection of the tab is required by the user at this point
        except Exception as e:
            self.logger(f"Could not select 'A Chrome tab': {e}", "ERROR")

    def stop_automation(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger("Browser closed and automation stopped.")
