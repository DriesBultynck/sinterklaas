from datetime import datetime
import re
from typing import Optional
from pathlib import Path
import base64


class LetterGenerator:
    """Klasse voor het genereren van Sinterklaas brieven in HTML formaat."""
    
    def __init__(self, background_image_path: str = "sint-briefpapier.png"):
        """
        Initialiseer de LetterGenerator.
        
        Args:
            background_image_path: Pad naar de achtergrondafbeelding
        """
        self.background_image_path = background_image_path
    
    def generate_html(self, text_content: str) -> str:
        """
        Genereer HTML voor de brief.
        
        Args:
            text_content: De tekstinhoud van de brief
        
        Returns:
            HTML string
        """
        # Get date
        date_str = self._get_dutch_date()
        
        # Process text
        greeting, paragraphs = self._process_text(text_content)
        
        # Build HTML
        return self._build_html(date_str, greeting, paragraphs)
    
    def _get_dutch_date(self) -> str:
        """Krijg de huidige datum in Nederlands formaat."""
        today = datetime.now()
        date_str = today.strftime("%d %B %Y")
        months = {
            "January": "januari", "February": "februari", "March": "maart",
            "April": "april", "May": "mei", "June": "juni",
            "July": "juli", "August": "augustus", "September": "september",
            "October": "oktober", "November": "november", "December": "december"
        }
        for eng, dutch in months.items():
            date_str = date_str.replace(eng, dutch)
        return date_str
    
    def _process_text(self, text_content: str) -> tuple[Optional[str], list[str]]:
        """Verwerk tekst en split in greeting en paragrafen."""
        # Remove closing
        closing_patterns = [
            r'[Tt]ot gauw[,\s]*[Hh]oogachtend[,\s]*[Ss]interklaas',
            r'[Tt]ot gauw[,\s]*[Hh]oogachtend',
            r'[Hh]oogachtend[,\s]*[Ss]interklaas'
        ]
        for pattern in closing_patterns:
            text_content = re.sub(pattern, '', text_content, flags=re.IGNORECASE)
        
        # Clean up
        text_content = ' '.join(text_content.split()).strip()
        
        # Split into sentences
        sentences = re.split(r'([.!?]\s+)', text_content)
        combined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                combined_sentences.append(sentences[i] + sentences[i + 1])
            else:
                combined_sentences.append(sentences[i])
        if len(sentences) % 2 == 1:
            combined_sentences.append(sentences[-1])
        
        combined_sentences = [s.strip() for s in combined_sentences if s.strip()]
        
        # Get greeting and body
        greeting = combined_sentences[0].rstrip(',') if combined_sentences else None
        body_sentences = combined_sentences[1:] if len(combined_sentences) > 1 else []
        
        # Group into paragraphs
        paragraphs = []
        if len(body_sentences) <= 2:
            paragraphs.append(' '.join(body_sentences))
        elif len(body_sentences) <= 4:
            paragraphs.append(' '.join(body_sentences[:2]))
            paragraphs.append(' '.join(body_sentences[2:]))
        else:
            paragraphs.append(' '.join(body_sentences[:2]))
            paragraphs.append(' '.join(body_sentences[2:4]))
            paragraphs.append(' '.join(body_sentences[4:]))
        
        return greeting, paragraphs
    
    def _build_html(self, date_str: str, greeting: Optional[str], paragraphs: list[str]) -> str:
        """Bouw de HTML string."""
        # Load background image as base64
        background_path = Path(self.background_image_path)
        if not background_path.is_absolute():
            # Relative path - assume it's relative to the script location
            background_path = Path(__file__).parent / self.background_image_path
        
        background_image_url = ""
        if background_path.exists():
            with open(background_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                background_image_url = f"data:image/png;base64,{img_data}"
        
        paragraphs_html = []
        if greeting:
            paragraphs_html.append(f'        <p class="greeting">{greeting}</p>')
        
        for i, p in enumerate(paragraphs, 1):
            if p.strip():
                paragraphs_html.append(f'        <p class="paragraph-{i}">{p}</p>')
        
        paragraphs_html.append('        <p class="closing">Tot gauw</p>')
        paragraphs_html.append('        <p class="signature-line">Hoogachtend</p>')
        paragraphs_html.append('        <p class="signature-name">Sinterklaas</p>')
        
        paragraphs_html_str = '\n'.join(paragraphs_html)
        
        return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Herr+Von+Muellerhoff&display=swap');
    .letter-container {{
        background-image: url('{background_image_url}');
        background-size: 100% 100%;
        background-repeat: no-repeat;
        background-position: center;
        width: 1696px;
        height: auto;
        aspect-ratio: 1696 / 2528;
        padding: 200px 80px 60px 80px;
        color: #3b2f2f;
        font-family: 'Pinyon Script', cursive;
        font-size: 24px;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-radius: 2px;
        margin: 2rem auto;
        box-sizing: border-box;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}
    /* PDF specific - ensure exact rendering */
    @media print {{
        .letter-container {{
            width: 1696px !important;
            height: 2528px !important;
            max-height: 2528px !important;
            font-size: 24px !important;
            padding: 200px 80px 60px 80px !important;
            margin: 0 !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }}
    }}
    .letter-container p {{
        margin-bottom: 0.8em;
        text-align: justify;
        font-size: 1em;
        flex-shrink: 0;
    }}
    /* Responsive styling for web display only */
    @media (max-width: 1800px) {{
        .letter-container {{
            width: min(1696px, 100%);
            height: auto;
            aspect-ratio: 1696 / 2528;
            background-size: 100% 100%;
            font-size: calc(24px * (100vw / 1696px));
            padding: calc(200px * (100vw / 1696px)) calc(80px * (100vw / 1696px)) calc(60px * (100vw / 1696px)) calc(80px * (100vw / 1696px));
        }}
    }}
    /* PDF/Print: Force exact dimensions and styling */
    @page {{
        size: 1696px 2528px;
        margin: 0;
    }}
    @media print {{
        .letter-container p {{
            font-size: 24px !important;
            margin-bottom: 0.8em !important;
        }}
        .greeting {{
            font-size: 24px !important;
            margin-bottom: 1.5em !important;
        }}
        .closing {{
            font-size: 24px !important;
        }}
        .signature-line {{
            font-size: 24px !important;
        }}
        .signature-name {{
            font-size: 36px !important;
        }}
    }}
    .letter-date {{
        position: absolute;
        top: 120px;
        right: 80px;
        font-size: 18px;
        color: #3b2f2f;
        font-family: 'Pinyon Script', cursive;
    }}
    /* Responsive date for web display */
    @media (max-width: 1800px) {{
        .letter-date {{
            top: calc(120px * (100vw / 1696px));
            right: calc(80px * (100vw / 1696px));
            font-size: calc(18px * (100vw / 1696px));
        }}
    }}
    /* PDF/Print: Force exact date position */
    @media print {{
        .letter-date {{
            top: 120px !important;
            right: 80px !important;
            font-size: 18px !important;
        }}
    }}
    .greeting {{
        margin-bottom: 1.5em;
    }}
    .closing {{
        margin-top: 2em;
        margin-bottom: 0.5em;
    }}
    .signature-line {{
        margin-bottom: 0.3em;
        text-align: right;
    }}
    .signature-name {{
        margin-bottom: 0;
        text-align: right;
        font-family: 'Herr Von Muellerhoff', cursive;
        font-size: 36px;
        color: #8B0000;
    }}
    .signature-area {{
        margin-top: 40px;
        text-align: right;
        position: relative;
    }}
    .sint-signature {{
        font-family: 'Herr Von Muellerhoff', cursive;
        font-size: 50px;
        color: #8B0000;
        margin-right: 20px;
    }}
    .seal-image {{
        position: absolute;
        bottom: -20px;
        right: 10px;
        width: 120px;
        opacity: 0.9;
        transform: rotate(-10deg);
    }}
    </style>
    <div class="letter-container">
        <div class="letter-date">{date_str}</div>
{paragraphs_html_str}
    </div>
    """

