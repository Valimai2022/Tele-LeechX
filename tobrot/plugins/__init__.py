from asyncio import create_subprocess_exec, subprocess
from shlex import split as ssplit
from shutil import rmtree
from re import match as rmatch
from urllib.parse import unquote, quote

from tobrot import DOWNLOAD_LOCATION, LOGGER
from tobrot.helper_funcs.display_progress import humanbytes
from typing import Tuple

async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = ssplit(cmd)
    process = await create_subprocess_exec(
        *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

def start_cleanup():
    try:
        rmtree(DOWNLOAD_LOCATION)
    except FileNotFoundError:
        pass


def is_gdtot_link(url: str): 
    url = rmatch(r'https?://.+\.gdtot\.\S+', url) 
    return bool(url)


def is_hubdrive_link(url: str): 
    url = rmatch(r'https?://hubdrive\.\S+', url) 
    return bool(url)


def is_appdrive_link(url: str): 
    url = rmatch(r'https?://appdrive\.\S+', url) 
    return bool(url)

def magnet_parse(mag_link):
    link = unquote(mag_link)
    link = link.split("&")
    tracker = ""
    tracCount = 0
    for check in link:
        if check.startswith('dn='):
            name = check.replace("dn=", "")
        elif check.startswith('tr='):
            tracCount += 1
            tracker += f"{tracCount}. <code>{check.replace('tr=', '')}</code>\n"
        elif check.startswith('magnet:?xt=urn:btih:'):
            hashh = check.replace('magnet:?xt=urn:btih:', '')
    return f"🔸️ <b>Hash :</b> <i>{hashh}</i>\n📨 <b>Name :</b> {name}\n🖲 <b>Trackers ({tracCount}) :</b> \n{tracker} \n 🔗 <a href='https://t.me/share/url?url={quote(mag_link)}'>Share To Telegram</a>"

def getDetails(client, message, func_txt: str):
    g_id = message.from_user.id
    u_men = message.from_user.mention
    link_send = message.text.split(" ", maxsplit=1)
    reply_to = message.reply_to_message
    txtCancel = False
    text__ = f"<i>⚡️{func_txt} Initiated⚡️</i>\n\n👤 <b>User</b> : <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n🆔 <b>User ID</b> : #ID{g_id}\n"
    if len(link_send) > 1:
        link = link_send[1]
        if link.lower().startswith("magnet:"):
            text__ += f"🧲 <b>Magnet Link Details</b> :  \n{magnet_parse(link)}"
        elif link.lower().startswith("http") and "|" not in link:
            text__ += f"🔗 <b>Link</b> :  <a href='{link.strip()}'>Click Here</a>"
        elif link.lower().startswith("http") and "|" in link:
            splitData = link.split("|", 1)
            link = splitData[0]
            text__ += f"🔗 <b>Link</b> :  <a href='{link.strip()}'>Click Here</a>\n🗳 <b>Custom Name</b> :<code>{splitData[1]}</code>"
        else:
            text__ += f"🔗 <b>Link</b> :  <code>{link}</code>"
    elif reply_to is not None:
        if reply_to.media:
            if reply_to.document:
                filename = [reply_to.document][0].file_name
                filesize = humanbytes([reply_to.document][0].file_size)
                if str(filename).lower().endswith(".torrent"):
                    text__ += f"\n📨 <b>File Name:</b> <code>{filename}</code>\n🗃 <b>Total Size:</b> <code>{filesize}</code>\n📂 <b>Media Type</b> : ☢️ <code>Torrent File</code> ☢️"
                else:
                    text__ += f"\n📨 <b>File Name:</b> <code>{filename}</code>\n🗃 <b>Total Size:</b> <code>{filesize}</code>\n📂 <b>Media Type</b> : 🗃 <code>Document</code> 🗃"
            elif reply_to.video:
                filename = [reply_to.video][0].file_name
                filesize = humanbytes([reply_to.video][0].file_size)
                text__ += f"\n📨 <b>File Name:</b> <code>{filename}</code>\n🗃 <b>Total Size:</b> <code>{filesize}</code>\n📂 <b>Media Type</b> :  🎥 <code>Video</code> 🎥"
            elif reply_to.audio:
                filename = [reply_to.audio][0].file_name
                filesize = humanbytes([reply_to.audio][0].file_size)
                text__ += f"\n📨 <b>File Name:</b> <code>{filename}</code>\n🗃 <b>Total Size:</b> <code>{filesize}</code>\n📂 <b>Media Type</b> :  🎶 <code>Audio</code> 🎶"
        elif reply_to.text.lower().startswith("magnet:"):
            text__ += f"🧲 <b>Magnet Link Details</b> :  \n{magnet_parse(reply_to.text)}"
        else:
            link = reply_to.text
            cusfname = ""
            cusfnam = link.split("|", maxsplit=1)
            if len(cusfnam) > 1:
                link, cusfname = cusfnam[0], cusfnam[1]
            LOGGER.info(cusfname)
            if cusfname != "" and link.lower().startswith("http"):
                text__ += f"🔗 <b>Link</b> :  <a href='{link.strip()}'>Click Here</a>\n🗳 <b>Custom Name</b> :<code>{cusfname}</code>"
            elif link.lower().startswith("http"):
                text__ += f"🔗 <b>Link</b> :  <a href='{link.strip()}'>Click Here</a>"
            else:
                text__ += f"🔗 <b>Link</b> :  <code>{link}</code>"
    else:
        txtCancel = True
        link = "N/A"
        text__ += f"🔗 <b>Link</b> : <code>{link}</code>"
    return text__, txtCancel
