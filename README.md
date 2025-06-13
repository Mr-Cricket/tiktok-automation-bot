# 🤖 TikTok Automation Bot
A powerful, multi-account TikTok automation bot built with Python and Selenium. This bot is designed to automate interactions such as liking and commenting on videos in the "For You" feed, with support for running multiple accounts simultaneously.
## ✨ Features
* Multi-Account Management: Run multiple bot instances for different accounts at the same time.

* Automatic Login: Saves session data to automatically log in after the first manual login for each account.

* Concurrent Execution: Utilizes threading to run multiple browser instances in parallel.

* Dynamic & Robust: Uses a dynamic article-finding model to reliably navigate the FYP and avoid common errors.

* Smart Interaction: Can like videos and post from a predefined list of comments.

* Error Handling: Includes robust error handling and fallbacks (e.g., double-tap to like if the button fails).

* Easy Configuration: All user settings are centralized in a config.py file.

* Action Logging: Keeps a detailed tiktok_comments.txt log of all comments posted.
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

**2. Run the Bot:**

Execute the `main.py` script from your terminal.

> `python main.py`

**3. First-Time Login:**

* The script will first ask you how many accounts you want to run.

* It will then launch a separate Chrome window for each account.

* **You must manually log in to each TikTok account in its respective browser window.**

* Once all accounts are logged in, go back to the terminal and press `Enter` to start all the bots.

**4. Stopping the Bot:**

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
