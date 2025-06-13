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
    ElementNotInteractableException,
    WebDriverException,
    InvalidSessionIdException
)
import undetected_chromedriver as uc
import logging
from datetime import datetime
import os
from config import AD_OPENERS, CALL_TO_ACTIONS, DISCORD_LINKS, HUMANIZER_TWEAKS, SLANG_ADDITIONS, DELAY_BETWEEN_ACTIONS, COMMENT_LOG_FILE

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
            logging.debug(f"Element not found within {timeout}s: {by}={value}")
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

    def _check_login_status(self, timeout=15):
        """Checks if the user is logged in by looking for multiple indicators."""
        logging.info("Verifying login status...")
        profile_icon = self._safe_find_element(By.CSS_SELECTOR, "[data-e2e='nav-avatar']", timeout)
        if profile_icon:
            logging.info("Login verified successfully (found profile avatar).")
            return True
        
        upload_button = self._safe_find_element(By.XPATH, "//a[@href='/upload']", 5)
        if upload_button:
            logging.info("Login verified successfully (found 'Upload' button).")
            return True

        logging.error("Login verification failed. Neither profile avatar nor upload button were found.")
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

    def _check_if_sponsored(self, article_index):
        """Checks if the current video is a sponsored post or ad."""
        logging.info("Checking if video is sponsored...")
        try:
            sponsored_xpath = f"//*[@id='column-list-container']/article[{article_index}]//*[contains(translate(., 'SPONRED', 'sponred'), 'sponsored') or @data-e2e='ad-badge']"
            ad_element = self._safe_find_element(By.XPATH, sponsored_xpath, timeout=1)
            if ad_element:
                logging.warning("Sponsored video/ad detected. Skipping.")
                return True
        except Exception as e:
            logging.error(f"Error while checking for sponsored video: {e}")
        logging.info("Video is not an ad.")
        return False

    def _check_if_comments_disabled(self, article_index):
        """Checks if the comment section for the current video is disabled."""
        logging.info("Checking if comments are disabled...")
        try:
            comment_button = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[2]', timeout=3)
            if comment_button and comment_button.get_attribute('aria-disabled') == 'true':
                logging.warning("Comments are disabled for this video (aria-disabled attribute found).")
                return True
            
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
                self.is_comment_sidebar_open = True
                return True
        logging.warning("Could not open comment sidebar.")
        return False

    def _close_comment_sidebar(self):
        """Closes the comment sidebar if it's open."""
        if not self.is_comment_sidebar_open:
            return
        logging.info("Attempting to close comment sidebar...")
        try:
            close_button = self._safe_find_element(By.XPATH, "//button[@aria-label='Close']", timeout=3)
            if self._safe_click(close_button, "comment sidebar close button"):
                self.is_comment_sidebar_open = False
                time.sleep(1) # Wait for animation
        except Exception as e:
            logging.warning(f"Could not close comment sidebar, it might close on its own: {e}")
            self.is_comment_sidebar_open = False # Assume it's closed to avoid getting stuck

    def _humanize_comment(self, text):
        """Applies misspellings and slang to a comment to make it appear more human."""
        words = text.split()
        new_words = []
        for word in words:
            clean_word = word.strip(".,!?;:").lower()
            if clean_word in self.config['HUMANIZER_TWEAKS']:
                if random.random() < 0.4:
                    new_word = random.choice(self.config['HUMANIZER_TWEAKS'][clean_word])
                    if word and word[0].isupper():
                        new_word = new_word.capitalize()
                    new_words.append(new_word + word[len(clean_word):])
                    continue
            
            if 'u' in clean_word and not clean_word.endswith('u') and len(clean_word) > 2:
                if random.random() < 0.15:
                    new_word = word.replace('u', 'v', 1).replace('U', 'V', 1)
                    new_words.append(new_word)
                    continue

            new_words.append(word)
        return " ".join(new_words)

    def _process_comment_input_and_post(self):
        """Builds, validates, and posts a random comment."""
        try:
            logging.debug("Sending ESCAPE key to dismiss potential overlays.")
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except Exception as e:
            logging.warning(f"Could not send ESCAPE key (this is often okay): {e}")

        comment_area = self._safe_find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
        if not comment_area: return False
        self._safe_click(comment_area, "comment input area")
        time.sleep(0.5)

        final_comment = ""
        for _ in range(10): 
            opener = random.choice(self.config['AD_OPENERS'])
            cta = random.choice(self.config['CALL_TO_ACTIONS'])
            link = random.choice(self.config['DISCORD_LINKS'])
            base_comment = f"{opener} {cta} {link}"
            
            humanized_comment = self._humanize_comment(base_comment)
            
            slang = random.choice(self.config['SLANG_ADDITIONS'])
            
            temp_comment = humanized_comment
            if slang:
                if random.random() < 0.5:
                    temp_comment = f"{slang} {temp_comment}"
                else:
                    temp_comment = f"{temp_comment} {slang}"
            
            final_comment = temp_comment.strip()

            if len(final_comment) <= 150:
                break
        else:
            logging.error("Could not generate a comment under 150 characters. Skipping.")
            return False

        logging.info(f"Typing comment: '{final_comment}'")
        try:
            for char in final_comment:
                comment_area.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
        except Exception as e:
            logging.error(f"Failed to type comment: {e}")
            return False

        time.sleep(0.5)
        post_button = self._safe_find_element(By.CSS_SELECTOR, '[data-e2e="comment-post"]')
        if self._safe_click(post_button, "comment post button"):
            self._log_comment_action(final_comment)
            logging.info("Comment posted successfully.")
            time.sleep(1.2)
            self._close_comment_sidebar()
            return True
        return False

    def _navigate_to_next_video(self):
        """Navigates to the next video using the simple, reliable PAGE_DOWN method."""
        logging.info("Scrolling to next video...")
        try:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(2.5, 4.0)) # A static pause to allow content to load
            logging.info("Scrolled to next video.")
            return True
        except Exception as e:
            logging.error(f"Scrolling with PAGE_DOWN failed: {e}")
            return False


    def run(self, start_event):
        """Main automation loop."""
        try:
            self._setup_driver()
            self.driver.get("https://www.tiktok.com")
            
            if self.headless:
                if not self._check_login_status():
                    logging.critical("Headless login failed. Please run in Setup Mode (Choice 1) to refresh your session.")
                    return
            
            logging.info("Browser opened. Waiting for the master 'go' signal from the main console...")
            start_event.wait()
            logging.info("Go signal received! Starting automation.")
            self._navigate_to_fyp()
            
            article_num = 1
            while True:
                logging.info(f"--- Processing video in article {article_num} ---")
                
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="column-list-container"]/article[{article_num}]')))
                except TimeoutException:
                    logging.error("Timed out waiting for current video article to load. Stopping.")
                    break

                if self._check_if_sponsored(article_index=article_num):
                    if not self._navigate_to_next_video():
                        break
                    article_num += 1
                    continue

                liked = self._like_current_video(article_index=article_num)
                if liked: time.sleep(random.uniform(0.4, 0.8))
                
                if self._check_if_comments_disabled(article_index=article_num):
                    logging.info("Skipping comment on this video.")
                else:
                    if self._open_comment_sidebar(article_num):
                        self._process_comment_input_and_post()
                
                if liked or not self.is_comment_sidebar_open:
                    time.sleep(random.uniform(*self.config['DELAY_BETWEEN_ACTIONS']))
                
                if not self._navigate_to_next_video():
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
            try:
                self.driver.quit()
            except Exception:
                pass # Ignore errors on quit

