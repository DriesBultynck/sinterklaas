#!/usr/bin/env python3
"""Script om ALLEEN je eigen (custom) HeyGen avatars op te lijsten."""

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

# Create video generator with dummy avatar ID
video_gen = VideoGenerator(api_key, "dummy")

# List avatars
print("\n🎭 Jouw Custom HeyGen Avatars:\n")
print("=" * 80)

avatars = video_gen.list_avatars()

if avatars:
    # Filter alleen custom avatars (is_public = False en geen _public in ID)
    custom_avatars = [a for a in avatars if not a.get('is_public', True) and '_public' not in a.get('avatar_id', '')]
    
    if custom_avatars:
        for i, avatar in enumerate(custom_avatars, 1):
            avatar_id = avatar.get('avatar_id', 'N/A')
            avatar_name = avatar.get('avatar_name', 'N/A')
            avatar_type = avatar.get('avatar_type', 'N/A')
            
            print(f"\n{i}. {avatar_name}")
            print(f"   ID: {avatar_id}")
            print(f"   Type: {avatar_type}")
            
            if avatar_type == 'studio':
                print(f"   ✅ Geanimeerd (Studio Avatar) - GEBRUIK DEZE VOOR VIDEO")
            else:
                print(f"   📷 Photo Avatar - Werkt mogelijk niet met V2 API")
            
            # Check if this is the current avatar
            current_avatar_id = os.getenv("HEYGEN_AVATAR_ID", "")
            if avatar_id == current_avatar_id:
                print(f"   👉 HUIDIGE AVATAR IN .ENV")
            
            print("-" * 80)
        
        print(f"\n✅ Totaal: {len(custom_avatars)} custom avatar(s) gevonden")
        print("\n💡 Tip: Kopieer de ID van een 'studio' type avatar naar je .env bestand\n")
    else:
        print("❌ Geen custom avatars gevonden. Alleen public avatars beschikbaar.\n")
else:
    print("❌ Geen avatars gevonden of fout bij ophalen.\n")

