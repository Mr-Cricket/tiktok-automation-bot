# --- Bot Configuration ---

# Add your permanent Discord invite links here. The bot will pick one randomly for each comment.
# Generate multiple permanent links from your Discord server to rotate them.
DISCORD_LINKS = [
    "discord.gg/occident",
    # "discord.gg/another-link",
    # "discord.gg/a-third-link"
    # Add as many as you want...
]

# Add a large variety of unique comments. The bot will randomly pick one, then add a random link from the list above.
COMMENTS = [
    "This is genuinely fascinating. If you're into European history, you should check out our community:",
    "Wow, learned something new today! We talk about stuff like this all the time in our server:",
    "Amazing content! For anyone interested in the deep history and genetics of Europe, we've got a great group here:",
    "This is the kind of history I love to see. We have a whole community dedicated to it:",
    "Incredible detail. Our server is all about European history and linguistics, come say hi!",
    "Love the focus on genetics here. We discuss this topic a lot:",
    "Super interesting! Anyone else a huge history nerd? You'd fit right in with us:",
    "This is right up my alley. If you're the same, you should join our Discord server:",
    "Great video! We're always looking for more people passionate about European heritage and history:",
    "Finally, some quality history content. Our server would love this:",
    "This is awesome! 🤓 Anyone who finds this interesting should definitely join us:",
    "My mind is blown. 🤯 For more on Euro history and genetics, check out:",
    "Yes! More of this please. We have a community for people who love this stuff:",
    "So cool. If you want to dive deeper into European history, our Discord is the place to be:",
    "This is exactly what I've been looking for. If you agree, come join the conversation:",
    "Brilliant. For fellow enthusiasts of European culture and history, you'll want to see this:",
    "Top-tier content. Our community discusses these topics 24/7:",
    "Absolutely captivating. If you're into genetics and the history of the continent, join us:",
    "This deserves more views! For those who want to learn more, we have a server:",
    "Excellent stuff! We're building a community around these exact topics:",
    "Love this! Our Discord server is a goldmine for info on European history:",
    "So well explained. If you're into the linguistic side of things too, you should join:",
    "This is why I love history. We've got a great community for people like us:",
    "Fantastic video! For more on the history of the European people, check this out:",
    "This is my favorite kind of content. We share stuff like this all the time in our server:",
    "Couldn't have said it better myself. For more on this, our Discord is active:",
    "You learn something new every day! Our server is all about this kind of knowledge:",
    "This is so important. We have a community that explores these topics in depth:",
    "Amazing! If you're passionate about the history of the continent, join our community:",
    "I'm hooked. For anyone else who is, here's a great place to learn more:",
    "This is just... wow. 😮 If you're into this, our Discord is a must-join:",
    "What a great explanation. We need more content like this! We discuss it here:",
    "This is epic. If you're interested in the genetic history of Europe, come join us:",
    "So fascinating! Our server is perfect for anyone who loves European history:",
    "This is the good stuff. For a deeper dive, check out our community:",
    "Really makes you think. We have some great discussions about this in our server:",
    "Love the scholarship here. For more academic-style discussions on this, join us:",
    "This is my jam! 🤘 For others who feel the same, here's where we hang out:",
    "Incredible. If you want to connect with other history buffs, here's the spot:",
    "This is so cool, I had to share the server where we talk about it:",
]

# The delay range (in seconds) to wait after a successful interaction (like/comment)
# This has been fine-tuned to be faster and more natural.
DELAY_BETWEEN_ACTIONS = (2.5, 5.0)

# Set to True to run the browser in headless mode (no visible UI).
# Recommended to keep as False for the first login to each account.
RUN_HEADLESS = False

# The name of the file where comment logs will be stored.
COMMENT_LOG_FILE = "tiktok_comments.txt"