def start_bot_instance(config, profile_dir, headless, start_event):
    """Target function for each thread."""
    automator = TikTokAutomator(config, profile_dir, headless)
    automator.run(start_event)

comment_log_lock = threading.Lock()

if __name__ == "__main__":
    bot_config = {
        'AD_OPENERS': AD_OPENERS, 'CALL_TO_ACTIONS': CALL_TO_ACTIONS, 
        'DISCORD_LINKS': DISCORD_LINKS, 
        'HUMANIZER_TWEAKS': HUMANIZER_TWEAKS,
        'SLANG_ADDITIONS': SLANG_ADDITIONS,
        'DELAY_BETWEEN_ACTIONS': DELAY_BETWEEN_ACTIONS, 
        'COMMENT_LOG_FILE': COMMENT_LOG_FILE
    }

    print("--- TikTok Automation Bot ---")
    print("Select a run mode:")
    print("  1. Setup Mode (Show browser windows for first-time login)")
    print("  2. Headless Mode (Run in background with saved logins)")
    
    run_headless = False
    while True:
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1': break
        elif choice == '2':
            run_headless = True
            break
        else: print("Invalid choice.")

    while True:
        try:
            num_accounts = int(input("How many accounts do you want to run simultaneously? "))
            if num_accounts > 0: break
        except ValueError:
            print("Invalid input.")

    threads = []
    start_bots_event = threading.Event()
    for i in range(num_accounts):
        account_name = f"Account-{i+1}"
        profile_path = os.path.join(os.getcwd(), "tiktok_profiles", f"profile_{i+1}")
        logging.info(f"Preparing to launch {account_name}...")
        thread = threading.Thread(
            target=start_bot_instance,
            name=account_name,
            args=(bot_config, profile_path, run_headless, start_bots_event)
        )
        threads.append(thread)
        thread.start()
        time.sleep(3)
    
    if not run_headless:
        print("\n" + "="*80 + "\nAll browsers launched. Please log in to each account.\n" + "="*80)
        input("Once logged in to ALL accounts, press ENTER here to start all bots...")
    else:
        print("\n" + "="*80 + "\nLaunching in Headless Mode. Press ENTER to start all bots.\n" + "="*80)
        input()

    start_bots_event.set()
    for thread in threads:
        thread.join()
