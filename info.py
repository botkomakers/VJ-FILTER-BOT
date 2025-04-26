# Don't Remove Credit @VJ_Botzv
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01


import re
from os import environ
from Script import script 

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'shsk')
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")


#For Request optional


DB_URL = environ.get('DATABASE_URI', "")
DB_NAME = environ.get('DATABASE_NAME', "techvjclonefilterbot")




# This Pictures Is For Start Message Picture, You Can Add Multiple By Giving One Space Between Each.
PICS = (environ.get('PICS', 'https://image.tmdb.org/t/p/original/fzvzm3HDEHhnpdiq17pdE7eJ6WJ.jpg https://image.tmdb.org/t/p/original/fwrqW8Lp5VQuppFrODd4iJ8LySE.jpg https://image.tmdb.org/t/p/original/ulMscezy9YX0bhknvJbZoUgQxO5.jpghttps://i.ibb.co/Rk0dkmvm/file-1314.jpg https://i.ibb.co/kgPRfF8c/file-1260.jpg https://i.ibb.co/pB4yG84v/file-1300.jpg https://i.ibb.co/KpX2qZJx/file-1298.jpg https://i.ibb.co/Sw6RB9hL/file-1299.jpg https://i.ibb.co/b5JJcfZm/file-1301.jpg https://i.ibb.co/N6v06yzq/file-1302.jpg https://i.ibb.co/Kc5HY6Fk/file-1303.jpg https://i.ibb.co/Jj6N9myY/file-1304.jpg https://i.ibb.co/6csMfgzc/file-1305.jpg https://i.ibb.co/yB6JzS25/file-1306.jpg https://i.ibb.co/Wvds1rvz/file-1307.jpg https://i.ibb.co/vvcwj75j/file-1308.jpg https://i.ibb.co/mrLzRHgy/file-1310.jpg https://i.ibb.co/4ZqTYDpm/file-1309.jpg https://i.ibb.co/XfXwzLnk/file-1311.jpg https://i.ibb.co/wh3c8C1h/file-1312.jpg https://image.tmdb.org/t/p/original/2jApwp78umL4dK9uSBJAngNDiG9.jpg https://image.tmdb.org/t/p/original/pWmJBkdb0EMb3PSd2f9wjza0krb.jpg https://image.tmdb.org/t/p/original/nlPCdZlHtRNcF6C9hzUH4ebmV1w.jpg https://image.tmdb.org/t/p/original/3XRdZTizomKAFtWNa1MaOktxkKB.jpg https://image.tmdb.org/t/p/original/snkRCV3ED99mYwo962fxohaTfrI.jpg https://image.tmdb.org/t/p/original/5LtSjMNw6j3LkG29Oa4O0iY5U8.jpg https://image.tmdb.org/t/p/original/1CbExVP0bgrTshP7DvnDdwqryYL.jpg https://image.tmdb.org/t/p/original/83LbQ6xMURQYO03Ilqdr3kwLBxD.jpg https://image.tmdb.org/t/p/original/wQ60FXOHnVimJo6Bpdk6VU0qaP6.jpg https://image.tmdb.org/t/p/original/4UXfZjqt0C5kHTROotrsnfDYCh.jpg https://image.tmdb.org/t/p/original/gAozjuCvXYyrxhpkb0P4SuLnEkV.jpg https://image.tmdb.org/t/p/original/jAbyybBSXCyKGFy5EXlwW1NhjM.jpg https://image.tmdb.org/t/p/original/aqMBEpd4kC8GpUg6761qFPkvQuS.jpg https://image.tmdb.org/t/p/original/umyOinNa6vqqnqoVc9QqzyaapUz.jpg')).split()


# Admins & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '7862181538').split()] # For Multiple Id Use One Space Between Each.
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '7862181538').split()]  # For Multiple Id Use One Space Between Each.
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

# This Channel Is For When User Start Your Bot Then Bot Send That User Name And Id In This Log Channel, Same For Group Also.
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002589776901'))

# This Is File Channel Where You Upload Your File Then Bot Automatically Save It In Database 
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002530980008').split()]  # For Multiple Id Use One Space Between Each.

# auth_channel means force subscribe channel.
# if REQUEST_TO_JOIN_MODE is true then force subscribe work like request to join fsub, else if false then work like normal fsub.
REQUEST_TO_JOIN_MODE = bool(environ.get('REQUEST_TO_JOIN_MODE', True)) # Set True Or False
TRY_AGAIN_BTN = bool(environ.get('TRY_AGAIN_BTN', True)) # Set True Or False (This try again button is only for request to join fsub not for normal fsub)

# This Is Force Subscribe Channel, also known as Auth Channel 
auth_channel = environ.get('AUTH_CHANNEL', '-1002458764661') # give your force subscribe channel id here else leave it blank
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

