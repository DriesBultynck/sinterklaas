import os
import tempfile
import time
import json
import http.client
import ssl
import uuid
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
        """Upload een bestand naar HeyGen via http.client."""
        filename = os.path.basename(file_path)
        field_names = ["content", "file", "asset", "data"]
        
        # Read file
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            file_size = len(file_content)
            st.write(f"🛠️ Debug: {asset_type} bestand gelezen: {file_size} bytes")
            st.write(f"🛠️ Debug: Eerste 10 bytes (hex): {file_content[:10].hex()}")
        except Exception as e:
            st.error(f"❌ Kon {asset_type} bestand niet lezen: {e}")
            return None
        
        # Try different field names
        for attempt, field_name in enumerate(field_names, 1):
            st.write(f"🛠️ Debug: Poging {attempt}/{len(field_names)} - field name: '{field_name}'")
            
            boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
            body_parts = [
                f"--{boundary}\r\n".encode('utf-8'),
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode('utf-8'),
                f'Content-Type: {content_type}\r\n'.encode('utf-8'),
                b'\r\n',
                file_content,
                f"\r\n--{boundary}--\r\n".encode('utf-8')
            ]
            payload = b''.join(body_parts)
            
            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection("upload.heygen.com", context=context)
            headers = {
                'X-Api-Key': self.api_key,
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(payload))
            }
            
            try:
                conn.request("POST", "/v1/asset", payload, headers)
                res = conn.getresponse()
                data = res.read()
                response_text = data.decode("utf-8")
                
                st.write(f"🛠️ Debug: Response status: {res.status}")
                
                if res.status == 200:
                    json_data = json.loads(response_text)
                    if "data" in json_data and "id" in json_data["data"]:
                        asset_id = json_data["data"]["id"]
                        st.success(f"✅ {asset_type} succesvol geüpload! Asset ID: {asset_id} (field name: '{field_name}')")
                        conn.close()
                        return asset_id
                    else:
                        st.warning(f"⚠️ Onverwacht antwoord bij poging {attempt}: {json_data}")
                elif res.status == 400:
                    st.write(f"⚠️ Poging {attempt} gefaald (400): {response_text[:100]}")
                    if attempt < len(field_names):
                        conn.close()
                        continue
                    else:
                        st.error(f"❌ Alle pogingen gefaald. Laatste response: {response_text}")
                        conn.close()
                        return None
                else:
                    st.write(f"⚠️ Poging {attempt} gefaald (status {res.status}): {response_text[:100]}")
                    if attempt < len(field_names):
                        conn.close()
                        continue
                    else:
                        st.error(f"❌ Alle pogingen gefaald. Laatste response: {response_text}")
                        conn.close()
                        return None
            except json.JSONDecodeError as e:
                st.write(f"⚠️ Kon response niet parsen als JSON bij poging {attempt}: {e}")
                if attempt < len(field_names):
                    conn.close()
                    continue
                else:
                    st.error(f"❌ Alle pogingen gefaald.")
                    conn.close()
                    return None
            except Exception as e:
                st.write(f"⚠️ Fout bij poging {attempt}: {str(e)[:100]}")
                if attempt < len(field_names):
                    conn.close()
                    continue
                else:
                    st.error(f"❌ Alle pogingen gefaald: {e}")
                    conn.close()
                    return None
            finally:
                if not conn.sock is None:
                    conn.close()
        
        return None
    
    def _start_generation(self, audio_asset_id: str, character_config: dict) -> Optional[str]:
        """Start video generatie."""
        generate_url = "https://api.heygen.com/v2/video/generate"
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
            "test": False,
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
            response = requests.post(generate_url, headers=headers, json=payload)
            if response.status_code != 200:
                st.error(f"❌ HeyGen Generate Fout: {response.text}")
                return None
            return response.json()["data"]["video_id"]
        except Exception as e:
            st.error(f"❌ Fout bij starten generatie: {e}")
            return None
    
    def _poll_for_completion(self, video_id: str) -> Optional[str]:
        """Poll voor video completion."""
        status_url = "https://api.heygen.com/v1/video_status.get"
        progress_bar = st.progress(0)
        
        while True:
            try:
                resp = requests.get(
                    f"{status_url}?video_id={video_id}",
                    headers={"X-Api-Key": self.api_key}
                )
                data = resp.json()["data"]
                status = data["status"]
                
                if status == "completed":
                    progress_bar.progress(100)
                    return data["video_url"]
                elif status == "failed":
                    st.error(f"❌ Video generatie mislukt: {data.get('error')}")
                    return None
                elif status in ["processing", "pending"]:
                    st.text(f"Status: {status}...")
                    time.sleep(3)
                else:
                    st.warning(f"Onbekende status: {status}")
                    time.sleep(3)
            except Exception as e:
                st.error(f"Fout tijdens wachten: {e}")
                return None

