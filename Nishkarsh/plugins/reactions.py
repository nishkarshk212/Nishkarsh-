import random
from pyrogram import filters
from Nishkarsh import app, logger
from Nishkarsh.core.bot import EMOJIS

@app.on_message(filters.all, group=-1)
async def auto_reaction(_, message):
    if not message.from_user:
        return
    
    # Avoid reacting to self if it somehow triggers
    if message.from_user.id == app.id:
        return

    try:
        await app.send_reaction(message.chat.id, message.id)
    except Exception as e:
        logger.error(f"Plugin reaction error: {e}")
        pass
