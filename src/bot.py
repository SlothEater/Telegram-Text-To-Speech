import telegram
from telegram.ext import Updater, CommandHandler
import os
from encryption import encrypt_key, decrypt_key
from openai_client import  set_openai_api_key, generate_chat_response
from sound_conversion import set_elevenlabs_api_key, convert_to_sound, query_voices
import logging

# Retrieve the telegram token from the environment variable. Set in the
# Dockerfile
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# For testing uncomment the following line and set the telegram token as needed.
# TELEGRAM_TOKEN = ''

# Telegram bot initialization
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Available commands and their descriptions
COMMANDS = {
    "/start":
    "Start the bot and receive a welcome message",
    "/query {your query}":
    "Process your query and generate a response",
    "/openai {OPENAI-API-KEY}":
    "Set your OpenAI API key",
    "/elevenlabs {ELEVEN-LABS-API-KEY}":
    "Set your ElevenLabs API key",
    "/help or /commands":
    "Show the available commands and their descriptions",
    "/voices":
    "Get a list of available voices from ElevenLabs to choose from",
    "/set_voice {name or -id ID}":
    "Set the voice ID for generating the response. Use the `-id` flag followed by the ID if you want to use an ID instead of the voice name."
}

# Store API keys per user
api_keys = {}


def start(update, context):
    """
    Handle the /start command.
    Send a welcome message to the user.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=
        "Bot is ready. Send your query using /query command or use /help to see available commands."
    )


def query(update, context):
    """
    Handle the /query command.
    Process user's query and generate a response.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    chat_id = update.effective_chat.id
    query_text = update.message.text[7:]  # Remove '/query ' from the message

    user_api_keys = api_keys.get(chat_id)
    if not user_api_keys:
        context.bot.send_message(
            chat_id=chat_id,
            text=
            "API keys are not configured. Please use /openai {API-KEY} and /elevenlabs {API-KEY} commands to set the API keys."
        )
        return

    openai_key = decrypt_key(user_api_keys.get("openai"))
    elevenlabs_key = decrypt_key(user_api_keys.get("elevenlabs"))

    if not openai_key:
        context.bot.send_message(
            chat_id=chat_id,
            text=
            "OpenAI API key is not configured. Please use /openai {API-KEY} command to set the API key."
        )
        return

    if not elevenlabs_key:
        context.bot.send_message(
            chat_id=chat_id,
            text=
            "ElevenLabs API key is not configured. Please use /elevenlabs {API-KEY} command to set the API key."
        )
        return

    set_openai_api_key(openai_key)
    set_elevenlabs_api_key(elevenlabs_key)

    response = generate_chat_response(query_text)

    if response:
        if "voiceid" in user_api_keys:
            voice_id = user_api_keys["voiceid"]
            sound_file = convert_to_sound(response, voice_id)
        else:
            sound_file = convert_to_sound(response)
        send_sound_file(chat_id, sound_file, response)
    else:
        logging.info(
            f'System crashed with the following response:\n```{response}```')
        context.bot.send_message(
            chat_id=chat_id,
            text=
            "An error occurred while processing your query. Please try again.")


def send_sound_file(chat_id, sound_file, response):
    """
    Send the generated sound file to the user.

    Parameters:
        chat_id (int): The chat ID of the user.
        sound_file (file): The sound file to send.
        response (str): The response message associated with the sound file.
    """
    if sound_file:
        filename = generate_filename(response)
        bot.send_audio(chat_id=chat_id,
                       audio=sound_file,
                       filename=filename.replace(" ", "_"))
    else:
        bot.send_message(
            chat_id=chat_id,
            text=
            "An error occurred while processing your query. Please try again.")


def generate_filename(response) -> str:
    """
    Generate a filename for the sound file.

    Parameters:
        response (str): The response message.

    Returns:
        str: The generated filename.
    """
    response = f'Can you give me a short but meaningful name (do not add a file extension please) for a file with the following text contents: {response}'
    generated_filename = generate_chat_response(response)
    filename = generated_filename + ".mp3"
    return filename


