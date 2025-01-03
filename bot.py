import discord
import responses

# Import required constants
from hidden import TOKEN

# Asynchronous function to send message to channel / user
async def send_message(message, user_message, is_private):
    # Get the response if possible
    try:
        # Get the response
        is_file, response = responses.handle_response(user_message)
        # Send message based on is_private and is_file
        if is_private:
            if is_file:
                for resp in response:
                    if resp.split(".")[-1] == "png":
                        await message.author.send(file=discord.File(response))
                    else:
                        await message.author.send(response)
            else:
                await message.author.send(response)
        else:
            if is_file:
                for resp in response:
                    if resp.split(".")[-1] == "png":
                        await message.channel.send(file=discord.File(resp))
                    else:
                        await message.channel.send(resp)
            else:
                await message.channel.send(response)
    except Exception as error:
        print(error)

# Function to run the discord bot
def run_discord_bot():
    
    # Instantiate the client (no intents needed in discord.py 1.7.3)
    client = discord.Client()
    # Print message when bot is running
    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    # Whenever a message is sent
    @client.event
    async def on_message(message):
        
        # Prevent infinite loops by preventing bots responding to their own messages
        if message.author == client.user:
            return
        
        # Get basic information for debugging purposes
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} said: {user_message} in {channel}!")

        # Private message if user starts the message with a question-mark
        if user_message.startswith('?'):
            # Remove the question mark
            user_message = user_message[1:]
            await send_message(message, user_message, True)
        # Send a public message
        else:
            await send_message(message, user_message, False)

    # Run the client locally
    client.run(TOKEN)
