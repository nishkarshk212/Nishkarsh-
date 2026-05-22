# Copyright (c) 2025 TheHamkerNishkarsh 
# Licensed under the MIT License.
# This file is part of NishkarshMusic


import random
import pyrogram
from pyrogram.enums import ChatAction

from Nishkarsh import config, logger

EMOJIS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "🍿", "🦍", "⚡️", "☃️", "⛄️", "🗿", "🆒", "🙊", "🦄", "🍭", "👾", "🫥", "💊", "💋", "🐳"
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
        except Exception as e:
            # We'll try one more way if super() fails
            try:
                from pyrogram.types import ReactionTypeEmoji
                return await super().send_reaction(chat_id, message_id, ReactionTypeEmoji(emoji=emoji))
            except:
                pass
            pass

    async def send_message(self, *args, **kwargs):
        msg = await super().send_message(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_photo(self, *args, **kwargs):
        msg = await super().send_photo(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_video(self, *args, **kwargs):
        msg = await super().send_video(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_audio(self, *args, **kwargs):
        msg = await super().send_audio(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_document(self, *args, **kwargs):
        msg = await super().send_document(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_voice(self, *args, **kwargs):
        msg = await super().send_voice(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_animation(self, *args, **kwargs):
        msg = await super().send_animation(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
        return msg

    async def send_sticker(self, *args, **kwargs):
        msg = await super().send_sticker(*args, **kwargs)
        try:
            await msg.react(random.choice(EMOJIS))
        except:
            pass
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
