import disnake
from disnake.ext import commands 

import re
from urllib.parse import urlparse
from typing import TypeVar, Literal, Optional, List, Union, Tuple, Dict
from loguru import logger as orpheus_log 
from src.core import Bot
from src.managers.database import get_session
from src.managers.database.models import WarnModel, AuditModel, GuildModel, MemberModel

INVITE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord(?:\.| |\[?\(?\"?'?dot'?\"?\)?\]?)?(?:gg|io|me|li)|discord(?:app)?\.com/invite)/+((?:(?!https?)[\w\d-])+)"
)


LINK_RE = re.compile(
    r"((?:https?://)[a-z0-9]+(?:[-._][a-z0-9]+)*\.[a-z]{2,5}(?::[0-9]{1,5})?(?:/[^ \n<>]*)?)", 
    re.IGNORECASE
)


MENTION_RE = re.compile(
    r"<@[!&]?\\d+>"
)


EMOTE_RE = re.compile(
    r"<(a?):([^: \n]+):([0-9]{15,20})>"
)


ALLOWED_FILE_FORMATS = [
    "txt",
    "md",

    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",

    "mov",
    "mp4",
    "flv",
    "mkv",

    "mp3",
    "wav",
    "m4a"
]


ZALGO = [
    u'\u030d',
    u'\u030e',
    u'\u0304',
    u'\u0305',
    u'\u033f',
    u'\u0311',
    u'\u0306',
    u'\u0310',
    u'\u0352',
    u'\u0357',
    u'\u0351',
    u'\u0307',
    u'\u0308',
    u'\u030a',
    u'\u0342',
    u'\u0343',
    u'\u0344',
    u'\u034a',
    u'\u034b',
    u'\u034c',
    u'\u0303',
    u'\u0302',
    u'\u030c',
    u'\u0350',
    u'\u0300',
    u'\u030b',
    u'\u030f',
    u'\u0312',
    u'\u0313',
    u'\u0314',
    u'\u033d',
    u'\u0309',
    u'\u0363',
    u'\u0364',
    u'\u0365',
    u'\u0366',
    u'\u0367',
    u'\u0368',
    u'\u0369',
    u'\u036a',
    u'\u036b',
    u'\u036c',
    u'\u036d',
    u'\u036e',
    u'\u036f',
    u'\u033e',
    u'\u035b',
    u'\u0346',
    u'\u031a',
    u'\u0315',
    u'\u031b',
    u'\u0340',
    u'\u0341',
    u'\u0358',
    u'\u0321',
    u'\u0322',
    u'\u0327',
    u'\u0328',
    u'\u0334',
    u'\u0335',
    u'\u0336',
    u'\u034f',
    u'\u035c',
    u'\u035d',
    u'\u035e',
    u'\u035f',
    u'\u0360',
    u'\u0362',
    u'\u0338',
    u'\u0337',
    u'\u0361',
    u'\u0489',
    u'\u0316',
    u'\u0317',
    u'\u0318',
    u'\u0319',
    u'\u031c',
    u'\u031d',
    u'\u031e',
    u'\u031f',
    u'\u0320',
    u'\u0324',
    u'\u0325',
    u'\u0326',
    u'\u0329',
    u'\u032a',
    u'\u032b',
    u'\u032c',
    u'\u032d',
    u'\u032e',
    u'\u032f',
    u'\u0330',
    u'\u0331',
    u'\u0332',
    u'\u0333',
    u'\u0339',
    u'\u033a',
    u'\u033b',
    u'\u033c',
    u'\u0345',
    u'\u0347',
    u'\u0348',
    u'\u0349',
    u'\u034d',
    u'\u034e',
    u'\u0353',
    u'\u0354',
    u'\u0355',
    u'\u0356',
    u'\u0359',
    u'\u035a',
    u'\u0323',
]

ZALGO_RE = re.compile(
    u"|".join(ZALGO)
)

ILLEGAL_CHARS = [
    "­",
    "​", 
    "\\"
]

class AutoModPlugin(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()

        self.bot = bot
        self.spam_cache: Dict[int, commands.CooldownMapping] = {}
        self.recent_messages: Dict[int, Dict[int, List[disnake.Message]]] = {}

    def update_recent_messages(self, msg: disnake.Message) -> None:
        if not msg.author.id in self.recent_messages:
            self.recent_messages[msg.guild.id] = [msg]
        else:
            last_ten = self.recent_messages[msg.author.id].get(msg.guild.id, [])
            if len(last_ten) == 10:
                last_ten[-1] = msg
            else:
                last_ten.append(msg)

            self.recent_messages[msg.author.id].update({
                msg.guild.id: last_ten
            })

    def get_recent_messages(self, msg: disnake.Message) -> List[Optional[disnake.Message]]:
        if not msg.author.id in self.recent_messages:
            return []
        else:
            return self.recent_messages[msg.author.id].get(msg.guild.id, [])
    
    async def can_act(
        self,
        guild: disnake.Guild,
        moderator: disnake.Member,
        target: Union[disnake.Member, disnake.User]
    ) -> bool:
        
        if moderator.id == target.id: return False
        if moderator.id == guild.owner_id: return True 

        moderator = guild.get_member(moderator.id)
        target = guild.get_member(target.id)

        if moderator == None or target == None: return False

        async_session = await get_session()

        async with async_session() as session:
            async with session.begin():
                guildModel = await GuildModel.fetch_one(session, guild_id=str(guild.id))

        await session.close()

    async def can_ignore(
        self,
        guild: disnake.Guild,
        channel: disnake.TextChannel,
        target: Union[disnake.Member, disnake.User]
    ) -> bool:
        
        async_session = await get_session()

        async with async_session() as session:
            async with session.begin():
                guildModel = await GuildModel.fetch_one(session, guild_id=str(guild.id))
                guildSettings = guildModel.settings 

        await session.close()

        roles = guildSettings["automod"]["whitelist"]["roles"]
        channels = guildSettings["automod"]["whitelist"]["channels"]

        if not channels is None:
            if channel.id in channels: return True 
        
        if any(x in [i.id for i in target.roles] for x in roles): return True 
        return False 
    
    def parse_regex(
        self,
        regex: str
    ) -> Optional[re.Pattern]:
        try:
            parsed = re.compile(regex, re.IGNORECASE)
        except Exception:
            return None 
        else:
            return parsed 
    
    def validate_regex(
        self,
        regex: str
    ) -> bool:
        try:
            re.compile(regex)
        except re.error:
            return False
        else:
            return True
        
    def safe_parse_url(
        self,
        url: str
    ) -> str:
        url = url.lower()
        if not (
            url.startswith("https://") or 
            url.startswith("http://")
        ):
            for x in [
                "www",
                "www5",
                "www2",
                "www3"
            ]:
                url = url.replace(x, "")

        else:
            url = urlparse(url).hostname
        return url 
    
    def sanitaze_content(
        self,
        content: str 
    ) -> str:
        for c in ILLEGAL_CHARS:
            content = content.replace(c, "")
        return content 
    
    async def delete_msg(
        self,
        rule: str,
        found: str,
        msg: disnake.Message,
        pattern_or_filter: Optional[str] = None
    ) -> None:
        try:
            await msg.delete()
        except (
            disnake.NotFound,
            disnake.Forbidden
        ):
            try:
                msg.add_reaction("❌")
            except:
                pass
            pass 


    async def enforce_rules(self, msg: disnake.Message) -> None:
        content = self.sanitaze_content(msg.content)

        async_session = await get_session()

        async with async_session() as session:
            async with session.begin():
                guildModel = await GuildModel.fetch_one(session, guild_id=str(msg.guild.id))
                guildSettings = guildModel.settings 

        await session.close()

        limits = guildSettings['automod']['limits']
        filters = guildSettings['automod']['filters']

        if filters['invite'] is True:
            found = INVITE_RE.findall(content)
            if found:
                for link in found:
                    try:
                        invite: disnake.Invite = await self.bot.fetch_invite(link)
                    except disnake.NotFound:
                        return await self.delete_msg(
                            "invite",
                            f"{link}",
                            msg
                        )

                    if invite.guild is None:
                        return await self.delete_msg(
                            "invite",
                            f"{link}",
                            msg
                        )
                    else:
                        if invite.guild is None or invite.guild.id != msg.guild.id:
                            return await self.delete_msg(
                                "invite",
                                f"{link}",
                                msg
                            )

        #if filters['links'] is True:
        #    found = LINK_RE.findall(content)
        #    if found:
        #        for link in found:
        #            url = urlparse(link)
        #            if url.hostname in 

        if filters['media'] is True:
            if len(msg.attachments) > 0:
                try:
                    forbidden = [
                        x.url.split(".")[-1] for x in msg.attachments \
                        if not x.url.split(".")[-1].lower() in ALLOWED_FILE_FORMATS
                    ]
                except Exception:
                    forbidden = []

                if len(forbidden) > 0:
                    return await self.delete_msg(
                        "media",
                        ", ".join([f"{x}" for x in forbidden]),
                        msg,
                    )
        
        if filters['symbols'] is True:
            found = ZALGO_RE.search(content)
            if found:
                return await self.delete_msg(
                    "symbols",
                    f"``{found.group()}``",
                    msg
                )
            
        if filters['mention'] is True:
            found = len(MENTION_RE.findall(content))
            if found > limits['mentions']:
                return await self.delete_msg(
                    "mention",
                    f"{found}",
                    msg
                )
            
        if filters['emoji'] is True:
            found = len(EMOTE_RE.findall(content))
            if found > limits['emoji']:
                return await self.delete_msg(
                    "emoji",
                    f"{found}",
                    msg
                )
            
        if filters['repeat'] is True:
            found = {}
            for word in content.split(" "):
                found.update({
                    word.lower(): found.get(word.lower(), 0) + 1
                })

            if len(found.keys()) < 12:
                for k, v in found.items():
                    if v > limits['repeat']:
                        return await self.delete_msg(
                            "repeat",
                            f"{k} ({v}x)",
                            msg
                        )  
        


    @commands.Cog.listener()                 
    async def on_message(self, message: disnake.Message) -> None:
        if message.guild == None: return 
        if not message.guild.chunked: return  
        #if not await self.can_act(message.guild, message.guild.me, message.author): return
        #if await self.can_ignore(message.guild, message.channel, message.author): return

        await self.enforce_rules(message)

    @commands.Cog.listener()
    async def on_message_edit(self, _, message: disnake.Message) -> None:
        if message.guild == None: return 
        if not message.guild.chunked: return  
        #if not await self.can_act(message.guild, message.guild.me, message.author): return
        #if await self.can_ignore(message.guild, message.channel, message.author): return

        await self.enforce_rules(message)


def setup(bot: Bot) -> None:
    bot.add_cog(AutoModPlugin(bot))