from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SeleniumAutomation:
    def __init__(self, logger):
        self.driver = None
        self.logger = logger

    def start_driver(self):
        self.logger.info("Starting Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Chrome driver started successfully.")
            return True
        except Exception as e:
            self.logger.error("Error starting Chrome driver", error=e)
            return False

    def join_meet(self, meet_link):
        self.logger.info("Joining Google Meet", meet_link=meet_link)
        try:
            self.driver.get(meet_link)
            time.sleep(5)  # Wait for the page to load
            # Dismiss the "welcome" popup
            try:
                dismiss_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Dismiss')]")
                dismiss_button.click()
                self.logger.info("Dismissed the welcome popup.")
            except:
                pass # no popup
            # Turn off microphone and camera
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div/div/div').click()
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div/div').click()
            self.logger.info("Turned off microphone and camera.")
            # Join the meeting
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/span').click()
            self.logger.info("Joined the meeting.")
            return True
        except Exception as e:
            self.logger.error("Error joining Google Meet", error=e)
            return False

    def play_youtube_video(self, youtube_link):
        self.logger.info("Playing YouTube video", youtube_link=youtube_link)
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(youtube_link)
            self.logger.info("YouTube video started.")
        except Exception as e:
            self.logger.error("Error playing YouTube video", error=e)

    def share_screen(self):
        self.logger.info("Sharing screen.")
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.find_element(By.XPATH, '//*[@id="ow3"]/div[1]/div/div[8]/div[3]/div[9]/div[2]/div[2]/div/div[1]/div[1]').click()
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/div[3]/div/div[2]/div/div[3]/div/span/span').click()
            self.logger.info("Screen shared successfully.")
        except Exception as e:
            self.logger.error("Error sharing screen", error=e)

    def mute_microphone(self):
        self.logger.info("Muting microphone.")
        try:
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div/div/div').click()
            self.logger.info("Microphone muted successfully.")
        except Exception as e:
            self.logger.error("Error muting microphone", error=e)

    def unmute_microphone(self):
        self.logger.info("Unmuting microphone.")
        try:
            self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div/div/div').click()
            self.logger.info("Microphone unmuted successfully.")
        except Exception as e:
            self.logger.error("Error unmuting microphone", error=e)

    def stop_automation(self):
        if self.driver:
            self.logger.info("Stopping automation and closing the browser.")
            self.driver.quit()
            self.driver = None
