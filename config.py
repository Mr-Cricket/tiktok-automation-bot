# --- Bot Configuration ---

# Add your permanent Discord invite links here. The bot will pick one randomly.
DISCORD_LINKS = [
    "https://discord.gg/GNJbpRBPdV",
    "https://discord.gg/zDvcnaNWy3",
    "https://discord.gg/xwJZhvpn9Q",
    "https://discord.gg/DKSxQJPyfM",
    "https://discord.gg/dkkP7XuNTP",
    "https://discord.gg/occident"
]

# --- Comment Generation Engine ---
# The bot builds a unique ad by picking one phrase from each category.

AD_OPENERS = [
    "Slightly random question, but are you interested in",
    "For anyone watching this who is also into",
    "If you find this video interesting, you might also like",
    "Speaking of this topic, if you're into",
    "This reminds me, for anyone who enjoys",
    "Not to hijack, but if you're passionate about",
    "For the history & anthropology nerds in the comments:",
    "Quick question for everyone here, are you into",
    "Just curious, does anyone else here love",
    "If you're looking for more content on",
    "For those who want to go deeper into",
    "A bit off-topic, but if you're fascinated by",
]

CALL_TO_ACTIONS = [
    "European history and anthropology, we have a community for that.",
    "European genetics, culture, and politics, our server discusses it all.",
    "the deep history of Europe, we've got a great group for it.",
    "European history and culture, you should come say hi in our server.",
    "European genetics and linguistics, we talk about it constantly.",
    "European heritage and culture, we're always looking for more people.",
    "history, genetics, and anthropology, you'd probably fit right in with us.",
    "European culture and history, our Discord is the place to be.",
    "genetics, history, and politics, we have some great conversations.",
    "the cultural history of the continent, you should come join our community.",
    "topics like this, we're building a community you might enjoy.",
    "European history and current events, our server is active 24/7.",
    "anthropology and cultural studies, feel free to check out our group.",
]

EMOJIS = [
    "🤓", "🤯", "😮", "👍", "💯", "🔥", "🌍", "📜", "🧐", "➡️", "" # Added an empty string for no emoji
]


# The delay range (in seconds) to wait after a successful interaction.
DELAY_BETWEEN_ACTIONS = (2.5, 5.0)

# Set to True to run the browser in headless mode (no visible UI).
RUN_HEADLESS = False

# The name of the file where comment logs will be stored.
COMMENT_LOG_FILE = "tiktok_comments.txt"
