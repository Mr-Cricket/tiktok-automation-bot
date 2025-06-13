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

comment_log_lock = threading.Lock()
# Global event to signal all bot threads to stop their operations
stop_bots_event = threading.Event() 

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
        # Store the last known article index to re-click the comment icon
        self.last_article_index_for_comment = None 
        # Reference to the global stop event, set in the run method
        self.stop_event = None 

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
            # Scroll element into view before clicking to ensure visibility
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
        # Look for profile icon, common indicator of being logged in
        profile_icon = self._safe_find_element(By.CSS_SELECTOR, "[data-e2e='nav-avatar']", timeout)
        if profile_icon:
            logging.info("Login verified successfully (found profile avatar).")
            return True
        
        # Look for the 'Upload' button, another strong indicator of login
        upload_button = self._safe_find_element(By.XPATH, "//a[@href='/upload']", 5)
        if upload_button:
            logging.info("Login verified successfully (found 'Upload' button).")
            return True

        # New fallback for headless mode: Check for the 'Activity' button
        if self.headless:
            logging.info("In headless mode, checking for 'Activity' button as login indicator...")
            # Try XPath first
            activity_button_xpath = self._safe_find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div/div[3]/div[1]/div[2]/button/div/div[2]', timeout=5)
            if activity_button_xpath and activity_button_xpath.text == "Activity":
                logging.info("Login verified successfully (found 'Activity' button via XPath).")
                return True
            
            # If XPath fails, try CSS Selector
            activity_button_css = self._safe_find_element(By.CSS_SELECTOR, '#app > div.css-1yczxwx-DivBodyContainer.e1irlpdw0 > div > div > div.css-10pqo95-DivScrollingContentContainer.e1u58fka5 > div.css-5yxamm-DivMainNavContainer.ej7on1p4 > div:nth-child(6) > button > div > div.TUXButton-label', timeout=5)
            if activity_button_css and activity_button_css.text == "Activity":
                logging.info("Login verified successfully (found 'Activity' button via CSS Selector).")
                return True


        logging.error("Login verification failed. Neither profile avatar, upload button, nor activity button were found.")
        return False

    def _navigate_to_fyp(self):
        """Finds and clicks the 'For You' page button."""
        logging.info("Attempting to navigate to the For You page...")
        # Common locators for the 'For You' button
        locators = [(By.XPATH, "//button[@aria-label='For You']"), (By.CSS_SELECTOR, "a[href='/foryou']")]
        for by, value in locators:
            try:
                fyp_button = self._safe_find_element(by, value, timeout=5)
                if self._safe_click(fyp_button, "For You page button"):
                    logging.info("Successfully navigated to the For You page.")
                    time.sleep(2.5) # Allow page to load
                    return
            except Exception:
                continue
        logging.warning("Could not find FYP button. Assuming we are on the correct page.")

    def _like_current_video(self, article_index):
        """Attempts to like the currently visible video."""
        logging.info(f"Attempting to like video in article [{article_index}]...")
        # XPath for the like button within the current video's article element
        like_button = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[1]')
        if like_button and "like video" in like_button.get_attribute('aria-label').lower():
            if self._safe_click(like_button, "like button"):
                return True
        logging.warning("Like button not found or click failed. Attempting double-tap on video player...")
        # Fallback to double-tap on the video element itself
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
            # Use a lock to prevent race conditions when multiple threads write to the same file
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
            # Look for "sponsored" text (case-insensitive) or a data-e2e ad badge
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
            # Check for aria-disabled attribute on the comment button
            comment_button = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container']/article[{article_index}]/div/section[2]/button[2]', timeout=3)
            if comment_button and comment_button.get_attribute('aria-disabled') == 'true':
                logging.warning("Comments are disabled for this video (aria-disabled attribute found).")
                return True
            
            # Check for specific text indicating comments are turned off
            disabled_text_element = self._safe_find_element(By.XPATH, "//*[contains(text(), 'Comments are turned off')]", timeout=1)
            if disabled_text_element:
                logging.warning("Comments are disabled for this video (text found).")
                return True
        except Exception as e:
            logging.error(f"Error while checking for disabled comments: {e}")
        logging.info("Comments appear to be enabled.")
        return False

    def _open_comment_sidebar(self, article_index):
        """Attempts to click the comment icon to open the comment sidebar."""
        comment_icon = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{article_index}]/div/section[2]/button[2]')
        if self._safe_click(comment_icon, "comment icon"):
            time.sleep(1.8) # Wait for sidebar to animate open
            # Verify the comment panel is actually open
            comment_panel = self._safe_find_element(By.XPATH, '//*[@id="main-content-homepage_hot"]/aside', 10)
            if comment_panel:
                logging.info("Comment panel opened.")
                self.is_comment_sidebar_open = True
                self.last_article_index_for_comment = article_index # Store current article index for closing
                return True
        logging.warning("Could not open comment sidebar.")
        return False

    def _close_comment_sidebar(self):
        """Closes the comment sidebar if it's open by re-clicking the comment icon."""
        if not self.is_comment_sidebar_open:
            return # Sidebar is already closed
        
        if self.last_article_index_for_comment is None:
            logging.warning("Cannot close comment sidebar: last_article_index_for_comment is not set. Assuming it's closed.")
            self.is_comment_sidebar_open = False # Reset state to avoid getting stuck
            return

        logging.info(f"Attempting to close comment sidebar by re-clicking the comment icon for article [{self.last_article_index_for_comment}]...")
        try:
            # Re-find the comment icon using the stored article index
            comment_icon = self._safe_find_element(By.XPATH, f'//*[@id="column-list-container"]/article[{self.last_article_index_for_comment}]/div/section[2]/button[2]')
            if self._safe_click(comment_icon, "comment icon to close sidebar"):
                self.is_comment_sidebar_open = False
                self.last_article_index_for_comment = None # Clear the stored index after closing
                time.sleep(1) # Wait for animation
                logging.info("Comment sidebar closed successfully.")
                return True
        except Exception as e:
            logging.warning(f"Could not re-click comment icon to close sidebar: {e}. Assuming it's closed.")
            self.is_comment_sidebar_open = False # Assume it's closed to avoid getting stuck
        return False

    def _humanize_comment(self, text):
        """Applies misspellings and slang to a comment to make it appear more human."""
        words = text.split()
        new_words = []
        for word in words:
            clean_word = word.strip(".,!?;:").lower()
            # Apply humanizer tweaks (misspellings/alternatives)
            if clean_word in self.config['HUMANIZER_TWEAKS']:
                if random.random() < 0.4: # 40% chance to apply tweak
                    new_word = random.choice(self.config['HUMANIZER_TWEAKS'][clean_word])
                    if word and word[0].isupper(): # Preserve capitalization
                        new_word = new_word.capitalize()
                    new_words.append(new_word + word[len(clean_word):]) # Re-add original punctuation
                    continue
            
            # Apply 'u' to 'v' transformation for certain words
            if 'u' in clean_word and not clean_word.endswith('u') and len(clean_word) > 2:
                if random.random() < 0.15: # 15% chance
                    new_word = word.replace('u', 'v', 1).replace('U', 'V', 1)
                    new_words.append(new_word)
                    continue

            new_words.append(word) # Keep original word if no tweaks applied
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
        if not comment_area: 
            logging.error("Comment input area not found.")
            return False
        
        # Click the comment area to ensure it's active for input
        self._safe_click(comment_area, "comment input area")
        time.sleep(0.5)

        final_comment = ""
        # Try up to 10 times to generate a comment under the character limit
        for _ in range(10): 
            opener = random.choice(self.config['AD_OPENERS'])
            cta = random.choice(self.config['CALL_TO_ACTIONS'])
            link = random.choice(self.config['DISCORD_LINKS'])
            base_comment = f"{opener} {cta} {link}"
            
            humanized_comment = self._humanize_comment(base_comment)
            
            slang = random.choice(self.config['SLANG_ADDITIONS'])
            
            temp_comment = humanized_comment
            if slang: # Randomly prepend or append slang
                if random.random() < 0.5:
                    temp_comment = f"{slang} {temp_comment}"
                else:
                    temp_comment = f"{temp_comment} {slang}"
            
            final_comment = temp_comment.strip()

            if len(final_comment) <= 150: # TikTok comment limit is typically 150 characters
                break
        else: # If loop completes without breaking (no suitable comment found)
            logging.error("Could not generate a comment under 150 characters. Skipping.")
            return False

        logging.info(f"Typing comment: '{final_comment}'")
        try:
            # Type the comment character by character for human-like input
            for char in final_comment:
                comment_area.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
        except Exception as e:
            logging.error(f"Failed to type comment: {e}")
            return False

        time.sleep(0.5) # Small pause before clicking post
        post_button = self._safe_find_element(By.CSS_SELECTOR, '[data-e2e="comment-post"]')
        if self._safe_click(post_button, "comment post button"):
            self._log_comment_action(final_comment)
            logging.info("Comment posted successfully.")
            time.sleep(1.2) # Allow comment to register
            # Close the comment sidebar immediately after posting
            self._close_comment_sidebar() 
            return True
        return False

    def _navigate_to_next_video(self):
        """Navigates to the next video using the simple, reliable PAGE_DOWN method."""
        logging.info("Scrolling to next video...")
        try:
            # Simulate pressing PAGE_DOWN key on the body element
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            
            # Use a short loop with sleep and stop_event check for responsiveness
            delay_start = time.time()
            while time.time() - delay_start < random.uniform(2.5, 4.0):
                if self.stop_event.is_set():
                    logging.info(f"Stop signal received during navigation delay for {threading.current_thread().name}.")
                    return False # Indicate navigation was interrupted
                time.sleep(0.1) # Check every 100ms
            
            logging.info("Scrolled to next video.")
            return True
        except Exception as e:
            logging.error(f"Scrolling with PAGE_DOWN failed: {e}")
            return False


    def run(self, start_event, stop_event):
        """Main automation loop."""
        self.stop_event = stop_event # Assign the global stop event to this instance
        try:
            self._setup_driver()
            self.driver.get("https://www.tiktok.com")
            
            if self.headless:
                if not self._check_login_status():
                    logging.critical("Headless login failed for account %s. Please run in Setup Mode (Choice 1) to refresh your session.", threading.current_thread().name)
                    # If login fails in headless, this thread can exit.
                    return 
            
            logging.info("Browser opened. Waiting for the master 'go' signal from the main console...")
            start_event.wait() # Block until the main thread signals to start
            logging.info("Go signal received! Starting automation.")
            self._navigate_to_fyp()
            
            article_num = 1
            # Main loop for processing videos, continues until stop signal is received
            while not self.stop_event.is_set(): 
                logging.info(f"--- Processing video in article {article_num} ---")
                
                try:
                    # Wait for the current video article to load. Add stop check here.
                    if self.stop_event.is_set(): break
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="column-list-container"]/article[{article_num}]')))
                except TimeoutException:
                    logging.error("Timed out waiting for current video article to load. Stopping.")
                    break # Exit loop if a video doesn't load
                
                if self.stop_event.is_set(): break # Check stop signal after element presence

                if self._check_if_sponsored(article_index=article_num):
                    if not self._navigate_to_next_video():
                        break # Stop if navigation fails
                    article_num += 1
                    continue # Skip current video if it's an ad

                liked = self._like_current_video(article_index=article_num)
                if liked: 
                    # Use responsive sleep
                    delay_start = time.time()
                    while time.time() - delay_start < random.uniform(0.4, 0.8):
                        if self.stop_event.is_set(): break
                        time.sleep(0.05)
                
                if self.stop_event.is_set(): break

                if self._check_if_comments_disabled(article_index=article_num):
                    logging.info("Skipping comment on this video as comments are disabled.")
                else:
                    if self._open_comment_sidebar(article_num):
                        if self.stop_event.is_set(): break
                        self._process_comment_input_and_post()
                
                if self.stop_event.is_set(): break

                # Add delay only if a like happened or the comment sidebar was closed
                if liked or not self.is_comment_sidebar_open:
                    # Use responsive sleep for DELAY_BETWEEN_ACTIONS
                    delay_start = time.time()
                    min_delay, max_delay = self.config['DELAY_BETWEEN_ACTIONS']
                    while time.time() - delay_start < random.uniform(min_delay, max_delay):
                        if self.stop_event.is_set(): break
                        time.sleep(0.1) # Check every 100ms for stop signal
                
                if self.stop_event.is_set(): break # Final check before navigating

                if not self._navigate_to_next_video():
                    break # Stop if navigation fails
                article_num += 1

        except Exception as e:
            logging.critical(f"An unrecoverable error occurred in {threading.current_thread().name}: {e}", exc_info=True)
        finally:
            self.close() # Ensure browser is closed even if an error occurs

    def close(self):
        """Closes the browser."""
        if self.driver:
            logging.info(f"Closing browser for {threading.current_thread().name}.")
            try:
                self.driver.quit()
            except Exception:
                pass # Ignore errors that might occur during quit

