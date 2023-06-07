# Import the bot
import bot

# import platform
# import asyncio

# # Prevent RuntimeError: Event loop is closed
# if platform.system()=='Windows':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Run the bot
if __name__ == "__main__":
    bot.run_discord_bot()