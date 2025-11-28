#!/usr/bin/env python3
"""Script om werkende Studio avatars te vinden."""

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

# Create video generator
video_gen = VideoGenerator(api_key, "dummy")

# List avatars
print("\n🎭 Beschikbare Studio Avatars (Geanimeerd):\n")
print("=" * 80)

avatars = video_gen.list_avatars()

if avatars:
    # Filter alleen studio avatars
    studio_avatars = [a for a in avatars if a.get('avatar_type') == 'studio']
    
    if studio_avatars:
        # Toon eerste 10
        for i, avatar in enumerate(studio_avatars[:10], 1):
            avatar_id = avatar.get('avatar_id', 'N/A')
            avatar_name = avatar.get('avatar_name', 'N/A')
            
            print(f"\n{i}. {avatar_name}")
            print(f"   ID: {avatar_id}")
            print(f"   ✅ Studio Avatar - Werkt met V2 API")
            print("-" * 80)
        
        print(f"\n✅ Totaal: {len(studio_avatars)} studio avatar(s) gevonden")
        print(f"   (Eerste 10 getoond)")
        print(f"\n💡 Tip: Kopieer een van deze IDs naar je .env bestand als HEYGEN_AVATAR_ID\n")
    else:
        print("❌ Geen studio avatars gevonden.\n")
else:
    print("❌ Geen avatars gevonden of fout bij ophalen.\n")

