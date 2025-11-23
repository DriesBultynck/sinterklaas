# 🎅 Sinterklaas Boodschap Generator

Een interactieve Streamlit applicatie waarmee je persoonlijke Sinterklaas boodschappen kunt genereren, inclusief audio, video en geschreven brieven.

## ✨ Features

- **🤖 Automatische boodschap generatie**: Laat Sinterklaas een gepersonaliseerde boodschap schrijven op basis van kindgegevens
- **✍️ Handmatige modus**: Schrijf je eigen Sinterklaas boodschap
- **🎵 Audio generatie**: Genereer audio met ElevenLabs of OpenAI TTS
- **🎥 Video generatie**: Maak realistische video's met HeyGen (optioneel)
- **✉️ Brief generatie**: Genereer mooie, perkament-stijl brieven met downloadbare PDF
- **💬 Slang/hip taal optie**: Kies tussen traditioneel Vlaams of moderne Gen Z/Alpha slang
- **📝 Tekst bewerking**: Pas de gegenereerde boodschap aan voordat je outputs genereert

## 🚀 Installatie

### Vereisten

- Python 3.8 of hoger
- pip

### Stappen

1. **Clone de repository:**
```bash
git clone https://github.com/DriesBultynck/sinterklaa.git
cd sinterklaa
```

2. **Installeer dependencies:**
```bash
pip install -r requirements.txt
```

3. **Installeer Playwright (voor PDF generatie):**
```bash
playwright install chromium
```

4. **Installeer ffmpeg (vereist voor audio padding):**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download van https://ffmpeg.org/download.html
```

5. **Maak een `.env` bestand aan:**
```bash
cp .env.template .env
```

6. **Vul je API keys en login credentials in het `.env` bestand:**
```env
# Login credentials (vereist)
APP_USERNAME=je-gebruikersnaam
APP_PASSWORD=je-wachtwoord

# Vereist voor tekst generatie
OPENAI_API_KEY=sk-...

# Voor audio generatie (optioneel - gebruikt OpenAI als fallback)
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=...

# Voor video generatie (optioneel)
HEYGEN_API_KEY=sk_...
HEYGEN_AVATAR_ID=...
```

## 📖 Gebruik

### Start de applicatie

```bash
streamlit run app.py
```

De applicatie opent automatisch in je browser op `http://localhost:8501`

### Twee modi

#### 1. 🤖 Laat Sint een brief schrijven (Automatisch)
- Vul de gegevens van het kind in
- Kies of je slang/hip taal wilt gebruiken
- Genereer de boodschap
- Pas de tekst aan (optioneel)
- Kies welke outputs je wilt genereren (Audio, Video, Brief)

#### 2. ✍️ Schrijf zelf een brief als Sint (Handmatig)
- Schrijf je eigen boodschap
- Kies welke outputs je wilt genereren (Audio, Video, Brief)

## 🎛️ Configuratie

In `app.py` kun je optionele generators uitschakelen:

```python
USE_MESSAGE_GENERATOR = True   # Tekst generatie
USE_AUDIO_GENERATOR = True      # Audio generatie
USE_VIDEO_GENERATOR = False     # Video generatie (HeyGen)
USE_LETTER_GENERATOR = True     # Brief generatie
```

Als `USE_VIDEO_GENERATOR = False`, verschijnt de video optie niet in de UI.

## 📁 Project Structuur

```
sinterklaas/
├── app.py                  # Hoofdapplicatie
├── message_generator.py   # GPT-4o tekst generatie
├── audio_generator.py     # ElevenLabs/OpenAI TTS
├── video_generator.py     # HeyGen video generatie
├── letter_generator.py    # HTML brief generatie
├── requirements.txt       # Python dependencies
├── README.md             # Deze file
├── sint.png              # Sinterklaas afbeelding
└── sint-briefpapier.png  # Briefpapier achtergrond
```

## 🔧 API Keys

### OpenAI (Vereist)
- Gebruikt voor tekst generatie (GPT-4o)
- Fallback voor audio generatie (TTS-1-HD)
- [Krijg je API key hier](https://platform.openai.com/api-keys)

### ElevenLabs (Optioneel)
- Voor betere audio kwaliteit
- [Krijg je API key hier](https://elevenlabs.io/app/settings/api-keys)

### HeyGen (Optioneel)
- Voor video generatie
- [Krijg je API key hier](https://app.heygen.com/settings/api-keys)

## 🎨 Features in Detail

### Tekst Generatie
- Gebruikt GPT-4o voor natuurlijke, persoonlijke boodschappen
- Ondersteunt Vlaams idioom en optionele Gen Z/Alpha slang
- Contextuele aanbevelingen op basis van anekdotes
- Verwijzingen naar verlanglijstjes met bekende quotes

### Audio Generatie
- **ElevenLabs**: Hoge kwaliteit, meertalig (eleven_multilingual_v2)
- **OpenAI TTS**: Fallback optie (tts-1-hd, voice: onyx)
- Automatische fallback als ElevenLabs niet beschikbaar is
- **Audio padding**: Voegt automatisch 1.5 seconden stilte toe aan het einde voor volledige downloads

### Video Generatie
- HeyGen Ultra Quality talking photo
- Gebruikt avatar ID of geüploade afbeelding
- Automatische polling tot video klaar is

### Brief Generatie
- Perkament-stijl HTML brief
- Google Fonts (Pinyon Script, Herr Von Muellerhoff)
- PDF download functionaliteit
- Exacte afmetingen (1696x2528px)

## 🐛 Troubleshooting

### PDF generatie werkt niet
```bash
pip install playwright
playwright install chromium
```

### ElevenLabs quota overschreden
De app valt automatisch terug op OpenAI TTS.

### HeyGen video upload fout
Controleer of je API key correct is en of je avatar ID geldig is.

### Audio padding werkt niet
Zorg ervoor dat ffmpeg geïnstalleerd is. Zie installatie instructies hierboven.

## 📝 Licentie

Dit project is voor persoonlijk gebruik.

## 👤 Auteur

Dries Bultynck

## 🙏 Credits

- OpenAI voor GPT-4o en TTS
- ElevenLabs voor high-quality voice synthesis
- HeyGen voor video generatie
- Streamlit voor het framework
