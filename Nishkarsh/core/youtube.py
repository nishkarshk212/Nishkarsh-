# Copyright (c) 2025 TheHamkerNishkarsh
# Licensed under the MIT License
# This file is part of NishkarshMusic


import os
import re
import asyncio
import aiohttp
import random
from py_yt import Playlist, VideosSearch
from Nishkarsh import config, logger
from Nishkarsh.helpers import Track, utils

API_SONG = config.NEXTGEN_API_SONG
API_VIDEO = config.NEXTGEN_API_VIDEO
DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "Nishkarsh/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                path = f"{self.cookie_dir}/cookie_{i}.txt"
                link = "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        # Check cache first
        cached_song = await db.get_song(query)
        if cached_song:
            return Track(
                id=cached_song.get("id"),
                channel_name=cached_song.get("channel_name"),
                duration=cached_song.get("duration"),
                duration_sec=cached_song.get("duration_sec"),
                message_id=m_id,
                title=cached_song.get("title"),
                thumbnail=cached_song.get("thumbnail"),
                url=cached_song.get("url"),
                view_count=cached_song.get("view_count"),
                video=video,
            )

        _search = VideosSearch(query, limit=1, with_live=False)
        results = await _search.next()
        if results and results["result"]:
            data = results["result"][0]
            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
            # Save to cache
            await db.save_song(query, {
                "id": track.id,
                "channel_name": track.channel_name,
                "duration": track.duration,
                "duration_sec": track.duration_sec,
                "title": track.title,
                "thumbnail": track.thumbnail,
                "url": track.url,
                "view_count": track.view_count
            })
            return track
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 11:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mp4" if video else "webm"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        try:
            async with aiohttp.ClientSession() as session:
                url = (API_VIDEO if video else API_SONG) + video_id
                params = {"api": config.NEXTGEN_API_KEY}
                
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"API returned status {resp.status} for {url}")
                        return None
                    
                    data = await resp.json()
                    download_url = data.get("link")
                    if not download_url:
                        logger.error(f"No download link found in API response: {data}")
                        return None

                # Now download the actual file from the link
                async with session.get(
                    download_url,
                    timeout=aiohttp.ClientTimeout(total=600 if video else 300),
                ) as file_resp:
                    if file_resp.status == 200:
                        await self._write_file(file_path, file_resp)
                    elif file_resp.status == 302:
                        redirect_url = file_resp.headers.get('Location')
                        if redirect_url:
                            async with session.get(redirect_url) as final_resp:
                                if final_resp.status == 200:
                                    await self._write_file(file_path, final_resp)

                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    logger.info(f"Downloaded: {file_path} ({os.path.getsize(file_path)} bytes)")
                    return file_path
                else:
                    logger.error(f"File {file_path} is empty or missing after download attempt.")
        except Exception as e:
            logger.warning(f"Download error for {video_id}: {e}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        return None

    async def _write_file(self, file_path, response):
        with open(file_path, "wb") as f:
            async for chunk in response.content.iter_chunked(16384):
                await asyncio.to_thread(f.write, chunk)
