# 🤖 TikTok Automation Bot
A powerful, multi-account TikTok automation bot built with Python and Selenium. This bot is designed to automate interactions such as liking and commenting on videos in the "For You" feed, with support for running multiple accounts simultaneously.
## ✨ Features
* Multi-Account Management: Run multiple bot instances for different accounts at the same time.

* User-Friendly Menu: Choose between a visible "Setup Mode" for first-time logins and a background "Headless Mode" for normal runs.

* Automatic Login: Saves session data to automatically log in after the first manual login for each account.

* Concurrent Execution: Utilizes threading to run multiple browser instances in parallel.

* Advanced Comment Engine: Builds unique, human-like comments from a library of phrases to avoid spam detection.

* Smart Error Handling: Intelligently detects when comments are disabled on a video and skips it, preventing errors.

* Robust Navigation: Uses multiple scrolling methods and waits for new content to load, eliminating race conditions and allowing the bot to run reliably in the background.

## 📋 Prerequisites
Before you begin, ensure you have the following installed on your computer:

* [Python 3.8+](https://www.python.org/downloads/)

* [Git](https://git-scm.com/downloads)

* [Google Chrome](https://www.google.com/chrome/)

## 🚀 Setup & Installation
Follow these steps in your terminal (like Command Prompt on Windows) to get your bot up and running.

**1. Clone the Repository:**
   
First, you need to download the project files from GitHub. Run the following command. Make sure to replace `your-github-username` with your actual GitHub username.

> `git clone https://github.com/your-github-username/tiktok-automation-bot.git`

After the download is complete, navigate into the new project folder:

> `cd tiktok-automation-bot`

**2. Create a Virtual Environment (Recommended):**

It's best practice to create a virtual environment to keep project dependencies isolated. This prevents conflicts with other Python projects on your computer.

* On Windows:

`python -m venv venv`

`venv\Scripts\activate`

* On macOS & Linux:

`python3 -m venv venv`

`source venv/bin/activate`

**3. Install Required Packages:**

Install all the required Python packages from the `requirements.txt` file. This command reads the file and installs everything the bot needs to run, including a compatibility patch (`setuptools`) needed for newer versions of Python

> `pip install -r requirements.txt`

## ▶️ Usage
**1. Configure Your Settings:**

Before running the bot, you can customize its behavior by editing the `config.py` file. You can open this file with any text editor, like Notepad or VS Code. You will be able to change and adjust:

* `DISCORD_LINKS`: This is important! Replace the placeholder links with your own permanent Discord server invites. The bot will randomly pick from this list.

* `COMMENTS`: Add the comments you want the bot to post. It will choose one randomly for each video.

* `DELAY_BETWEEN_ACTIONS`: Set the min/max time (in seconds) the bot should wait after an interaction before moving to the next video.

* `RUN_HEADLESS`: Set to `True` to run the browsers in the background (no visible UI). Defaults to `False`.

## 2. Run the Bot and Choose a Mode:

Execute the `main.py` script from your terminal.

>`python main.py`

The script will now ask you to choose a run mode. Here is the recommended workflow:

* **For First-Time Setup**:

  1. Choose `1` for **Setup Mode**.

  2. Enter the number of accounts you want to set up (e.g., `3`).

  3. A visible browser window will open for each account. **Log in manually** to each one.

  4. Once all accounts are logged in, press Enter in the terminal to start the bots. You can let them run for a minute and then stop them with `Ctrl+C`. The login sessions are now saved.

* **For All Future Runs**:

  1. **Choose `2` for Headless Mode**.

  2. Enter the number of accounts you want to run.

  3. The bot will now use your saved logins and run completely invisibly in the background.

**3. Stopping the Bot:**

To stop all running bots, simply go to the terminal window where the script is running and press `Ctrl+C`.

## 🛠️ Troubleshooting
**Problem: `Permission Denied` Error During Installation**

If you see an error message like `OSError: [Errno 13] Permission denied` when running `pip install`, it means your command prompt doesn't have the necessary rights to save files.

Solution: Run as Administrator

**Close** your current Command Prompt window.

Go to your Windows Start Menu and type `cmd`.

**Right-click** on "Command Prompt" in the search results.

Select **"Run as administrator"**.

In the new administrator Command Prompt, navigate back to your project folder (`cd tiktok-automation-bot`), activate the virtual environment (`venv\Scripts\activate`), and then run the `pip install -r requirements.txt` command again. It will work this time.

## ⚖️ Disclaimer
This project is for educational purposes only. Automating user interactions can be against the terms of service of many platforms, including TikTok. Use this software responsibly and at your own risk. The developers of this project are not responsible for any account suspension or other consequences that may arise from its use. Don't be stupid cunts, you wankers. 
