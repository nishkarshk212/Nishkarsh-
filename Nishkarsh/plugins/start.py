# Copyright (c) 2025 TheHamkerNishkarsh
# Licensed under the MIT License.
# This file is part of NishkarshMusic
#ALONE-CODER

import asyncio
import random
from pyrogram import enums, filters, types

from Nishkarsh import app, config, db, lang
from Nishkarsh.helpers import buttons, utils


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    # React to the command
    try:
        await message.react("❤️")
    except:
        pass

    # Send sticker
    try:
        sticker_set = await app.get_sticker_set("Nishkarsh5")
        if sticker_set:
            sticker = random.choice(sticker_set.stickers)
            await message.reply_sticker(sticker.file_id)
    except:
        pass

    private = message.chat.type == enums.ChatType.PRIVATE
    _text = (
        message.lang["start_pm"].format(message.from_user.mention, app.mention)
        if private
        else message.lang["start_gp"].format(message.from_user.mention, app.mention)
    )

    key = buttons.start_key(message.lang, private)
    _img = (
        random.choice(config.START_IMG)
        if isinstance(config.START_IMG, list)
        else config.START_IMG
    )
    await message.reply_photo(
        photo=_img,
        caption=_text,
        reply_markup=key,
        quote=not private,
    )

    if private:
        if await db.is_user(message.from_user.id):
            return
        await utils.send_log(message)
        await db.add_user(message.from_user.id)
    else:
        if await db.is_chat(message.chat.id):
            return
        await utils.send_log(message, True)
        await db.add_chat(message.chat.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    if await db.get_cmd_delete(message.chat.id):
        try:
            await message.delete()
        except:
            pass
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    play_message_delete = await db.get_play_msg_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, play_message_delete, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
