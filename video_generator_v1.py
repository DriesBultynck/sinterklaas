import os
import tempfile
import time
import json
import requests
from typing import Optional
import streamlit as st


class VideoGeneratorV1:
    """Video generator gebaseerd op de HeyGen API v1 (geschikt voor photo avatars)."""

    def __init__(
        self,
        api_key: str,
        avatar_id: str,
        *,
        avatar_type: str = "avatar",
        background_color: str = "#FFFFFF",
        aspect_ratio: str = "16:9",
        width: int = 1280,
        height: int = 720,
        test_mode: bool = False,
    ):
        if not api_key:
            raise ValueError("HeyGen API key is vereist")
        if not avatar_id:
            raise ValueError("Avatar of photo ID is vereist voor de v1 implementatie")

        self.api_key = api_key.strip()
        self.avatar_id = avatar_id.strip()
        self.avatar_type = avatar_type.lower()
        if self.avatar_type not in {"avatar", "photo"}:
            st.warning(
                f"Onbekend avatar_type '{avatar_type}', fallback naar 'avatar'"
            )
            self.avatar_type = "avatar"

        self.background_color = background_color
        self.aspect_ratio = aspect_ratio
        self.dimension = {"width": width, "height": height}
        self.test_mode = test_mode

    def generate(self, audio_bytes) -> Optional[str]:
        """Genereer een video met de HeyGen v1 API."""
        data = self._peek_audio(audio_bytes)
        if not data:
            st.error("❌ Audio data is leeg!")
            return None

        st.info(f"📊 Audio grootte: {len(data)} bytes")

        audio_asset_id = self._upload_asset(audio_bytes, "audio/mpeg")
        if not audio_asset_id:
            st.error("❌ Audio upload mislukt, kan niet starten met genereren.")
            return None

        video_id = self._start_generation_v1(audio_asset_id)
        if not video_id:
            return None

        return self._poll_for_completion(video_id)

    # --- Helpers -----------------------------------------------------------

    def _peek_audio(self, audio_bytes):
        if hasattr(audio_bytes, "getvalue"):
            return audio_bytes.getvalue()
        if hasattr(audio_bytes, "read"):
            try:
                audio_bytes.seek(0)
            except (OSError, AttributeError):
                pass
            data = audio_bytes.read()
            audio_bytes.seek(0)
            return data
        return audio_bytes

    def _upload_asset(self, file_data, content_type: str) -> Optional[str]:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_filename = temp_file.name

        try:
            if hasattr(file_data, "getvalue"):
                data = file_data.getvalue()
            elif hasattr(file_data, "read"):
                try:
                    file_data.seek(0)
                except (OSError, AttributeError):
                    pass
                data = file_data.read()
            else:
                data = file_data

            if isinstance(data, str):
                data = data.encode("utf-8")

            if not data:
                st.error("❌ Geen audiogegevens beschikbaar om te uploaden.")
                return None

            temp_file.write(data)
            temp_file.close()

            st.info(f"💾 Temp bestand aangemaakt: {len(data)} bytes")

            return self._upload_file_to_api(temp_filename, content_type)
        finally:
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except Exception:
                    pass

    def _upload_file_to_api(self, file_path: str, content_type: str) -> Optional[str]:
        if not os.path.exists(file_path):
            st.error(f"❌ Bestand niet gevonden: {file_path}")
            return None

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            st.error("❌ Bestand is leeg!")
            return None

        st.info(f"📤 Bestandsgrootte: {file_size} bytes")

        upload_url = "https://upload.heygen.com/v1/asset"
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": content_type,
        }

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            response = requests.post(
                upload_url,
                headers=headers,
                data=file_content,
                timeout=120,
            )

            if response.status_code == 200:
                json_data = response.json()
                if "data" in json_data and "id" in json_data["data"]:
                    asset_id = json_data["data"]["id"]
                    st.success(f"✅ Audio geüpload! Asset ID: {asset_id}")
                    return asset_id

                st.error(f"❌ Onverwacht response format: {json_data}")
                return None

            st.error(f"❌ Upload Error ({response.status_code}): {response.text}")
            return None
        except Exception as e:
            st.error(f"❌ Exception bij upload: {str(e)}")
            return None

    def _start_generation_v1(self, audio_asset_id: str) -> Optional[str]:
        generate_url = "https://api.heygen.com/v1/video.generate"

        character_payload = (
            {"type": "photo", "photo_id": self.avatar_id}
            if self.avatar_type == "photo"
            else {"type": "avatar", "avatar_id": self.avatar_id}
        )

        payload = {
            "character": character_payload,
            "voice": {
                "type": "audio",
                "audio_asset_id": audio_asset_id,
            },
            "background": {
                "type": "color",
                "value": self.background_color,
            },
            "aspect_ratio": self.aspect_ratio,
            "dimension": self.dimension,
            "test": self.test_mode,
        }

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                generate_url,
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 200:
                json_data = response.json()
                if "data" in json_data and "video_id" in json_data["data"]:
                    video_id = json_data["data"]["video_id"]
                    st.success(f"✅ v1 job gestart! Video ID: {video_id}")
                    return video_id

                st.error(f"❌ Onverwacht response format: {json_data}")
                return None

            st.error(f"❌ Generatie mislukt ({response.status_code}): {response.text}")
            return None
        except Exception as e:
            st.error(f"❌ Fout bij v1 video generatie: {str(e)}")
            return None

    def _poll_for_completion(self, video_id: str) -> Optional[str]:
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
                    status_text.text("⏳ Wachten op data...")
                    time.sleep(5)
                    continue

                data = json_data["data"]
                status = data.get("status")

                if status == "completed":
                    progress_bar.progress(100)
                    status_text.text("Status: Klaar!")
                    video_url = data.get("video_url")
                    st.success("🎥 Video is klaar!")
                    return video_url

                if status == "failed":
                    error_msg = data.get("error", "Onbekende fout")
                    st.error(f"❌ Renderen mislukt: {error_msg}")
                    return None

                status_text.text(f"Status: {status}... (even geduld)")
                progress_value = min(progress_value + 5, 90)
                progress_bar.progress(progress_value)
                time.sleep(5)

            except Exception as e:
                st.error(f"Polling fout: {e}")
                time.sleep(5)
                continue

