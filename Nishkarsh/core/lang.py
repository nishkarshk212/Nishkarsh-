# Copyright (c) 2025 TheHamkerNishkarsh
# Licensed under the MIT License.
# This file is part of NishkarshMusic
# ALONE-CODER
# @ForRealNishkarsh
# @XoDrk

import json
from functools import wraps
from pathlib import Path

from pyrogram import errors

from Nishkarsh import db, logger

lang_codes = {
    "ar": "Arabic",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "hi": "Hindi",
    "ja": "Japanese",
    "my": "Burmese",
    "pa": "Punjabi",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
}


class Language:
    """
    Language class for managing multilingual support using JSON language files.
    """

    def __init__(self):
        self.lang_codes = lang_codes
        self.lang_dir = Path("Nishkarsh/locales")
        self.languages = self.load_files()

    def load_files(self):
        languages = {}
        lang_files = {file.stem: file for file in self.lang_dir.glob("*.json")}
        for lang_code, lang_file in lang_files.items():
            try:
                with open(lang_file, "r", encoding="utf-8") as file:
                    languages[lang_code] = json.load(file)
            except Exception as e:
                logger.critical(
                    f"Failed to load localization file: {lang_file}. Error: {e}"
                )
                continue
        logger.info(f"Loaded languages: {', '.join(languages.keys())}")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        lang_code = await db.get_lang(chat_id)
        return self.languages[lang_code]

    def get_languages(self) -> dict:
        files = {f.stem for f in self.lang_dir.glob("*.json")}
        return {code: self.lang_codes[code] for code in sorted(files)}

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )
                
                if fallen:
                    logger.info(f"Update received: {type(fallen).__name__} from {fallen.from_user.id if fallen.from_user else 'None'}")
                else:
                    logger.info("Update received but no chat/message found")

                if not fallen.from_user:
                    logger.info("Ignoring update: No from_user")
                    return

                if hasattr(fallen, "chat"):
                    chat = fallen.chat
                elif hasattr(fallen, "message"):
                    chat = fallen.message.chat
                
                logger.info(f"Processing update for chat: {chat.id}")

                if chat.id in db.blacklisted:
                    logger.warning(f"Chat {chat.id} is blacklisted, leaving...")
                    return await chat.leave()

                logger.info(f"Fetching language for chat: {chat.id}")
                lang_code = await db.get_lang(chat.id)
                logger.info(f"Language found: {lang_code}")
                lang_dict = self.languages[lang_code]

                setattr(fallen, "lang", lang_dict)
                try:
                    return await func(*args, **kwargs)
                except (errors.Forbidden, errors.exceptions.Forbidden):
                    logger.warning(f"Cannot write to chat {chat.id}, leaving...")
                    return await chat.leave()

            return wrapper

        return decorator
