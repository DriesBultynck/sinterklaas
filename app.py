import streamlit as st
from dotenv import load_dotenv
import os
import io
from pathlib import Path
import pandas as pd
import random
from datetime import datetime

# Import de nieuwe klassen
from message_generator import MessageGenerator
from audio_generator import AudioGenerator
from video_generator import VideoGenerator
from letter_generator import LetterGenerator

# Load environment variables
load_dotenv()

# Helper function to safely get secrets
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except:
        return default

# Initialize generators (optioneel - kan worden uitgeschakeld)
USE_MESSAGE_GENERATOR = True
USE_AUDIO_GENERATOR = True
USE_VIDEO_GENERATOR = False
USE_LETTER_GENERATOR = True

message_gen = None
audio_gen = None
video_gen = None
letter_gen = None

# Initialize MessageGenerator
if USE_MESSAGE_GENERATOR:
    api_key = os.getenv("OPENAI_API_KEY") or get_secret("OPENAI_API_KEY", "")
    if api_key:
        try:
            message_gen = MessageGenerator(api_key)
        except Exception as e:
            st.error(f"❌ MessageGenerator initialisatie mislukt: {e}")

# Initialize AudioGenerator
if USE_AUDIO_GENERATOR:
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") or get_secret("ELEVENLABS_API_KEY", "")
    elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID") or get_secret("ELEVENLABS_VOICE_ID", "")
    openai_key = os.getenv("OPENAI_API_KEY") or get_secret("OPENAI_API_KEY", "")
    if elevenlabs_key or openai_key:
        try:
            audio_gen = AudioGenerator(elevenlabs_key, elevenlabs_voice, openai_key)
        except Exception as e:
            st.warning(f"⚠️ AudioGenerator initialisatie mislukt: {e}")

# Initialize VideoGenerator
if USE_VIDEO_GENERATOR:
    heygen_key = os.getenv("HEYGEN_API_KEY") or get_secret("HEYGEN_API_KEY", "")
    heygen_avatar_id = os.getenv("HEYGEN_AVATAR_ID") or get_secret("HEYGEN_AVATAR_ID", "")
    if heygen_key:
        try:
            video_gen = VideoGenerator(heygen_key, avatar_id=heygen_avatar_id if heygen_avatar_id else None)
        except Exception as e:
            st.warning(f"⚠️ VideoGenerator initialisatie mislukt: {e}")

# Initialize LetterGenerator
if USE_LETTER_GENERATOR:
    try:
        letter_gen = LetterGenerator("sint-briefpapier.png")
    except Exception as e:
        st.warning(f"⚠️ LetterGenerator initialisatie mislukt: {e}")

# Page configuration
st.set_page_config(
    page_title="Sinterklaas boodschap",
    page_icon="",
    layout="centered"
)

