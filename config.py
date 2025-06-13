# --- Bot Configuration ---

# Add the comments you want the bot to post. It will choose one randomly.
COMMENTS = [
    "Are you interested in history of the European continent and the genetics of the people that inhabited today and before? Then you should join our server! discord.gg/occident",
    "Are you interested in European genetics and linguistics and the history of the continent? Then you should join this server! discord.gg/occident"
]

# The delay range (in seconds) to wait after a successful interaction (like/comment)
# before moving to the next video. A random value between these two will be chosen.
DELAY_BETWEEN_ACTIONS = (1.5, 3.5)

# Set to True to run the browser in headless mode (no visible UI).
# Recommended to keep as False for the first login to each account.
RUN_HEADLESS = False

# The name of the file where comment logs will be stored.
COMMENT_LOG_FILE = "tiktok_comments.txt"