# This Channel Is For When User Request Any File Name With command or hashtag like - /request or #request
reqst_channel = environ.get('REQST_CHANNEL', '-1002589776901')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None

# This Channel Is For Index Request 
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

# This Is Your Bot Support Group Id , Here Bot Will Not Give File Because This Is Support Group.
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-1002674031223')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None

# This Channel Is For /batch command file store.
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '-1002589776901')).split()]  # For Multiple Id Use One Space Between Each.

# This Channel Is For Delete Index File, Forward Your File In This Channel Which You Want To Delete Then Bot Automatically Delete That File From Database.
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-1002545091234').split()]  # For Multiple Id Use One Space Between Each.


# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")   # IF Multiple Database Is False Then Fill Only This Database Url.
DATABASE_NAME = environ.get('DATABASE_NAME', "techvjclonefilterbot")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'vjcollection')

MULTIPLE_DATABASE = bool(environ.get('MULTIPLE_DATABASE', False)) # Set True or False

# If Multiple Database Is True Then Fill All Three Below Database Uri Else You Will Get Error.
O_DB_URI = environ.get('O_DB_URI', "")   # This Db Is For Other Data Store
F_DB_URI = environ.get('F_DB_URI', "")   # This Db Is For File Data Store
S_DB_URI = environ.get('S_DB_URI', "mongodb+srv://sojib:sojib@cluster0.hfszr0v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")   # This Db is for File Data Store When First Db Is Going To Be Full.


# Premium And Referal Settings
PREMIUM_AND_REFERAL_MODE = bool(environ.get('PREMIUM_AND_REFERAL_MODE', True)) # Set Ture Or False

# If PREMIUM_AND_REFERAL_MODE is True Then Fill Below Variable, If Flase Then No Need To Fill.
REFERAL_COUNT = int(environ.get('REFERAL_COUNT', '20')) # number of referal count
REFERAL_PREMEIUM_TIME = environ.get('REFERAL_PREMEIUM_TIME', '1month') # time in week, day, month.
PAYMENT_QR = environ.get('PAYMENT_QR', 'https://files.catbox.moe/89raj0.jpg') # payment code picture url.
PAYMENT_TEXT = environ.get(
    'PAYMENT_TEXT',
    """<b>✨ 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗹𝗮𝗻𝘀 ✨

• $0.10 – 𝟭 𝗪𝗲𝗲𝗸 𝗔𝗰𝗰𝗲𝘀𝘀  
• $0.20 – 𝟭 𝗠𝗼𝗻𝘁𝗵 𝗣𝗹𝗮𝗻  
• $0.50 – 𝟯 𝗠𝗼𝗻𝘁𝗵𝘀 𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆  
• $0.90 – 𝟲 𝗠𝗼𝗻𝘁𝗵𝘀 𝗔𝗰𝗰𝗲𝘀𝘀  
• $1.50 – 𝗟𝗶𝗳𝗲𝘁𝗶𝗺𝗲 𝗔𝗰𝗰𝗲𝘀𝘀

🎁 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀 🎁

✓ No Verification Required  
✓ Direct File Downloads  
✓ Ad-Free & No Popups  
✓ Ultra-Fast Download Links  
✓ High-Quality Streaming  
✓ Unlimited File Access  
✓ Dedicated Admin Support  
✓ Priority Request Handling  
✓ Exclusive Filter Support in Groups  
✓ Refer & Earn – Give Access, Get Extra Months

📣 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗣𝗿𝗼𝗴𝗿𝗮𝗺  
Refer a friend and get +7 days extra on your plan!  
They must mention your username when activating.

💳 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝘃𝗶𝗮 𝗕𝗶𝗻𝗮𝗻𝗰𝗲 𝗨𝗜𝗗:  
<code>1122*****</code>

🚀 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗶𝗼𝗻 𝗦𝗽𝗲𝗲𝗱:  
Usually within 5 minutes

📸 𝗔𝗳𝘁𝗲𝗿 𝗣𝗮𝘆𝗺𝗲𝗻𝘁:  
Send a screenshot of your payment here.

✅ 𝗖𝗵𝗲𝗰𝗸 𝗣𝗹𝗮𝗻 𝗦𝘁𝗮𝘁𝘂𝘀:  
<code>/myplan</code>

🔁 𝗥𝗲𝗳𝘂𝗻𝗱 𝗣𝗼𝗹𝗶𝗰𝘆  
Refunds only applicable if premium is not activated within 1 hour.  
No refunds once activated.</b>"""
)


# Clone Information : If Clone Mode Is True Then Bot Clone Other Bots.
CLONE_MODE = bool(environ.get('CLONE_MODE', False)) # Set True or False
CLONE_DATABASE_URI = environ.get('CLONE_DATABASE_URI', "mongodb+srv://andfreefirew:andfreefirew@cluster0.qufbkvn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Necessary If clone mode is true
PUBLIC_FILE_CHANNEL = environ.get('PUBLIC_FILE_CHANNEL', 'hjjjkkyui') # Public Channel Username Without @ or without https://t.me/ and Bot Is Admin With Full Right.


# Links
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/moviehub_chats')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/movie_channel8')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'moviegroupbotko') # Support Chat Link Without https:// or @
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/moviesmansh')