# Custom CSS styling - Lichte interface
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #F5F5F5 0%, #FFFFFF 100%);
            background-attachment: fixed;
        }
        .main .block-container {
            background-color: #FFFFFF;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }
        h1 {
            color: #C41E3A;
            text-align: center;
            font-family: 'Georgia', serif;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
        }
    </style>
""", unsafe_allow_html=True)


# Title
st.markdown("# Sinterklaas Boodschap Generator")

# Check for Sinterklaas image
image_path = Path(__file__).parent / "sint.png"
if image_path.exists():
    st.image(str(image_path), use_container_width=True)
else:
    st.markdown("### *Afbeelding van Sinterklaas wordt hier getoond*")
    st.info("💡 Tip: Voeg een `sint.png` bestand toe aan deze map voor een mooie afbeelding!")

# Mode selection - Show only if no mode is selected yet
if 'app_mode' not in st.session_state:
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✍️ Schrijf zelf een brief als Sint", use_container_width=True, type="primary"):
            st.session_state['app_mode'] = 'manual'
            st.rerun()
    
    with col2:
        if st.button("🤖 Laat Sint een brief schrijven", use_container_width=True, type="primary"):
            st.session_state['app_mode'] = 'auto'
            st.rerun()
    
    st.stop()

# Continue based on selected mode
app_mode = st.session_state.get('app_mode')

# Manual mode - User writes their own message
if app_mode == 'manual':
    st.markdown("### ✍️ Schrijf je eigen Sinterklaas boodschap")
    
    with st.form("manual_message_form"):
        naam = st.text_input("Naam van het kind *", placeholder="Bijvoorbeeld: Emma")
        eigen_tekst = st.text_area(
            "Je eigen boodschap van Sinterklaas *",
            placeholder="Schrijf hier je eigen boodschap...",
            height=200,
            help="Schrijf je eigen persoonlijke boodschap van Sinterklaas"
        )
        
        submitted = st.form_submit_button("💾 Opslaan", use_container_width=True)
    
    if submitted:
        if not naam:
            st.error("⚠️ Vul ten minste de naam van het kind in.")
        elif not eigen_tekst:
            st.error("⚠️ Vul een boodschap in.")
        else:
            # Store in session state
            st.session_state['sinterklaas_tekst'] = eigen_tekst
            st.session_state['sinterklaas_tekst_aangepast'] = eigen_tekst
            st.session_state['tekst_generatie_klaar'] = True
            st.session_state['naam'] = naam
            st.rerun()
    
    # Show output selection after text is saved (manual mode)
    if st.session_state.get('sinterklaas_tekst') and not st.session_state.get('genereer_media', False):
        tekst = st.session_state.get('sinterklaas_tekst_aangepast', st.session_state.get('sinterklaas_tekst'))
        
        st.markdown("### 📜 De Boodschap van Sinterklaas")
        st.markdown(f'<div style="background-color: #FFF9E6; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #C41E3A; font-size: 1.1em; line-height: 1.6; color: #333; margin-bottom: 1rem;">{tekst}</div>', unsafe_allow_html=True)
        
        # Output selection checkboxes
        st.markdown("---")
        st.markdown("### 📤 Kies welke outputs je wilt genereren:")
        generate_audio = st.checkbox("🎵 Audio genereren", value=True, key="manual_output_audio")
        generate_video = False
        if USE_VIDEO_GENERATOR:
            generate_video = st.checkbox("🎥 Video genereren (HeyGen Ultra Quality)", value=False, key="manual_output_video")
            # Video vereist audio, dus als video is geselecteerd, audio ook inschakelen
            if generate_video and not generate_audio:
                st.info("ℹ️ Audio wordt automatisch gegenereerd voor video.")
                generate_audio = True
        generate_letter = st.checkbox("✉️ Brief genereren", value=True, key="manual_output_letter")
        
        # Button to generate selected outputs
        st.markdown("---")
        output_text = "🎁 Genereer "
        outputs = []
        if generate_audio:
            outputs.append("Audio")
        if generate_video:
            outputs.append("Video")
        if generate_letter:
            outputs.append("Brief")
        
        if outputs:
            output_text += ", ".join(outputs)
        else:
            output_text += "Outputs"
            st.warning("⚠️ Selecteer ten minste één output om te genereren.")
        
        if st.button(output_text, type="primary", use_container_width=True, disabled=len(outputs) == 0):
            # Store selected outputs in session state
            # Als video is geselecteerd, audio ook inschakelen
            st.session_state['generate_audio'] = generate_audio or generate_video
            st.session_state['generate_video'] = generate_video
            st.session_state['generate_letter'] = generate_letter
            st.session_state['genereer_media'] = True
            st.rerun()

# Auto mode - Let Sint write the message
elif app_mode == 'auto':
    # Input form
    with st.form("sinterklaas_form"):
        naam = st.text_input("Naam van het kind *", placeholder="Bijvoorbeeld: Emma")
        leeftijd = st.number_input("Leeftijd *", min_value=1, max_value=18, value=5)
        geslacht = st.selectbox("Geslacht *", ["Jongen", "Meisje"])
        anekdote = st.text_area(
            "Anekdote / In het grote boek",
            placeholder="Vertel iets over het kind dat Sinterklaas kan gebruiken in zijn boodschap...",
            height=100
        )
        verlanglijstje = st.text_area(
            "Verlanglijstje items (gescheiden door komma's)",
            placeholder="Bijvoorbeeld: Lego, Playmobil, een fiets, een boek, Star Wars speelgoed...",
            height=80,
            help="Voer de items van het verlanglijstje in. De Sint kan bekende quotes of spreuken gebruiken bij deze items!"
        )
        zeker_item = st.text_input(
            "Iets wat het kind absoluut leuk vindt of zeker zal krijgen",
            placeholder="Bijvoorbeeld: een nieuwe fiets, een Playstation, een puppy...",
            help="Iets speciaals dat het kind zeker zal krijgen of waar het heel blij van wordt!"
        )
        schoentje_gezet = st.radio(
            "Heeft het kind al een schoentje gezet met verlanglijstje?",
            ["Ja", "Nee"],
            help="Als het kind nog geen schoentje heeft gezet en er is geen verlanglijstje, kan de Sint hiernaar verwijzen."
        )
        slang_toggle = st.toggle("💬 Gebruik slang/hip taal (Gen Z)", value=True, help="Zet uit voor traditionele Vlaamse begroetingen en afsluitingen")
        
        submitted = st.form_submit_button("🎁 Genereer Sinterklaas Boodschap", use_container_width=True)

if submitted:
    if not naam:
        st.error("⚠️ Vul ten minste de naam van het kind in.")
    elif not message_gen:
        st.error("⚠️ MessageGenerator niet geïnitialiseerd. Voeg `OPENAI_API_KEY` toe aan `.env` of `st.secrets`.")
    else:
        with st.spinner("Sinterklaas neemt z'n pen en brief en schrijft zijn boodschap... even geduld, aub."):
            try:
                # Generate text using MessageGenerator
                tekst = message_gen.generate(
                    naam=naam,
                    leeftijd=leeftijd,
                    geslacht=geslacht,
                    anekdote=anekdote if anekdote else "(Geen specifieke notitie)",
                    verlanglijstje=verlanglijstje if verlanglijstje else "(Geen verlanglijstje)",
                    zeker_item=zeker_item if zeker_item else "(Geen specifiek item)",
                    schoentje_gezet="Ja" if schoentje_gezet == "Ja" else "Nee",
                    slang_toggle=slang_toggle
                )
                
                # Store in session state
                st.session_state['sinterklaas_tekst'] = tekst
                st.session_state['tekst_generatie_klaar'] = True
                st.session_state['naam'] = naam
                
            except Exception as e:
                st.error(f"❌ Er is een fout opgetreden bij tekst generatie: {str(e)}")
                st.info("Controleer of je OpenAI API key geldig is en of je credits hebt.")
                tekst = None

# Display the text and allow editing (only for auto mode, outside submitted block, so it persists after rerun)
if app_mode == 'auto' and st.session_state.get('sinterklaas_tekst'):
    tekst = st.session_state['sinterklaas_tekst']
    
    # Only show editor if we're not generating media yet
    if not st.session_state.get('genereer_media', False):
        # Display the text and allow editing
        st.markdown("### 📜 De Boodschap van Sinterklaas")
        st.markdown(f'<div style="background-color: #FFF9E6; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #C41E3A; font-size: 1.1em; line-height: 1.6; color: #333; margin-bottom: 1rem;">{tekst}</div>', unsafe_allow_html=True)
        
        # Allow user to edit the text
        st.markdown("**✏️ Pas de tekst aan (optioneel):**")
        tekst_aangepast = st.text_area(
            "Bewerk de boodschap van Sinterklaas",
            value=tekst,
            height=200,
            help="Pas de tekst aan voordat audio, video en brief worden gegenereerd.",
            label_visibility="collapsed",
            key="tekst_editor"
        )
        
        # Store edited text
        st.session_state['sinterklaas_tekst_aangepast'] = tekst_aangepast
        
        if tekst_aangepast.strip() != tekst.strip():
            st.info("ℹ️ Je hebt de tekst aangepast. De aangepaste versie wordt gebruikt voor audio, video en brief.")
        
        # Output selection checkboxes after text editing
        st.markdown("---")
        st.markdown("### 📤 Kies welke outputs je wilt genereren:")
        generate_audio = st.checkbox("🎵 Audio genereren", value=True, key="output_audio")
        generate_video = False
        if USE_VIDEO_GENERATOR:
            generate_video = st.checkbox("🎥 Video genereren (HeyGen Ultra Quality)", value=False, key="output_video")
            # Video vereist audio, dus als video is geselecteerd, audio ook inschakelen
            if generate_video and not generate_audio:
                st.info("ℹ️ Audio wordt automatisch gegenereerd voor video.")
                generate_audio = True
        generate_letter = st.checkbox("✉️ Brief genereren", value=True, key="output_letter")
        
        # Button to generate selected outputs
        st.markdown("---")
        output_text = "🎁 Genereer "
        outputs = []
        if generate_audio:
            outputs.append("Audio")
        if generate_video:
            outputs.append("Video")
        if generate_letter:
            outputs.append("Brief")
        
        if outputs:
            output_text += ", ".join(outputs)
        else:
            output_text += "Outputs"
            st.warning("⚠️ Selecteer ten minste één output om te genereren.")
        
        if st.button(output_text, type="primary", use_container_width=True, disabled=len(outputs) == 0):
            # Store selected outputs in session state
            # Als video is geselecteerd, audio ook inschakelen
            st.session_state['generate_audio'] = generate_audio or generate_video
            st.session_state['generate_video'] = generate_video
            st.session_state['generate_letter'] = generate_letter
            st.session_state['genereer_media'] = True
            st.rerun()

# Generate audio, video and letter if button was clicked
if st.session_state.get('genereer_media', False):
    # Get the final text (edited or original)
    final_tekst = st.session_state.get('sinterklaas_tekst_aangepast', st.session_state.get('sinterklaas_tekst', ''))
    
    if not final_tekst:
        st.error("❌ Geen tekst beschikbaar om audio, video en brief te genereren.")
    else:
        # Generate audio if selected OR if video is selected (video requires audio)
        audio_bytes = None
        generate_audio = st.session_state.get('generate_audio', True)
        generate_video = st.session_state.get('generate_video', False) and USE_VIDEO_GENERATOR
        # Video vereist audio, dus audio altijd genereren als video wordt gegenereerd
        if generate_video:
            generate_audio = True
        
        if generate_audio:
            with st.spinner("🎤 Sinterklaas spreekt..."):
                if not audio_gen:
                    st.error("❌ AudioGenerator niet geïnitialiseerd. Configureer ElevenLabs of OpenAI API key.")
                else:
                    try:
                        audio_bytes = audio_gen.generate(final_tekst, prefer_elevenlabs=True)
                    except Exception as e:
                        error_msg = str(e)
                        # Show specific error messages
                        if "authenticatie" in error_msg.lower() or "401" in error_msg:
                            st.error(f"❌ **ElevenLabs authenticatie fout**\n\nControleer je API key in `.env` of `st.secrets`.\n\n*Fout: {error_msg[:150]}*")
                        elif "Voice ID" in error_msg or "404" in error_msg:
                            st.error(f"❌ **ElevenLabs Voice ID fout**\n\nVoice ID niet gevonden. Controleer of de Voice ID correct is.\n\n*Fout: {error_msg[:150]}*")
                        elif "rate limit" in error_msg.lower() or "429" in error_msg:
                            st.warning(f"⚠️ **ElevenLabs rate limit bereikt**\n\nProbeer over een paar minuten opnieuw.\n\n*Fout: {error_msg[:150]}*")
                        elif "quota" in error_msg.lower() or "quota_exceeded" in error_msg.lower():
                            st.warning(f"⚠️ **ElevenLabs quota overschreden**\n\nJe account heeft niet genoeg credits. Gebruik OpenAI TTS als backup.\n\n*Fout: {error_msg[:150]}*")
                        else:
                            st.warning(f"⚠️ **Audio generatie fout**\n\n*Fout: {error_msg[:150]}*")
        
        # Handle video generation if selected and enabled
        # generate_video is al hierboven gedefinieerd
        if generate_video:
            if not audio_bytes:
                st.warning("⚠️ Audio is vereist voor video generatie. Genereer eerst audio.")
            else:
                sint_image_path = Path(__file__).parent / "sint.png"
                if not video_gen:
                    st.warning("⚠️ VideoGenerator niet geïnitialiseerd. Voeg `HEYGEN_API_KEY` toe aan je `.env` om video te genereren.")
                    if audio_bytes:
                        st.markdown("### 🎵 Luister naar Sinterklaas")
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                else:
                    if sint_image_path.exists():
                        st.image(str(sint_image_path), use_container_width=True, caption="🎅 Sinterklaas bereidt zich voor...")
                    with st.spinner("🎬 HeyGen maakt een ultra-realistische video... even geduld (30-90 seconden)"):
                        try:
                            # Create a copy of audio_bytes to avoid pointer issues
                            if hasattr(audio_bytes, 'getvalue'):
                                audio_bytes.seek(0)
                                audio_bytes_copy = io.BytesIO(audio_bytes.getvalue())
                            elif hasattr(audio_bytes, 'read'):
                                audio_bytes.seek(0)
                                audio_bytes_copy = io.BytesIO(audio_bytes.read())
                            else:
                                audio_bytes_copy = io.BytesIO(audio_bytes)
                            
                            video_url = video_gen.generate(audio_bytes_copy, str(sint_image_path))
                            if video_url:
                                st.markdown("### 🎥 Sinterklaas in HeyGen Ultra Quality")
                                st.video(video_url)
                                
                                # Toon ook audio player if audio was generated
                                if generate_audio and audio_bytes:
                                    st.markdown("### 🎵 Luister naar Sinterklaas")
                                    audio_bytes.seek(0)
                                    st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                                    # Download button voor audio
                                    audio_bytes.seek(0)
                                    st.download_button(
                                        label="📥 Download Audio",
                                        data=audio_bytes.getvalue() if hasattr(audio_bytes, 'getvalue') else audio_bytes.read(),
                                        file_name=f"sinterklaas_audio_{st.session_state.get('naam', 'kind')}_{datetime.now().strftime('%Y%m%d')}.mp3",
                                        mime="audio/mpeg",
                                        use_container_width=True
                                    )
                            else:
                                st.warning("⚠️ Video generatie mislukt.")
                                if generate_audio and audio_bytes:
                                    st.markdown("### 🎵 Luister naar Sinterklaas")
                                    audio_bytes.seek(0)
                                    st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                                    # Download button voor audio
                                    audio_bytes.seek(0)
                                    st.download_button(
                                        label="📥 Download Audio",
                                        data=audio_bytes.getvalue() if hasattr(audio_bytes, 'getvalue') else audio_bytes.read(),
                                        file_name=f"sinterklaas_audio_{st.session_state.get('naam', 'kind')}_{datetime.now().strftime('%Y%m%d')}.mp3",
                                        mime="audio/mpeg",
                                        use_container_width=True
                                    )
                        except Exception as video_error:
                            st.error(f"❌ HeyGen video generatie mislukt: {str(video_error)}")
                            if generate_audio and audio_bytes:
                                st.info("Toon alleen audio als fallback.")
                                st.markdown("### 🎵 Luister naar Sinterklaas")
                                audio_bytes.seek(0)
                                st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                                # Download button voor audio
                                audio_bytes.seek(0)
                                st.download_button(
                                    label="📥 Download Audio",
                                    data=audio_bytes.getvalue() if hasattr(audio_bytes, 'getvalue') else audio_bytes.read(),
                                    file_name=f"sinterklaas_audio_{st.session_state.get('naam', 'kind')}_{datetime.now().strftime('%Y%m%d')}.mp3",
                                    mime="audio/mpeg",
                                    use_container_width=True
                                )
        
        # Show audio player if audio was generated but video was not
        if generate_audio and audio_bytes and not generate_video:
            sint_image_path = Path(__file__).parent / "sint.png"
            if sint_image_path.exists():
                st.image(str(sint_image_path), use_container_width=True)
            st.markdown("### 🎵 Luister naar Sinterklaas")
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3", autoplay=False)
            # Download button voor audio
            audio_bytes.seek(0)
            st.download_button(
                label="📥 Download Audio",
                data=audio_bytes.getvalue() if hasattr(audio_bytes, 'getvalue') else audio_bytes.read(),
                file_name=f"sinterklaas_audio_{st.session_state.get('naam', 'kind')}_{datetime.now().strftime('%Y%m%d')}.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
        
        # Render the parchment-style letter if selected
        generate_letter = st.session_state.get('generate_letter', True)
        if generate_letter:
            if not letter_gen:
                st.warning("⚠️ LetterGenerator niet geïnitialiseerd.")
            else:
                letter_html = letter_gen.generate_html(final_tekst)
                st.markdown("### ✉️ Officiële Sinterklaasbrief")
                st.markdown(letter_html, unsafe_allow_html=True)
                
                # PDF Download button
                try:
                    from playwright.sync_api import sync_playwright
                    from datetime import datetime
                    import io
                    import tempfile
                    import os
                    
                    # Create a temporary HTML file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_html:
                        tmp_html.write(letter_html)
                        tmp_html_path = tmp_html.name
                    
                    try:
                        # Use Playwright to generate PDF in A4 format
                        with sync_playwright() as p:
                            browser = p.chromium.launch(headless=True)
                            # Set viewport to A4 dimensions (210mm x 297mm at 96 DPI ≈ 794x1123px)
                            page = browser.new_page(viewport={'width': 794, 'height': 1123}, device_scale_factor=1)
                            page.goto(f"file://{tmp_html_path}")
                            # Wait for fonts and images to load
                            page.wait_for_load_state('networkidle')
                            page.wait_for_timeout(2000)  # Extra time for fonts to load
                            # Generate PDF in A4 format with proper scaling
                            pdf_bytes = page.pdf(
                                format='A4',
                                print_background=True,
                                margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
                                scale=1.0,
                                prefer_css_page_size=True  # Use CSS @page size
                            )
                            browser.close()
                        
                        st.download_button(
                            label="📥 Download Brief als PDF",
                            data=pdf_bytes,
                            file_name=f"sinterklaas_brief_{st.session_state.get('naam', 'kind')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    finally:
                        # Clean up temp file
                        if os.path.exists(tmp_html_path):
                            os.unlink(tmp_html_path)
                except ImportError:
                    st.info("💡 **PDF download beschikbaar** - Installeer `playwright` voor PDF download functionaliteit: `pip install playwright && playwright install chromium`")
                except Exception as pdf_error:
                    st.warning(f"⚠️ PDF generatie mislukt: {str(pdf_error)[:200]}")
                    st.info("💡 Probeer: `pip install playwright && playwright install chromium`")
        
        # Reset flag
        st.session_state['genereer_media'] = False
        
        # Add button to go back to mode selection
        st.markdown("---")
        if st.button("🔄 Terug naar modus selectie", use_container_width=True):
            st.session_state.pop('app_mode', None)
            st.session_state.pop('sinterklaas_tekst', None)
            st.session_state.pop('sinterklaas_tekst_aangepast', None)
            st.session_state.pop('genereer_media', None)
            st.rerun()

