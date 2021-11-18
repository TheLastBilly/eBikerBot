#!/usr/bin/python3

import cv2
import logging
import random
import base64
import string
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Get bot info
with open("./token", 'r+') as f:
    API_TOKEN = str(f.readline()).strip()
with open("./owner", 'r+') as f:
    OWNER = str(f.readline()).strip()
    ALLOWED_USER_FILTER = Filters.user(username=OWNER)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def createRandomBase64String(n = 10):
    r_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    b = base64.urlsafe_b64encode(r_str.encode("ascii"))
    return str(b, "ascii")

def takeCapture():
    cap = cv2.VideoCapture(0)
    ret,frame = cap.read()

    if ret and frame is not None:
        path = "/tmp/capture{}.jpg".format(createRandomBase64String())
        cv2.imwrite(path, frame)
        return path
    
    return None

def capture(update, context):
    path = takeCapture()
    if path is not None:
        update.message.bot.send_photo(update.message.chat.id,photo=open(path, 'rb'))
    else:
        update.message.reply_text("Cannot take capture!")
    
def cli(update, context):
    command = update.message.text.lower()
    if command == "capture":
        capture(update, context)
    else:
        update.message.reply_text("Unknown command")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(API_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("capture", capture, ALLOWED_USER_FILTER))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text and ALLOWED_USER_FILTER, cli))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
