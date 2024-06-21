import schedule
import time
import logging
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, ChannelsTooMuchError

# Configure logging to show debug messages
# logging.basicConfig(level=logging.DEBUG)

# Replace with your own Telegram API credentials
api_id = '26809903'
api_hash = '0b8582d56d4f31de363fffb9c88804cd'

# Replace with your own phone number and the path to the session file
phone_number = '+14012128946'
session_file = 'everythingisfine'

# Keywords to search for channels
keywords = ['Software']

# Message to post
message = (
    "With over 3 years of experience in Software DevOps, I honed my skills in UI/UX design, "
    "performance optimization, and project leadership. My efforts successfully translate business "
    "requirements into solutions, resulting in more effective and user-loved apps. With a robust background "
    "in computer science and tech experience, I'll bring extensive results and expertise in the IT section.\n\n"
    "My workflow is based on Agile methodologies and my business style is 'No job is too big or small'."
)

client = TelegramClient(session_file, api_id, api_hash)

# List to store channels to send messages to
target_channels = []

def connect_client():
    if not client.is_connected():
        client.connect()
        if not client.is_user_authorized():
            try:
                client.start(phone_number)
                client.sign_in(code=input('Enter the code: '))
            except FloodWaitError as e:
                logging.error(f"Flood wait error: {e}")
                time.sleep(e.seconds)

def fetch_all_joined_channels():
    connect_client()
    try:
        # Fetch all dialogs (conversations)
        dialogs = client.get_dialogs()
        channels = [dialog.entity for dialog in dialogs if dialog.is_channel]
        return channels
    except Exception as e:
        logging.error(f"Error fetching joined channels: {e}")
        return []

def search_and_join_channels():
    global target_channels
    connect_client()
    for keyword in keywords:
        try:
            result = client(SearchRequest(
                q=keyword,
                limit=20  # Number of channels to find per keyword
            ))
            for chat in result.chats:
                if chat.megagroup or chat.broadcast:  # Ensure it's a channel or supergroup
                    try:
                        client(JoinChannelRequest(channel=chat))
                        target_channels.append(chat)
                        logging.info(f"Joined and added channel: {chat.title}")
                        print(chat.title)
                    except UserPrivacyRestrictedError:
                        logging.warning(f"Privacy settings restrict joining channel: {chat.title}")
                    except FloodWaitError as e:
                        logging.warning(f"Flood wait error: {e}")
                        time.sleep(e.seconds)
                    except ChannelsTooMuchError:
                        logging.warning("Too many channels joined, can't join more.")
                        return
        except Exception as e:
            logging.error(f"Error searching for channels with keyword '{keyword}': {str(e)}")

def send_message_to_channels():
    connect_client()
    for chat in target_channels:
        try:
            client.send_message(chat, message)
            logging.info(f"Message sent successfully to {chat.title}")
        except Exception as e:
            logging.error(f"Failed to send message to {chat.title}: {str(e)}")

def main():
    connect_client()
    target_channels.extend(fetch_all_joined_channels())
    search_and_join_channels()
    send_message_to_channels()
    schedule.every(10).minutes.do(send_message_to_channels)

    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")

    client.disconnect()

if __name__ == '__main__':
    main()
