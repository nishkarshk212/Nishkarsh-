import random
from pyrogram import filters
from Nishkarsh import app, logger
from Nishkarsh.core.bot import EMOJIS

@app.on_message(filters.all, group=-1)
async def auto_reaction(_, message):
    if not message.from_user:
        return
    
    # Avoid reacting to self
    if message.from_user.id == app.id:
        return

    try:
        await message.react(random.choice(EMOJIS))
    except Exception as e:
        # Don't log for every message if it fails (e.g. in channels)
        pass
