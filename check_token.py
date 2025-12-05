import os
import sys

# Force reload environment
token = os.environ.get('TELEGRAM_BOT_TOKEN', 'NOT_SET')
print(f"Current token in env: {token[:20] if token != 'NOT_SET' else 'NOT_SET'}...")

# If it's the old token, show warning
if token.startswith('8268294938'):
    print("⚠️ ESKİ TOKEN - Bu token geçersiz!")
    print("   Lütfen BotFather'dan YENİ bir token alın")
else:
    print(f"Token prefix: {token[:10]}...")
