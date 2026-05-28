# Copyright (c) 2025 TheHamkerNishkarsh
# Licensed under the MIT License
# This file is part of NishkarshMusic


import os
import re
import asyncio
import aiohttp
import random
import yt_dlp
from py_yt import Playlist, VideosSearch
from Nishkarsh import config, db, logger
from Nishkarsh.helpers import Track, utils

XBIT_API_URL = config.XBIT_API_URL
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
        ext = "mp4" if video else "m4a"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        xbit_url = await self._try_xbit(video_id, video)
        if xbit_url:
            return xbit_url

        logger.info(f"Attempting yt-dlp fallback for {video_id}")
        file_path = await self._download_ytdl(video_id, video)
        if not file_path:
            logger.warning(f"All download methods failed for {video_id}")
        return file_path

    async def _try_xbit(self, video_id: str, video: bool = False) -> str | None:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{XBIT_API_URL}/info/{video_id}"
                headers = {
                    "x-api-key": config.XBIT_API_KEY,
                    "Content-Type": "application/json"
                }
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "success":
                            stream_url = data.get("video_url" if video else "audio_url")
                            if stream_url:
                                logger.info(f"Streaming {video_id} from XBIT API")
                                return stream_url
                        else:
                            logger.warning("Xbit API error for " + video_id + ": " + str(data.get("message")))
                    else:
                        logger.warning("Xbit API returned status " + str(resp.status) + " for " + video_id)
        except Exception as e:
            logger.warning("Xbit API exception for " + video_id + ": " + str(e))
        return None

    async def _download_ytdl(self, video_id: str, video: bool = False) -> str | None:
        ext = "mp4" if video else "m4a"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best" if not video else "best[height<=720]/best",
            "outtmpl": file_path,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": self.get_cookies(),
            "nocheckcertificate": True,
            "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
            "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            "extract_flat": False,
            "retries": 3,
            "fragment_retries": 3,
        }

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(ydl_opts).download([f"https://www.youtube.com/watch?v={video_id}"])
            )
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"Downloaded via yt-dlp: {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"yt-dlp error for {video_id}: {e}")
        return None

    async def _write_file(self, file_path, response):
        with open(file_path, "wb") as f:
            async for chunk in response.content.iter_chunked(16384):
                await asyncio.to_thread(f.write, chunk)
