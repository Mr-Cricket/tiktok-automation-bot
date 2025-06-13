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
from config import AD_OPENERS, CALL_TO_ACTIONS, EMOJIS, DISCORD_LINKS, DELAY_BETWEEN_ACTIONS, RUN_HEADLESS, COMMENT_LOG_FILE

# Configure logging for better feedback
log_format = '%(asctime)s - [%(threadName)-25s] - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

class TikTokAutomator:
    """A class to automate interactions on TikTok's For You Page (FYP)."""

    def __init__(self, config, profile_dir, headless=False):
        """Initializes the TikTokAutomator."""
        self.config = config
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
        """Finds and clicks the 'For You' page button."""
        logging.info("Attempting to navigate to the For You page...")
        locators = [(By.XPATH, "//button[@aria-label='For You']"), (By.CSS_SELECTOR, "a[href='/foryou']")]
        for by, value in locators:
            try:
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
        like_button = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[1]')
        if like_button and "like video" in like_button.get_attribute('aria-label').lower():
            if self._safe_click(like_button, "like button"):
                return True
        logging.warning("Like button not found or click failed. Attempting double-tap...")
        video_player = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]//video', 5)
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
        """Logs the successful comment action to a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Account: {threading.current_thread().name} | Comment: \"{comment_text}\"\n"
        try:
            with comment_log_lock:
                with open(self.config['COMMENT_LOG_FILE'], "a", encoding="utf-8") as f:
                    f.write(log_entry)
            logging.info(f"Logged comment action.")
        except IOError as e:
            logging.error(f"Could not write to log file: {e}")

    def _check_if_comments_disabled(self, article_index):
        """Checks if the comment section for the current video is disabled."""
        logging.info("Checking if comments are disabled...")
        try:
            # TikTok often adds 'aria-disabled="true"' to the button or shows specific text.
            comment_button = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[2]', timeout=3)
            if comment_button and comment_button.get_attribute('aria-disabled') == 'true':
                logging.warning("Comments are disabled for this video (aria-disabled attribute found).")
                return True
            
            # Look for text like "Comments are turned off"
            disabled_text_element = self._safe_find_element(By.XPATH, "//*[contains(text(), 'Comments are turned off')]", timeout=1)
            if disabled_text_element:
                logging.warning("Comments are disabled for this video (text found).")
                return True
        except Exception as e:
            logging.error(f"Error while checking for disabled comments: {e}")
        logging.info("Comments appear to be enabled.")
        return False

    def _open_comment_sidebar(self, article_index):
        """Attempts to click the comment icon."""
        comment_icon = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[2]')
        if self._safe_click(comment_icon, "comment icon"):
            time.sleep(1.8)
            comment_panel = self._safe_find_element(By.XPATH, '//*[@id="main-content-homepage_hot"]/aside', 10)
            if comment_panel:
                logging.info("Comment panel opened.")
                return True
        logging.warning("Could not open comment sidebar.")
        return False

    def _process_comment_input_and_post(self):
        """Builds a random ad comment, types it like a human, and posts."""
        comment_area = self._safe_find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
        if not comment_area: return False
        self._safe_click(comment_area, "comment input area")
        time.sleep(0.5)

        # Build a highly randomized advertisement comment
        opener = random.choice(self.config['AD_OPENERS'])
        cta = random.choice(self.config['CALL_TO_ACTIONS'])
        emoji = random.choice(self.config['EMOJIS'])
        link = random.choice(self.config['DISCORD_LINKS'])
        full_comment = f"{opener} {cta} {link} {emoji}".strip()

        logging.info(f"Typing comment: '{full_comment}'")
        for char in full_comment:
            comment_area.send_keys(char)
            time.sleep(random.uniform(0.03, 0.09))
        time.sleep(0.7)

        post_button = self._safe_find_element(By.CSS_SELECTOR, '[data-e2e="comment-post"]')
        if self._safe_click(post_button, "comment post button"):
            self._log_comment_action(full_comment)
            logging.info("Comment posted successfully.")
            time.sleep(1.5)
            return True
        return False

    def _navigate_to_next_video(self, current_article_count):
        """Navigates to the next video and waits for it to load."""
        logging.info("Scrolling to next video...")
        
        def new_video_has_loaded(driver):
            new_count = len(driver.find_elements(By.XPATH, "//*[@id='column-list-container']/article"))
            return new_count > current_article_count

        scroll_methods = [
            lambda: self.driver.execute_script("window.scrollBy(0, window.innerHeight);"),
            lambda: self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        ]
        for i, scroll_method in enumerate(scroll_methods):
            try:
                logging.debug(f"Attempting scroll method #{i+1}...")
                scroll_method()
                # Reduced timeout for faster feel, but still robust.
                WebDriverWait(self.driver, 7).until(new_video_has_loaded)
                logging.info("New video loaded successfully.")
                return True
            except Exception as e:
                logging.warning(f"Scroll method #{i+1} failed or new video did not load in time: {e}")
        
        logging.error("All scroll methods failed.")
        return False

    def run(self, start_event):
        """Main automation loop."""
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
                
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="column-list-container"]/article[{article_num}]')))
                except TimeoutException:
                    logging.error("Timed out waiting for next video article to load. Stopping.")
                    break

                liked = self._like_current_video(article_index=article_num)
                if liked: time.sleep(random.uniform(0.5, 1))
                
                # Check for disabled comments before attempting to comment
                if self._check_if_comments_disabled(article_index=article_num):
                    logging.info("Skipping comment on this video.")
                else:
                    commented = False
                    if not self.is_comment_sidebar_open:
                        if self._open_comment_sidebar(article_num):
                            self.is_comment_sidebar_open = True
                            commented = self._process_comment_input_and_post()
                    else:
                        commented = self._process_comment_input_and_post()
                        if not commented: self.is_comment_sidebar_open = False
                
                if liked or ('commented' in locals() and commented):
                    time.sleep(random.uniform(*self.config['DELAY_BETWEEN_ACTIONS']))

                current_article_count = len(self.driver.find_elements(By.XPATH, "//*[@id='column-list-container']/article"))
                if not self._navigate_to_next_video(current_article_count):
                    break
                article_num += 1

        except Exception as e:
            logging.critical(f"An unrecoverable error occurred: {e}", exc_info=True)
        finally:
            self.close()

    def close(self):
        """Closes the browser."""
        if self.driver:
            logging.info("Closing browser.")
            self.driver.quit()

def start_bot_instance(config, profile_dir, headless, start_event):
    """Target function for each thread."""
    automator = TikTokAutomator(config, profile_dir, headless)
    automator.run(start_event)

comment_log_lock = threading.Lock()

if __name__ == "__main__":
    bot_config = {
        'AD_OPENERS': AD_OPENERS, 'CALL_TO_ACTIONS': CALL_TO_ACTIONS, 
        'EMOJIS': EMOJIS, 'DISCORD_LINKS': DISCORD_LINKS, 
        'DELAY_BETWEEN_ACTIONS': DELAY_BETWEEN_ACTIONS, 
        'COMMENT_LOG_FILE': COMMENT_LOG_FILE
    }

    while True:
        try:
            num_accounts = int(input("How many accounts do you want to run simultaneously? "))
            if num_accounts > 0: break
        except ValueError:
            print("Invalid input. Please enter a number.")

    threads = []
    start_bots_event = threading.Event()
    for i in range(num_accounts):
        account_name = f"Account-{i+1}"
        profile_path = os.path.join(os.getcwd(), "tiktok_profiles", f"profile_{i+1}")
        logging.info(f"Preparing to launch {account_name}...")
        thread = threading.Thread(
            target=start_bot_instance,
            name=account_name,
            args=(bot_config, profile_path, RUN_HEADLESS, start_bots_event)
        )
        threads.append(thread)
        thread.start()
        time.sleep(3)

    print("\n" + "="*80 + "\nAll browsers launched. Please log in to each account.\n" + "="*80)
    input("Once logged in to ALL accounts, press ENTER here to start all bots...")
    print("="*80 + "\n")
    
    start_bots_event.set()
    for thread in threads:
        thread.join()
