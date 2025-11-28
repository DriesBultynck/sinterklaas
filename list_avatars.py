#!/usr/bin/env python3
"""Script om beschikbare HeyGen avatars op te lijsten."""

import os
from dotenv import load_dotenv
from video_generator import VideoGenerator

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("HEYGEN_API_KEY")
if not api_key:
    print("❌ HEYGEN_API_KEY niet gevonden in .env bestand")
    exit(1)

# Create video generator with dummy avatar ID (alleen om de API key te gebruiken)
video_gen = VideoGenerator(api_key, "dummy")

# List avatars
print("\n🎭 Beschikbare HeyGen Avatars:\n")
print("=" * 80)

avatars = video_gen.list_avatars()

if avatars:
    for i, avatar in enumerate(avatars, 1):
        avatar_id = avatar.get('avatar_id', 'N/A')
        avatar_name = avatar.get('avatar_name', 'N/A')
        avatar_type = avatar.get('avatar_type', 'N/A')
        is_public = avatar.get('is_public', False)
        
        print(f"\n{i}. {avatar_name}")
        print(f"   ID: {avatar_id}")
        print(f"   Type: {avatar_type}")
        print(f"   Public: {'Ja' if is_public else 'Nee'}")
        print(f"   {'✅ Geanimeerd (Studio Avatar)' if avatar_type == 'studio' else '📷 Photo Avatar'}")
        
        # Check if this is the current avatar
        current_avatar_id = os.getenv("HEYGEN_AVATAR_ID", "")
        if avatar_id == current_avatar_id:
            print(f"   👉 HUIDIGE AVATAR IN .ENV")
        
        print("-" * 80)
    
    print(f"\n✅ Totaal: {len(avatars)} avatar(s) gevonden")
    print("\n💡 Tip: Gebruik een 'studio' type avatar voor video generatie met audio.")
    print("   Photo avatars werken mogelijk niet met de huidige V2 implementatie.\n")
else:
    print("❌ Geen avatars gevonden of fout bij ophalen.\n")

