import io
from typing import Optional
from elevenlabs.client import ElevenLabs
import openai


class AudioGenerator:
    """Klasse voor het genereren van audio met ElevenLabs of OpenAI TTS."""
    
    def __init__(
        self,
        elevenlabs_api_key: Optional[str] = None,
        elevenlabs_voice_id: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialiseer de AudioGenerator.
        
        Args:
            elevenlabs_api_key: ElevenLabs API key (optioneel)
            elevenlabs_voice_id: ElevenLabs Voice ID (optioneel)
            openai_api_key: OpenAI API key voor fallback (optioneel)
        """
        self.elevenlabs_client = None
        self.elevenlabs_voice_id = elevenlabs_voice_id
        self.openai_client = None
        
        if elevenlabs_api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
            except Exception as e:
                print(f"Warning: ElevenLabs client initialisatie mislukt: {e}")
        
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
    
    def generate(self, text: str, prefer_elevenlabs: bool = True) -> io.BytesIO:
        """
        Genereer audio van tekst.
        
        Args:
            text: De tekst om te converteren naar audio
            prefer_elevenlabs: Of ElevenLabs geprefereerd wordt (True) of OpenAI (False)
        
        Returns:
            Audio bytes als io.BytesIO object
        
        Raises:
            ValueError: Als geen audio engine beschikbaar is
        """
        # Try ElevenLabs first if preferred and available
        if prefer_elevenlabs and self.elevenlabs_client and self.elevenlabs_voice_id:
            try:
                return self._generate_elevenlabs(text)
            except Exception as e:
                error_msg = str(e)
                # Fallback to OpenAI if ElevenLabs fails
                if self.openai_client:
                    print(f"ElevenLabs fout, gebruik OpenAI TTS: {error_msg}")
                    return self._generate_openai(text)
                else:
                    raise ValueError(f"ElevenLabs fout en geen OpenAI fallback: {error_msg}")
        
        # Use OpenAI if available
        if self.openai_client:
            return self._generate_openai(text)
        
        raise ValueError("Geen audio engine beschikbaar. Configureer ElevenLabs of OpenAI API key.")
    
    def _generate_elevenlabs(self, text: str) -> io.BytesIO:
        """Genereer audio met ElevenLabs."""
        if not self.elevenlabs_client:
            raise ValueError("ElevenLabs client niet geïnitialiseerd")
        if not self.elevenlabs_voice_id:
            raise ValueError("ElevenLabs Voice ID niet gevonden")
        
        audio_generator = self.elevenlabs_client.text_to_speech.convert(
            voice_id=self.elevenlabs_voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            text=text
        )
        
        audio_bytes = io.BytesIO()
        for chunk in audio_generator:
            audio_bytes.write(chunk)
        audio_bytes.seek(0)
        
        return audio_bytes
    
    def _generate_openai(self, text: str) -> io.BytesIO:
        """Genereer audio met OpenAI TTS."""
        if not self.openai_client:
            raise ValueError("OpenAI client niet geïnitialiseerd")
        
        audio_response = self.openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            speed=0.85,
            input=text
        )
        
        audio_bytes = io.BytesIO(audio_response.content)
        audio_bytes.seek(0)
        return audio_bytes