# True Or False
AI_SPELL_CHECK = bool(environ.get('AI_SPELL_CHECK', True))
PM_SEARCH = bool(environ.get('PM_SEARCH', True))
BUTTON_MODE = bool(environ.get('BUTTON_MODE', False))
MAX_BTN = bool(environ.get('MAX_BTN', True))
IS_TUTORIAL = bool(environ.get('IS_TUTORIAL', False))
IMDB = bool(environ.get('IMDB', False))
AUTO_FFILTER = bool(environ.get('AUTO_FFILTER', True))
AUTO_DELETE = bool(environ.get('AUTO_DELETE', True))
LONG_IMDB_DESCRIPTION = bool(environ.get("LONG_IMDB_DESCRIPTION", False))
SPELL_CHECK_REPLY = bool(environ.get("SPELL_CHECK_REPLY", True))
MELCOW_NEW_USERS = bool(environ.get('MELCOW_NEW_USERS', True))
PROTECT_CONTENT = bool(environ.get('PROTECT_CONTENT', False))
PUBLIC_FILE_STORE = bool(environ.get('PUBLIC_FILE_STORE', True))
NO_RESULTS_MSG = bool(environ.get("NO_RESULTS_MSG", False))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))


# Token Verification Info :
VERIFY = bool(environ.get('VERIFY', False))
VERIFY_SHORTLINK_URL = environ.get('VERIFY_SHORTLINK_URL', 'tnlinks.in')
VERIFY_SHORTLINK_API = environ.get('VERIFY_SHORTLINK_API', 'bc38e85fce6fa153d2c4af55f9f36a71968ac978')
VERIFY_TUTORIAL = environ.get('VERIFY_TUTORIAL', 'https://t.me/hjjjkkyui/2693')

# If You Fill Second Shortner Then Bot Attach Both First And Second Shortner And Use It For Verify.
VERIFY_SECOND_SHORTNER = bool(environ.get('VERIFY_SECOND_SHORTNER', False))
# if verify second shortner is True then fill below url and api
VERIFY_SND_SHORTLINK_URL = environ.get('VERIFY_SND_SHORTLINK_URL', '')
VERIFY_SND_SHORTLINK_API = environ.get('VERIFY_SND_SHORTLINK_API', '')


# Shortlink Info
SHORTLINK_MODE = bool(environ.get('SHORTLINK_MODE', False)) # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'tnlinks.in')
SHORTLINK_API = environ.get('SHORTLINK_API', 'bc38e85fce6fa153d2c4af55f9f36a71968ac978')
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/hjjjkkyui/2693') # How Open Shortner Link Video Link , Channel Link Where You Upload Your Video.


# Others
CACHE_TIME = int(environ.get('CACHE_TIME', 1800))
MAX_B_TN = environ.get("MAX_B_TN", "5")
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'Hello My Dear Friends ❤️')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)


# Choose Option Settings 
LANGUAGES = ["malayalam", "mal", "tamil", "tam" ,"english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]
SEASONS = ["season 1", "season 2", "season 3", "season 4", "season 5", "season 6", "season 7", "season 8", "season 9", "season 10"]
EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = ["1900", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]


                           # Don't Remove Credit @VJ_Botz
                           # Subscribe YouTube Channel For Amazing Bot @Tech_VJ
                           # Ask Doubt on telegram @KingVJ01


# Online Stream and Download
STREAM_MODE = bool(environ.get('STREAM_MODE', True)) # Set True or False

# If Stream Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://testofvjfilter-1fa60b1b8498.herokuapp.com/")


# Rename Info : If True Then Bot Rename File Else Not
RENAME_MODE = bool(environ.get('RENAME_MODE', True)) # Set True or False


# Auto Approve Info : If True Then Bot Approve New Upcoming Join Request Else Not
AUTO_APPROVE_MODE = bool(environ.get('AUTO_APPROVE_MODE', False)) # Set True or False


# Start Command Reactions
REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions


if MULTIPLE_DATABASE == False:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = DATABASE_URI
    FILE_DB_URI = DATABASE_URI
    SEC_FILE_DB_URI = DATABASE_URI
else:
    USER_DB_URI = DATABASE_URI    # This Db is for User Data Store
    OTHER_DB_URI = O_DB_URI       # This Db Is For Other Data Store
    FILE_DB_URI = F_DB_URI        # This Db Is For File Data Store
    SEC_FILE_DB_URI = S_DB_URI    # This Db is for File Data Store When First Db Is Going To Be Full.


# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