def start_bot_instance(config, profile_dir, headless, start_event, stop_event):
    """Target function for each thread to run a TikTokAutomator instance."""
    automator = TikTokAutomator(config, profile_dir, headless)
    automator.run(start_event, stop_event) # Pass both events

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
            print("Invalid input. Please enter a number greater than 0.")

    threads = []
    start_bots_event = threading.Event()
    # Global stop_bots_event is defined at the top of the file

    for i in range(num_accounts):
        account_name = f"Account-{i+1}"
        profile_path = os.path.join(os.getcwd(), "tiktok_profiles", f"profile_{i+1}")
        logging.info(f"Preparing to launch {account_name}...")
        thread = threading.Thread(
            target=start_bot_instance,
            name=account_name,
            args=(bot_config, profile_path, run_headless, start_bots_event, stop_bots_event)
        )
        threads.append(thread)
        thread.start()
        time.sleep(3) # Give a small delay between launching browsers

    try:
        if not run_headless:
            print("\n" + "="*80 + "\nAll browsers launched. Please log in to each account.\n" + "="*80)
            input("Once logged in to ALL accounts, press ENTER here to start all bots...")
        else:
            print("\n" + "="*80 + "\nLaunching in Headless Mode. Press ENTER to start all bots.\n" + "="*80)
            input()
        
        start_bots_event.set() # Signal all bot threads to begin their automation tasks
        
        # Wait for all threads to complete, allowing for graceful shutdown via KeyboardInterrupt
        for thread in threads:
            # Use a timeout on join to allow the main thread to periodically check for KeyboardInterrupt
            while thread.is_alive():
                thread.join(timeout=1) 
                if stop_bots_event.is_set():
                    logging.info(f"Main thread breaking join loop for {thread.name} due to stop signal.")
                    break # Break from joining this specific thread if stop signal is received
            
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Initiating graceful shutdown for all bots...")
    finally:
        # Ensure all bots receive the stop signal, regardless of how the main loop exits
        stop_bots_event.set() 
        # Attempt to join all threads again to ensure they've had a chance to clean up
        for thread in threads:
            if thread.is_alive():
                logging.info(f"Attempting final join for thread {thread.name}...")
                thread.join(timeout=5) # Give threads a short grace period to terminate
                if thread.is_alive():
                    logging.warning(f"Thread {thread.name} did not terminate gracefully after timeout.")
        logging.info("All bots shut down successfully.")
