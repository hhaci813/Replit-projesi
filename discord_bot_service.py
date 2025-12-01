"""🎮 Discord Bot - Real-time alerts"""
import os
import asyncio
import discord
from discord.ext import commands

class DiscordBotService:
    def __init__(self, token=None):
        self.token = token or os.getenv('DISCORD_BOT_TOKEN')
        self.bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
        self.channel_id = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Bot event handlers"""
        @self.bot.event
        async def on_ready():
            print(f"✅ Discord Bot Ready: {self.bot.user}")
    
    def set_channel(self, channel_id):
        """Alert channel ayarla"""
        self.channel_id = channel_id
    
    async def send_alert(self, title, message, color=0x00ff00):
        """Embed message gönder"""
        try:
            if not self.token or not self.channel_id:
                print("❌ Discord token veya channel_id ayarlanmamış")
                return False
            
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print(f"❌ Channel bulunamadı: {self.channel_id}")
                return False
            
            embed = discord.Embed(
                title=title,
                description=message,
                color=color
            )
            embed.set_footer(text="AKILLI YATIRIM ASİSTANI")
            
            await channel.send(embed=embed)
            print(f"✅ Discord message gönderildi: {title}")
            return True
        
        except Exception as e:
            print(f"❌ Discord mesaj hatası: {e}")
            return False
    
    def run(self):
        """Discord bot'u çalıştır"""
        if not self.token:
            print("❌ DISCORD_BOT_TOKEN ayarlanmamış")
            return
        
        try:
            self.bot.run(self.token)
        except Exception as e:
            print(f"❌ Discord bot hatası: {e}")

if __name__ == "__main__":
    bot = DiscordBotService()
    print("🎮 Discord Bot Service Hazır")
