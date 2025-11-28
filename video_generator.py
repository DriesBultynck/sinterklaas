import os
import tempfile
import time
import json
import requests
from typing import Optional
import streamlit as st

class VideoGenerator:
    """Klasse voor het genereren van video met HeyGen API V2."""
    
    def __init__(self, api_key: str, avatar_id: str):
        """
        Initialiseer de VideoGenerator.
        
        Args:
            api_key: HeyGen API key
            avatar_id: De ID van de avatar die je wilt gebruiken (Verplicht).
        """
        if not api_key:
            raise ValueError("HeyGen API key is vereist")
        if not avatar_id:
            raise ValueError("Avatar ID is vereist voor deze V2 implementatie")
            
        self.api_key = api_key.strip()
        self.avatar_id = avatar_id.strip()
    
    def list_avatars(self) -> Optional[list]:
        """
        Haal een lijst op van alle beschikbare avatars in je HeyGen account.
        
        Returns:
            List van avatar dictionaries met details, of None bij fout
        """
        avatars_url = "https://api.heygen.com/v2/avatars"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = requests.get(avatars_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                json_data = response.json()
                if "data" in json_data and "avatars" in json_data["data"]:
                    avatars = json_data["data"]["avatars"]
                    return avatars
                else:
                    st.error(f"❌ Onverwacht API formaat: {json_data}")
                    return None
            else:
                st.error(f"❌ Fout bij ophalen avatars ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Exception bij ophalen avatars: {e}")
            return None
    
    def generate(self, audio_bytes) -> Optional[str]:
        """
        Genereer video met HeyGen V2 (Avatar + Audio).
        
        Args:
            audio_bytes: Audio bytes (io.BytesIO of bytes)
        
        Returns:
            Video URL als string, of None bij fout
        """
        # Debug: Check audio data
        if hasattr(audio_bytes, 'getvalue'):
            data = audio_bytes.getvalue()
        elif hasattr(audio_bytes, 'read'):
            try:
                audio_bytes.seek(0)
            except (OSError, AttributeError):
                pass
            data = audio_bytes.read()
        else:
            data = audio_bytes
        
        if not data or len(data) == 0:
            st.error("❌ Audio data is leeg!")
            return None
        
        st.info(f"📊 Audio grootte: {len(data)} bytes")
        
        # Stap 1: Upload audio om een Asset ID te krijgen
        audio_asset_id = self._upload_asset(audio_bytes, "audio/mpeg")
        
        if not audio_asset_id:
            st.error("❌ Audio upload mislukt, kan niet starten met genereren.")
            return None
        
        # Stap 2: Start Video Generatie (V2)
        video_id = self._start_generation_v2(audio_asset_id)
        
        if not video_id:
            return None
        
        # Stap 3: Poll status tot voltooiing
        return self._poll_for_completion(video_id)
    
    def _upload_asset(self, file_data, content_type: str) -> Optional[str]:
        """Upload audio bytes naar HeyGen."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        
        try:
            # Bytes wegschrijven naar temp file
            if hasattr(file_data, 'getvalue'):
                data = file_data.getvalue()
            elif hasattr(file_data, 'read'):
                try:
                    file_data.seek(0)
                except (OSError, AttributeError):
                    pass
                data = file_data.read()
            else:
                data = file_data
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if not data or len(data) == 0:
                st.error("❌ Geen audiogegevens beschikbaar om te uploaden.")
                return None
            
            temp_file.write(data)
            temp_file.close()
            
            st.info(f"💾 Temp bestand aangemaakt: {len(data)} bytes")
            
            return self._upload_file_to_api(temp_filename, content_type)
        finally:
            # Opruimen
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
    
    def _upload_file_to_api(self, file_path: str, content_type: str) -> Optional[str]:
        """Fysieke upload naar de HeyGen Upload Endpoint."""
        if not os.path.exists(file_path):
            st.error(f"❌ Bestand niet gevonden: {file_path}")
            return None
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            st.error("❌ Bestand is leeg!")
            return None
        
        st.info(f"📤 Bestandsgrootte: {file_size} bytes")
        
        # HeyGen Upload Asset endpoint
        upload_url = "https://upload.heygen.com/v1/asset"
        
        # BELANGRIJK: Volgens HeyGen documentatie moet de file als RAW BINARY DATA
        # in de request body gestuurd worden, NIET als multipart/form-data!
        headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': content_type  # Dit specificeert het bestandstype
        }
        
        try:
            st.info(f"🛠️ Audio uploaden naar HeyGen...")
            
            # Lees het bestand als binary data
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            st.info(f"📦 {len(file_content)} bytes geladen")
            
            # Stuur de raw binary data direct in de body
            response = requests.post(
                upload_url,
                headers=headers,
                data=file_content,  # Raw binary data, GEEN files parameter!
                timeout=120
            )
            
            st.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                st.info(f"📋 Response data: {json.dumps(json_data, indent=2)}")
                
                # HeyGen response format: {"code": 100, "data": {"id": "...", ...}}
                if "data" in json_data and "id" in json_data["data"]:
                    asset_id = json_data["data"]["id"]
                    st.success(f"✅ Audio geüpload! Asset ID: {asset_id}")
                    return asset_id
                else:
                    st.error(f"❌ Onverwacht response format: {json_data}")
                    return None
            else:
                st.error(f"❌ Upload Error ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Exception bij upload: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None

    def _start_generation_v2(self, audio_asset_id: str) -> Optional[str]:
        """Start de V2 Video Generatie met Avatar + Audio ID."""
        generate_url = "https://api.heygen.com/v2/video/generate"
        
        # Correcte V2 Payload volgens documentatie
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": self.avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "audio",
                        "audio_asset_id": audio_asset_id
                    },
                    "background": {
                        "type": "color",
                        "value": "#FFFFFF"
                    }
                }
            ],
            "dimension": {
                "width": 1280,
                "height": 720
            }
        }
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            st.info("🛠️ Video generatie starten...")
            st.info(f"📋 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(generate_url, headers=headers, json=payload, timeout=30)
            
            st.info(f"📡 Response status: {response.status_code}")
            st.info(f"📋 Response: {response.text}")
            
            if response.status_code == 200:
                json_data = response.json()
                if "data" in json_data and "video_id" in json_data["data"]:
                    video_id = json_data["data"]["video_id"]
                    st.success(f"✅ Job gestart! Video ID: {video_id}")
                    return video_id
                else:
                    st.error(f"❌ Onverwacht response format: {json_data}")
            else:
                st.error(f"❌ Generatie mislukt ({response.status_code}): {response.text}")
            
            return None
            
        except Exception as e:
            st.error(f"❌ Fout bij aanroep: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
    def _poll_for_completion(self, video_id: str) -> Optional[str]:
        """Wacht tot de video klaar is."""
        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"X-Api-Key": self.api_key}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        progress_value = 0
        
        while True:
            try:
                response = requests.get(status_url, headers=headers)
                json_data = response.json()
                
                if "data" not in json_data:
                    st.warning("⏳ Wachten op data...")
                    time.sleep(5)
                    continue

                data = json_data["data"]
                status = data.get("status")
                
                if status == "completed":
                    progress_bar.progress(100)
                    status_text.text("Status: Klaar!")
                    video_url = data.get("video_url")
                    st.success(f"🎥 Video is klaar!")
                    return video_url
                
                elif status == "failed":
                    error_msg = data.get('error', 'Onbekende fout')
                    st.error(f"❌ Renderen mislukt: {error_msg}")
                    return None
                
                elif status in ["processing", "pending", "waiting"]:
                    status_text.text(f"Status: {status}... (even geduld)")
                    # Fake progress voor UX
                    progress_value = min(progress_value + 5, 90)
                    progress_bar.progress(progress_value)
                    time.sleep(5)
                
                else:
                    status_text.text(f"Status: {status}")
                    time.sleep(5)
                    
            except Exception as e:
                st.error(f"Polling fout: {e}")
                time.sleep(5)
                continue