def set_api_key(update, context):
    """
    Set the API key for a specific service.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    chat_id = update.effective_chat.id
    command, api_key = update.message.text.split(maxsplit=1)
    api_key_type = command[1:]

    if api_key_type == "openai":
        api_keys.setdefault(chat_id, {})["openai"] = encrypt_key(api_key)
        context.bot.send_message(
            chat_id=chat_id,
            text="OpenAI API key has been configured successfully.")
    elif api_key_type == "elevenlabs":
        api_keys.setdefault(chat_id, {})["elevenlabs"] = encrypt_key(api_key)
        context.bot.send_message(
            chat_id=chat_id,
            text="ElevenLabs API key has been configured successfully.")
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Invalid command. Please try again.")


def help_command(update, context):
    """
    Handle the /help command.
    Show available commands and their descriptions.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    chat_id = update.effective_chat.id
    message = "Available commands:\n"
    for cmd, desc in COMMANDS.items():
        message += f"{cmd}: {desc}\n"
    context.bot.send_message(chat_id=chat_id, text=message)


def get_voice_id(update, context):
    """
    Handle the /voices command.
    Retrieves the available voices from ElevenLabs.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    chat_id = update.effective_chat.id

    # Check if ElevenLabs API key is set
    user_api_keys = api_keys.get(chat_id)
    if not user_api_keys or not user_api_keys.get("elevenlabs"):
        context.bot.send_message(
            chat_id=chat_id,
            text=
            "ElevenLabs API key is not configured. Please use /elevenlabs {API-KEY} command to set the API key."
        )
        return

    elevenlabs_key = decrypt_key(user_api_keys.get("elevenlabs"))
    set_elevenlabs_api_key(elevenlabs_key)

    # Call query_voices to retrieve available voices
    voices_response = query_voices()

    # Extract voices from the response
    voices = voices_response.get('voices', [])

    if not voices:
        context.bot.send_message(chat_id=chat_id, text="No voices available.")
        return

    # Display voice options to the user
    voice_options = []
    for voice in voices:
        voice_name = voice.get('name')
        voice_options.append(f"{voice_name}")

    options_message = "Available voices:\n"
    options_message += "\n".join(voice_options)
    options_message += "\n\nPlease do /set_voice `name`. "

    context.bot.send_message(chat_id=chat_id, text=options_message)

    api_keys[chat_id]["voices"] = voices


def set_voice_id(update, context):
    """
    Handle user's voice selection and set the voice ID.

    Parameters:
        update (telegram.Update): The update object.
        context (telegram.ext.CallbackContext): The callback context.
    """
    user_selection = update.message.text.strip()[
        11:]  # Get user's selection (name or ID)
    chat_id = update.effective_chat.id

    if user_selection[:3] == '-id':
        api_keys.setdefault(chat_id, {})["voiceid"] = user_selection[4:]
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Voice ID set to `{user_selection[4:]}` successfully.")
        return

    if 'voices' not in api_keys[chat_id]:
        context.bot.send_message(
            chat_id=chat_id,
            text="List of voices to get ID from missing, please do /voices.")
        return

    voices = api_keys[chat_id]["voices"]

    # Find the voice ID based on user's selection
    selected_voice = None
    for voice in voices:
        voice_id = voice.get('voice_id')
        voice_name = voice.get('name').lower()
        if voice_name.lower() == user_selection.lower() or voice_id.lower(
        ) == user_selection.lower():
            selected_voice = voice
            break

    if selected_voice:
        # Set the voice ID in api_keys
        api_keys[chat_id]["voiceid"] = selected_voice['voice_id']
        context.bot.send_message(
            chat_id=chat_id,
            text=(f"Voice `{selected_voice['name']}` set successfully, "
                  "ID set to {selected_voice['voice_id']}."))
    else:
        context.bot.send_message(
            chat_id=chat_id, text="Invalid voice selection. Please try again.")


def main():
    """
    The main function to start the Telegram bot.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    start_handler = CommandHandler('start', start)
    query_handler = CommandHandler('query', query)
    set_api_key_handler = CommandHandler(['openai', 'elevenlabs'], set_api_key)
    help_handler = CommandHandler(['help', 'commands'], help_command)
    voice_id_handler = CommandHandler('voices', get_voice_id)
    set_id_handler = CommandHandler('set_voice', set_voice_id)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(query_handler)
    dispatcher.add_handler(set_api_key_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(voice_id_handler)
    dispatcher.add_handler(set_id_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
