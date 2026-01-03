import asyncio
from telegram import Bot
import os



async def get_missing_messages(bot_token):
    bot = Bot(token=bot_token)
    updates = await bot.get_updates()

    if updates:
        print(f"Found {len(updates)} missing messages.")
        for update in updates:
            # Process your message here (e.g., store in DB, react)
            print(f"Processing message ID: {update.message.message_id} from {update.message.chat_id}")
            # print(update.message.text)

        # Acknowledge all retrieved updates by setting the offset
        last_update_id = updates[-1].update_id
        # By calling get_updates again with an offset+1, we tell Telegram to stop sending these
        await bot.get_updates(offset=last_update_id + 1)
        print("Acknowledged all retrieved messages.")
    else:
        print("No missing messages found.")


if __name__ == '__main__':
    # Replace with your actual bot token

    asyncio.run(get_missing_messages(os.getenv("TELEGRAM_BOT_KEY")))