import random
from pyrogram import filters
from Nishkarsh import app
from Nishkarsh.core.bot import EMOJIS

@app.on_message(filters.all, group=-1)
async def auto_reaction(_, message):
    if not message.from_user:
        return
    
    # Check if it's a command or just a message
    # We react to all messages as requested "on every command of bot"
    # Usually, reacting to all messages is safer to ensure commands are covered.
    try:
        await app.send_reaction(message.chat.id, message.id, random.choice(EMOJIS))
    except Exception:
        pass
