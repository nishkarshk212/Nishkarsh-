# Copyright (c) 2025 TheHamkerNishkarsh 
# Licensed under the MIT License.
# This file is part of NishkarshMusic


import random
import pyrogram
from pyrogram.enums import ChatAction

from Nishkarsh import config, logger

EMOJIS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "🍿", "🦍", "⚡️", "☃️", "⛄️", "🗿", "🆒", "🙊", "🦄", "🍭", "👾", "🫥", "💊", "💋", "🐳",
    # Premium Emojis (Custom Emoji IDs)
    5431466076986203243, 5431113032587071029, 5431154563821915354, 5431327142491503373, 5431260907267469614,
    5431458231423131811, 5431319200845318850, 5431113032587071029, 5431057813585054358, 5431113032587071029
]

class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            name="Nishkarsh",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
        )
        self.owner = config.OWNER_ID
        self.logger = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def send_reaction(self, chat_id, message_id, emoji=None):
        if emoji is None:
            emoji = random.choice(EMOJIS)
        try:
            return await super().send_reaction(chat_id, message_id, emoji)
        except Exception:
            pass

    async def send_message(self, *args, **kwargs):
        msg = await super().send_message(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_photo(self, *args, **kwargs):
        msg = await super().send_photo(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_video(self, *args, **kwargs):
        msg = await super().send_video(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_audio(self, *args, **kwargs):
        msg = await super().send_audio(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_document(self, *args, **kwargs):
        msg = await super().send_document(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_voice(self, *args, **kwargs):
        msg = await super().send_voice(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_animation(self, *args, **kwargs):
        msg = await super().send_animation(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def send_sticker(self, *args, **kwargs):
        msg = await super().send_sticker(*args, **kwargs)
        await self.send_reaction(msg.chat.id, msg.id)
        return msg

    async def boot(self):
        """
        Starts the bot and performs initial setup.

        Raises:
            SystemExit: If the bot fails to access the log group or is not an administrator in the logger group.
        """
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(self.logger, "Bot Started")
            get = await self.get_chat_member(self.logger, self.id)
            if get.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                logger.warning("Please promote the bot as an admin in logger group.")
        except Exception as ex:
            logger.warning(f"Bot has failed to access the log group: {self.logger}\nReason: {ex}")

        logger.info(f"Bot started as @{self.username}")

    async def exit(self):
        """
        Asynchronously stops the bot.
        """
        await super().stop()
        logger.info("Bot stopped.")
