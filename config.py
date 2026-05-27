#ALONE CODER
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", "17596251"))
        self.API_HASH = getenv("API_HASH", "e58343b4c0193e293e391daf97603fcd")

        self.BOT_TOKEN = getenv("BOT_TOKEN", "Apna Bot Token")
        self.MONGO_URL = getenv("MONGO_URL", "Apna Mongo Db Dalo")

        self.LOGGER_ID = int(getenv("LOGGER_ID", "Apna Log Group Id Dalo"))
        self.OWNER_ID = int(getenv("OWNER_ID", "Owner I'd dalo"))
        
        self.SESSION1 = getenv("SESSION", "Apna String Dalo")
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Tele_212_bots")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/jayden_clan")

        self.AUTO_END = getenv("AUTO_END", "False").lower() in ("true", "1", "yes")
        self.AUTO_LEAVE = getenv("AUTO_LEAVE", "False").lower() in ("true", "1", "yes")
        self.VIDEO_PLAY = getenv("VIDEO_PLAY", "True").lower() in ("true", "1", "yes")

        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "50"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", "5400"))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "20"))
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://i.ibb.co/dwSr1BCH/071045e1b930a364060e7f853a6394b8.jpg https://i.ibb.co/QjxJJq4z/a543640d2cae1726345278d761180958.jpg https://i.ibb.co/VcFwYZj0/c94b8f6d7917e218e2494ef8dda9873c.jpg").split()

        self.XBIT_API_KEY = getenv("XBIT_API_KEY", "xbit_40gZEycIlXXF38AlKKU4I96ZnNaiDFOV")
        self.XBIT_API_URL = getenv("XBIT_API_URL", "https://tgapi.xbitcode.com")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
