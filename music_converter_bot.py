import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Retrieve the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start command handler - sends a welcome message
def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "🎶 Welcome to the Ultimate Music Converter Bot! 🎵\n\n"
        "Easily convert your favorite music files into formats like MP3, WAV, and AAC. "
        "Just upload a file, and we’ll handle the rest! 🚀"
    )
    update.message.reply_text(welcome_message)

# Handle audio file uploads and present conversion options
def handle_audio(update: Update, context: CallbackContext) -> None:
    message = update.message
    file = message.audio or message.voice
    
    # Inform the user that the audio file is being downloaded
    message.reply_text("Your audio file is being downloaded...")

    # Download the file locally
    file_path = file.get_file().download()

    # Determine the file's current format
    file_format = file.mime_type.split('/')[1]

    # Define available format options, excluding the current format
    formats = ["mp3", "opus", "wav", "aac"]
    available_formats = [fmt for fmt in formats if fmt != file_format]

    # If the file format is unrecognized, offer all options
    if file_format not in formats:
        available_formats = formats

    # Create inline keyboard buttons for available format options
    keyboard = [
        [InlineKeyboardButton(fmt.upper(), callback_data=fmt) for fmt in available_formats]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Ask the user to select a format for conversion
    message.reply_text("Choose a format to convert to:", reply_markup=reply_markup)

    # Save the file path in context for later use in conversion
    context.user_data["file_path"] = file_path

# Convert the audio based on the user's selection
def convert_audio(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Retrieve the chosen format and the file path
    chosen_format = query.data
    file_path = context.user_data["file_path"]

    # Notify the user that the conversion process is starting
    query.edit_message_text(text="Starting conversion...")

    # Determine the output path with the new format
    output_path = f"{os.path.splitext(file_path)[0]}.{chosen_format}"

    # Convert the audio using pydub
    audio = AudioSegment.from_file(file_path)
    audio.export(output_path, format=chosen_format)

    # Send the converted file back to the user with the bot’s username as caption
    with open(output_path, "rb") as converted_file:
        query.message.reply_audio(
            audio=converted_file,
            caption="Here's your converted file! @YourBotUsername"
        )

    # Clean up files after sending
    os.remove(file_path)
    os.remove(output_path)

# Error handler
def error_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, something went wrong. Please try again.")

# Main function to set up the bot
def main():
    # Set up the bot using the environment variable BOT_TOKEN
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.audio | Filters.voice, handle_audio))
    dispatcher.add_handler(CallbackQueryHandler(convert_audio))
    dispatcher.add_error_handler(error_handler)

    # Start polling for updates
    updater.start_polling()
    updater.idle()

# Run the bot
if __name__ == "__main__":
    main()
