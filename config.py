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
    "Good to see people still talking about",
    "For those who know what's really going on with",
    "If you're tired of the mainstream narrative on",
    "Based take. If you're interested in",
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
    "real solutions for Europe's future, we're discussing them here.",
    "saving Europe, our community is a good place to start.",
    "preserving our heritage, we're organizing here.",
    "building a network of like-minded people, you know where to find us.",
    "the future of Europa, we're planning it here.",
    "traditional European values, we have a server for that.",
]

# EMOJI list updated with only the "safest" characters to prevent crashes.
EMOJIS = [
    "👍", "➡️", "😮", "💯", "" # Added an empty string for no emoji
]

# --- Humanizer Engine ---
# This engine makes the comments appear more authentic.

# Specific, intentional misspellings and slang.
HUMANIZER_TWEAKS = {
    "you": ["yuo", "you"], # Will sometimes replace "you" with "yuo"
    "sir": ["saar"],
    "bro": ["vro"],
    "Europe": ["Europa", "Europe"],
}

# Slang phrases that can be randomly added to the beginning or end of a comment.
SLANG_ADDITIONS = [
    "W server.",
    "Based server.",
    "Good community here.",
    "Finally, a good server.",
    "", # An empty string means sometimes no slang is added.
    "",
    ""
]


# The delay range (in seconds) to wait after a successful interaction.
# Fine-tuned for slightly faster performance.
DELAY_BETWEEN_ACTIONS = (2.0, 4.5)

# The name of the file where comment logs will be stored.
COMMENT_LOG_FILE = "tiktok_comments.txt"
