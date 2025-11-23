import os
import tempfile
import time
import json
import requests
from pathlib import Path
from typing import Optional
import streamlit as st


class VideoGenerator:
    """Klasse voor het genereren van video met HeyGen API."""
    
    def __init__(self, api_key: str, avatar_id: Optional[str] = None):
        """
        Initialiseer de VideoGenerator.
        
        Args:
            api_key: HeyGen API key
            avatar_id: Optionele HeyGen avatar ID (video group avatar ID). 
                      Als niet opgegeven, wordt een talking_photo gebruikt.
        """
        if not api_key:
            raise ValueError("HeyGen API key is vereist")
        self.api_key = api_key.strip()
        self.avatar_id = avatar_id.strip() if avatar_id else None
    
    def generate(self, audio_bytes, image_path: str = "sint.png") -> Optional[str]:
        """
        Genereer video met HeyGen.
        
        Args:
            audio_bytes: Audio bytes (io.BytesIO of bytes)
            image_path: Pad naar de afbeelding (alleen gebruikt als geen avatar_id is opgegeven)
        
        Returns:
            Video URL als string, of None bij fout
        """
        # Upload audio
        audio_asset_id = self._upload_asset(audio_bytes, "audio/mpeg", "Audio")
        if not audio_asset_id:
            return None
        
        # Als avatar_id is opgegeven, gebruik die. Anders upload image voor talking_photo
        character_config = None
        if self.avatar_id:
            # Gebruik avatar ID
            character_config = {
                "type": "avatar",
                "avatar_id": self.avatar_id
            }
        else:
            # Upload image voor talking_photo
            image_asset_id = self._upload_asset_from_file(image_path, "image/png", "Afbeelding")
            if not image_asset_id:
                return None
            character_config = {
                "type": "talking_photo",
                "talking_photo_id": image_asset_id
            }
        
        # Generate video
        video_id = self._start_generation(audio_asset_id, character_config)
        if not video_id:
            return None
        
        # Poll for completion
        return self._poll_for_completion(video_id)
    
    def _upload_asset(self, file_data, content_type: str, asset_type: str) -> Optional[str]:
        """Upload een bestand (bytes) naar HeyGen."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        
        try:
            # Extract bytes
            if hasattr(file_data, 'getvalue'):
                file_data.seek(0)
                data = file_data.getvalue()
            elif hasattr(file_data, 'read'):
                file_data.seek(0)
                data = file_data.read()
            elif isinstance(file_data, bytes):
                data = file_data
            else:
                st.error(f"❌ Onbekend formaat voor {asset_type}")
                return None
            
            temp_file.write(data)
            temp_file.flush()
            temp_file.close()
            
            return self._upload_asset_from_file(temp_filename, content_type, asset_type)
        finally:
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
    
    def _upload_asset_from_file(self, file_path: str, content_type: str, asset_type: str) -> Optional[str]:
        """Upload een bestand naar HeyGen via requests library (gebaseerd op officiële voorbeeldcode)."""
        filename = os.path.basename(file_path)
        
        # Controleer of bestand bestaat
        if not os.path.exists(file_path):
            st.error(f"❌ Kon {asset_type} bestand niet vinden: {file_path}")
            return None
        
        try:
            # Gebruik de officiële API endpoint en 'file' als field name (zoals in voorbeeldcode)
            upload_url = "https://api.heygen.com/v1/asset"
            headers = {
                'X-Api-Key': self.api_key
            }
            
            # Open bestand als binaire stream en upload (zoals in voorbeeldcode)
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, content_type)
                }
                
                st.write(f"🛠️ Bezig met uploaden van {filename}...")
                response = requests.post(upload_url, headers=headers, files=files, timeout=60)
            
            if response.status_code == 200:
                json_data = response.json()
                if "data" in json_data and "id" in json_data["data"]:
                    asset_id = json_data["data"]["id"]
                    st.success(f"✅ {asset_type} succesvol geüpload! Asset ID: {asset_id}")
                    return asset_id
                else:
                    st.error(f"❌ Onverwacht antwoord: {json_data}")
                    return None
            else:
                error_text = response.text[:200]
                st.error(f"❌ Upload mislukt (status {response.status_code}): {error_text}")
                return None
                
        except FileNotFoundError as e:
            st.error(f"❌ Bestand niet gevonden: {e}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Fout bij uploaden: {str(e)[:200]}")
            return None
        except Exception as e:
            st.error(f"❌ Onverwachte fout bij uploaden: {str(e)[:200]}")
            return None
    
    def _start_generation(self, audio_asset_id: str, character_config: dict) -> Optional[str]:
        """Start video generatie (gebaseerd op officiële voorbeeldcode)."""
        generate_url = "https://api.heygen.com/v2/video/generate"
        
        # Voeg scale toe aan character config als het een avatar is (zoals in voorbeeldcode)
        if character_config.get("type") == "avatar" and "scale" not in character_config:
            character_config["scale"] = 1.0
        
        payload = {
            "video_inputs": [
                {
                    "character": character_config,
                    "voice": {
                        "type": "audio",
                        "audio_asset_id": audio_asset_id
                    }
                }
            ],
            "test": False,  # Zet op False voor watermerk-vrije video (verbruikt credits)
            "dimension": {
                "width": 1920,  # HD kwaliteit (zoals in voorbeeldcode)
                "height": 1080
            }
        }
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            st.write("🛠️ Video generatie verzoek sturen...")
            response = requests.post(generate_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                json_data = response.json()
                video_id = json_data["data"]["video_id"]
                st.write(f"✅ Video wordt gemaakt! Video ID: {video_id}")
                return video_id
            else:
                st.error(f"❌ Video generatie mislukt: {response.text}")
                return None
        except Exception as e:
            st.error(f"❌ Fout bij starten generatie: {e}")
            return None
    
    def _poll_for_completion(self, video_id: str) -> Optional[str]:
        """Poll voor video completion (gebaseerd op officiële voorbeeldcode)."""
        status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        headers = {"X-Api-Key": self.api_key}
        progress_bar = st.progress(0)
        
        st.write("🛠️ Wachten op renderen...")
        
        while True:
            try:
                response = requests.get(status_url, headers=headers)
                json_data = response.json()
                data = json_data["data"]
                status = data["status"]
                
                if status == "completed":
                    progress_bar.progress(100)
                    video_url = data["video_url"]
                    st.success(f"✅ Klaar! Video URL: {video_url}")
                    return video_url
                elif status == "failed":
                    error_msg = data.get('error', 'Onbekende fout')
                    st.error(f"❌ Renderen is mislukt: {error_msg}")
                    return None
                elif status in ["processing", "pending"]:
                    st.text(f"Status: {status}... even wachten")
                    time.sleep(5)  # Wacht 5 seconden (zoals in voorbeeldcode)
                else:
                    st.warning(f"Onbekende status: {status}")
                    time.sleep(5)
            except Exception as e:
                st.error(f"Fout tijdens wachten: {e}")
                return None

