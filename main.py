import time
import random
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)
import undetected_chromedriver as uc
import logging
from datetime import datetime
import os
from config import COMMENTS, DELAY_BETWEEN_ACTIONS, RUN_HEADLESS, COMMENT_LOG_FILE

# Configure logging for better feedback
# Use a custom format to include the thread name (account name)
log_format = '%(asctime)s - [%(threadName)-25s] - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

class TikTokAutomator:
    """
    A class to automate interactions on TikTok's For You Page (FYP).
    Each instance of this class will be controlled by a separate thread.
    """

    def __init__(self, comments, delay_range, profile_dir, comment_log_file, headless=False):
        """Initializes the TikTokAutomator."""
        self.comments = comments
        self.delay_range = delay_range
        self.comment_log_file = comment_log_file
        self.profile_dir = profile_dir
        self.headless = headless
        self.is_comment_sidebar_open = False
        self.driver = None
        self.wait = None

    def _setup_driver(self):
        """Initializes the WebDriver for this specific instance."""
        logging.info(f"Initializing Chrome driver with profile: {self.profile_dir}")
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_dir}")

        if self.headless:
            options.add_argument("--headless")
            logging.info("Running in headless mode.")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logging.info("Driver initialized.")

    def _safe_find_element(self, by, value, timeout=5):
        """Helper to safely find an element with explicit wait."""
        try:
            return self.wait.until(EC.visibility_of_element_located((by, value)))
        except (TimeoutException, NoSuchElementException):
            logging.warning(f"Element not found within {timeout}s: {by}={value}")
            return None

    def _safe_click(self, element, description="element"):
        """Helper to safely click an element."""
        if not element:
            logging.warning(f"Cannot click a non-existent element: {description}")
            return False
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.wait.until(EC.element_to_be_clickable(element)).click()
            logging.info(f"Successfully clicked {description}.")
            return True
        except Exception as e:
            logging.warning(f"Could not click {description}: {e}.")
            try:
                logging.debug(f"Attempting JavaScript click for {description}...")
                self.driver.execute_script("arguments[0].click();", element)
                logging.info(f"Successfully JavaScript-clicked {description}.")
                return True
            except Exception as js_e:
                logging.error(f"JavaScript click also failed for {description}: {js_e}")
                return False

    def _navigate_to_fyp(self):
        """Finds and clicks the 'For You' page button using multiple locators."""
        logging.info("Attempting to navigate to the For You page...")
        locators = [
            (By.XPATH, "//button[@aria-label='For You']"),
            (By.CSS_SELECTOR, "a[href='/foryou']"),
            (By.XPATH, "//p[text()='For You']/ancestor::a")
        ]
        
        for by, value in locators:
            try:
                logging.debug(f"Trying to find FYP button with: {by}={value}")
                fyp_button = self._safe_find_element(by, value, timeout=5)
                if self._safe_click(fyp_button, "For You page button"):
                    logging.info("Successfully navigated to the For You page.")
                    time.sleep(2.5)
                    return
            except Exception:
                continue
        
        logging.warning("Could not find FYP button. Assuming we are on the correct page.")

    def _like_current_video(self, article_index):
        """Attempts to like the currently visible video."""
        logging.info(f"Attempting to like video in article [{article_index}]...")
        like_button_xpath = f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[1]'
        like_button = self._safe_find_element(By.XPATH, like_button_xpath)
        
        if like_button and "like video" in like_button.get_attribute('aria-label').lower():
            if self._safe_click(like_button, f"like button for article {article_index}"):
                return True

        logging.warning("Like button not found or click failed. Attempting double-tap...")
        video_player_xpath = f'//*[@id="column-list-container"]/article[{article_index}]//video'
        video_player = self._safe_find_element(By.XPATH, video_player_xpath, 5)
        
        if video_player:
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).double_click(video_player).perform()
                logging.info("Video liked successfully via double-tap.")
                return True
            except Exception as e:
                logging.error(f"Failed to double-tap video player: {e}")
        return False

    def _log_comment_action(self, comment_text):
        """Logs the successful comment action to a file, with thread safety."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Account: {threading.current_thread().name} | Comment: \"{comment_text}\"\n"
        try:
            with comment_log_lock:
                with open(self.comment_log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            logging.info(f"Logged comment action.")
        except IOError as e:
            logging.error(f"Could not write to log file: {e}")

    def _open_comment_sidebar(self, article_index):
        """Attempts to click the comment icon."""
        comment_icon_xpath = f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[2]'
        comment_icon = self._safe_find_element(By.XPATH, comment_icon_xpath)
        if self._safe_click(comment_icon, "comment icon"):
            time.sleep(1.5)
            comment_panel = self._safe_find_element(By.XPATH, '//*[@id="main-content-homepage_hot"]/aside', 10)
            if comment_panel:
                logging.info("Comment panel opened.")
                return True
        logging.warning("Could not open comment sidebar.")
        return False

    def _process_comment_input_and_post(self):
        """Finds comment input, types, and posts."""
        comment_area = self._safe_find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
        if not comment_area:
            logging.warning("Comment input area not found.")
            return False
        
        self._safe_click(comment_area, "comment input area")
        time.sleep(0.5)

        comment = random.choice(self.comments)
        comment_area.send_keys(comment)
        time.sleep(0.5)

        post_button = self._safe_find_element(By.CSS_SELECTOR, '[data-e2e="comment-post"]')
        if self._safe_click(post_button, "comment post button"):
            self._log_comment_action(comment)
            time.sleep(1.2)
            return True
        return False

    def _navigate_to_next_video(self):
        """Navigates to the next video."""
        try:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(2.0, 3.5))
            return True
        except Exception as e:
            logging.error(f"An error occurred while navigating: {e}")
            return False

    def run(self, start_event):
        """Main function to run the automation infinitely for one instance."""
        try:
            self._setup_driver()
            self.driver.get("https://www.tiktok.com")
            
            logging.info("Browser opened. Waiting for login and Enter key press in console...")
            start_event.wait()
            logging.info("Go signal received! Starting automation.")

            self._navigate_to_fyp()
            
            article_num = 1
            while True:
                logging.info(f"--- Processing video in article {article_num} ---")
                time.sleep(random.uniform(0.8, 1.8))
                liked = self._like_current_video(article_num)
                if liked: time.sleep(random.uniform(0.5, 1))

                commented = False
                if not self.is_comment_sidebar_open:
                    if self._open_comment_sidebar(article_num):
                        self.is_comment_sidebar_open = True
                        commented = self._process_comment_input_and_post()
                else:
                    commented = self._process_comment_input_and_post()
                    if not commented:
                        self.is_comment_sidebar_open = False

                if liked or commented:
                    logging.info(f"Interaction complete. Waiting before next navigation...")
                    time.sleep(random.uniform(*self.delay_range))
                else:
                    logging.info(f"No interaction for this video.")

                if not self._navigate_to_next_video():
                    logging.error("Failed to navigate. Stopping this instance.")
                    break
                article_num += 1

        except Exception as e:
            logging.critical(f"An unrecoverable error occurred: {e}", exc_info=True)
        finally:
            self.close()

    def close(self):
        """Closes the browser for this instance."""
        if self.driver:
            logging.info("Closing browser.")
            self.driver.quit()

def start_bot_instance(comments, delay, profile_dir, log_file, headless, start_event):
    """Target function for each thread. Creates and runs a bot instance."""
    automator = TikTokAutomator(comments, delay, profile_dir, log_file, headless)
    automator.run(start_event)

# A lock to ensure only one thread writes to the log file at a time
comment_log_lock = threading.Lock()

if __name__ == "__main__":
    while True:
        try:
            num_accounts = int(input("How many accounts do you want to run simultaneously? "))
            if num_accounts > 0:
                break
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    threads = []
    start_bots_event = threading.Event()

    for i in range(num_accounts):
        account_name = f"Account-{i+1}"
        profile_path = os.path.join(os.getcwd(), "tiktok_profiles", f"profile_{i+1}")
        
        logging.info(f"Preparing to launch {account_name} with profile path: {profile_path}")

        thread = threading.Thread(
            target=start_bot_instance,
            name=account_name,
            args=(COMMENTS, DELAY_BETWEEN_ACTIONS, profile_path, COMMENT_LOG_FILE, RUN_HEADLESS, start_bots_event)
        )
        threads.append(thread)
        thread.start()
        time.sleep(3)

    print("\n" + "="*80)
    print(f"All {num_accounts} browser windows have been launched.")
    print("Please log in to each TikTok account in its respective window.")
    input("Once you have logged in to ALL accounts, press ENTER here to start all bots...")
    print("="*80 + "\n")
    
    start_bots_event.set()

    for thread in threads:
        thread.join()

