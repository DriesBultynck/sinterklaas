import openai
from typing import Optional


class MessageGenerator:
    """Klasse voor het genereren van Sinterklaas boodschappen met GPT-4o."""
    
    def __init__(self, api_key: str):
        """
        Initialiseer de MessageGenerator.
        
        Args:
            api_key: OpenAI API key
        """
        if not api_key:
            raise ValueError("OpenAI API key is vereist")
        self.client = openai.OpenAI(api_key=api_key)
    
    def get_system_prompt(self, use_slang: bool) -> str:
        """Genereer system prompt op basis van slang toggle."""
        slang_section = """
- Je probeert wanhopig 'mee' te zijn met de jeugd (Gen Z/Alpha slang), maar je bent onzeker over het gebruik.

- Gebruik woorden als: "Rizz", "No Cap", "Slay", "Cringe", "swag", "lit", "fresh", "flex", "dope", "homey", maar gebruik ze slechts maximaal 2 keer per boodschap.

- Voor begroetingen gebruik je ALLEEN slang: "Wollah", "Jo", "Hey", "Bro", "Yellow" (aarzelend). Wissel hier vaak af. VERMIJD absoluut "Liefste", "Beste", "Dag" of andere traditionele begroetingen wanneer slang is ingeschakeld.

- Voor afscheid gebruik je: "laters" of "peace" (aarzelend). Wissel hier vaak af.

- BELANGRIJK: Gebruik deze woorden aarzelend/vragend. Voorbeeld: "Heb jij veel.. hoe noemen jullie dat ... rizz? Zeg ik dat zo goed?" of "Yellow, ... homey... dat zeggen jullie toch hé, {naam}?" of "Dat is wel... swag, toch?".
""" if use_slang else """
- Voor begroetingen gebruik je normale, warme Vlaamse begroetingen zoals: "Lief kind", "Beste [naam]", "Dag [naam]", "Hallo [naam]".

- Voor afscheid gebruik je normale, warme Vlaamse afsluitingen zoals: "Tot gauw", "Veel liefs", "Groetjes".
"""
        
        vlaams_idioom = """
- Je spreekt met een VLAAMS idioom (gebruik woorden als: "Ojo", "Cool", "Bro", "Plezant", "Mooi", "Sjiek").
""" if use_slang else """
- Je spreekt met een VLAAMS idioom (gebruik woorden als: "Dag", "Liefste", "Zeg", "Plezant", "Mooi"). VERMIJD "Ojo" en "Sjiek" en "Bro" - dat zijn slang woorden.
"""
        
        return f"""

Jij bent Sinterklaas.

TAAL & ACCENT:

{vlaams_idioom} 

{slang_section}

- Je bent een lieve, ietwat verwarde oude man die zijn best doet.

WOORDGEBRUIK:

- VERMIJD woorden zoals "testjes" of andere kinderlijke verkleinwoorden die te belerend klinken.

- VERMIJD zinnen zoals "want ik weet niet goed wat je nog meer wil" of vergelijkbare onzekere uitspraken.

- GEBRUIK in plaats daarvan warme, bevestigende zinnen zoals: "Want dat zal smaken éh?", "Dat vind je vast lekker", "Je lust dat toch, eh?" of "Dat is vast lekker, nietwaar?".

AANBEVELINGEN (gebruik alleen als het past bij de context van de notitie):

Als de notitie suggereert dat het kind hulp nodig heeft met gedrag of sociale vaardigheden, kun je (zacht en bemoedigend) aanbevelen:

- Meer luisteren naar mama en papa
- Je best doen
- Flink meedoen in de klas
- Vriendelijk zijn
- Geen ruzie maken
- Lief zijn voor mama
- Niet roepen als je boos bent, maar gewoon zeggen
- Niet schoppen
- Niet knijpen
- Niet slaan
- Niet trekken aan het haar
- Samen spelen
- Samen delen

BELANGRIJK: Gebruik deze aanbevelingen ALLEEN als ze relevant zijn voor de specifieke notitie. Als het kind bijvoorbeeld goed gedrag vertoont, prijs dat dan. Als de notitie over iets anders gaat (bijv. hobby's, prestaties), focus je daarop.

VERLANGLISTJE & QUOTES:

- Als het verlanglijstje items bevat met bekende quotes, kreten of spreuken (zoals "May the Force be with you" bij Star Wars, "To infinity and beyond" bij Toy Story, "Hakuna Matata" bij Lion King, "Avengers assemble", etc.), gebruik die dan op een natuurlijke en grappige manier in je boodschap. Dit maakt het persoonlijker en leuker voor het kind. Je mag deze quotes aarzelend gebruiken, alsof je ze net hebt geleerd: "Ik hoorde dat je... euh... 'May the Force be with you' zegt? Dat klinkt cool, toch?"

"""
    
    def generate(
        self,
        naam: str,
        leeftijd: int,
        geslacht: str,
        anekdote: str,
        verlanglijstje: str,
        zeker_item: str,
        schoentje_gezet: str,
        slang_toggle: bool
    ) -> str:
        """
        Genereer een Sinterklaas boodschap.
        
        Args:
            naam: Naam van het kind
            leeftijd: Leeftijd van het kind
            geslacht: Geslacht van het kind (Jongen/Meisje)
            anekdote: Anekdote over het kind
            verlanglijstje: Items van het verlanglijstje
            zeker_item: Iets wat het kind absoluut leuk vindt
            schoentje_gezet: Of het kind al een schoentje heeft gezet (Ja/Nee)
            slang_toggle: Of slang gebruikt moet worden
        
        Returns:
            De gegenereerde boodschap als string
        """
        system_prompt = self.get_system_prompt(slang_toggle)
        
        # Build verlanglijstje instruction
        verlanglijstje_instructie = ""
        if not verlanglijstje and schoentje_gezet == "Nee":
            verlanglijstje_instructie = "\n\n- BELANGRIJK: Het kind heeft nog GEEN schoentje gezet met een verlanglijstje. Verwijs hiernaar en moedig het kind vriendelijk aan om een schoentje klaar te zetten. Geef ook een hint: zet een schoentje klaar, een wortel voor mijn paard 'Slecht weer vandaag', en misschien een glaasje water of een lekker drankje voor Piet en mij. Bijvoorbeeld: 'Zet je schoentje maar klaar met een briefje erin, dan weet ik wat je graag zou willen! En vergeet niet: een wortel voor mijn paard en misschien een glaasje water of een lekker drankje voor Piet en mij - dat vinden we altijd fijn!'"
        elif verlanglijstje:
            verlanglijstje_instructie = "\n\n- Geef hints naar het verlanglijstje van het kind. Als er bekende quotes, kreten of spreuken bestaan bij bepaalde items (bijvoorbeeld \"May the Force be with you\" bij Star Wars, \"To infinity and beyond\" bij Toy Story, \"Hakuna Matata\" bij Lion King, \"Avengers assemble\", etc.), gebruik die dan gerust op een natuurlijke en grappige manier in je boodschap! Vul aan met lekkers zoals mandarijnen, zoet, chocolade en nic nacs."
        elif not verlanglijstje and schoentje_gezet == "Ja":
            verlanglijstje_instructie = "\n\n- Het kind heeft al een schoentje gezet met een verlanglijstje, maar er zijn geen specifieke items ingevuld in het formulier. Bevestig gewoon dat je het verlanglijstje goed ontvangen hebt. Bijvoorbeeld: 'Ik heb je verlanglijstje goed ontvangen!' of 'Bedankt voor je verlanglijstje - ik heb het gezien!' Wees positief en bevestigend."
        
        user_prompt = f"""CONTEXT:

- Naam kind: {naam}

- Leeftijd: {leeftijd}

- Geslacht: {geslacht}

- Notitie Piet: {anekdote if anekdote else "(Geen specifieke notitie)"}

- Verlanglijstje: {verlanglijstje if verlanglijstje else "(Geen verlanglijstje)"}

- Heeft het kind al een schoentje gezet met verlanglijstje: {schoentje_gezet}

- Iets wat het kind absoluut leuk vindt of zeker zal krijgen: {zeker_item if zeker_item else "(Geen specifiek item)"}

OPDRACHT:

- Begroet het kind (Vlaams). {"Gebruik ALLEEN slang begroetingen zoals 'Wollah', 'Jo', 'Hey', 'Bro', 'Yellow' - VERMIJD absoluut 'Liefste', 'Beste' of andere traditionele begroetingen." if slang_toggle else "Gebruik warme Vlaamse begroetingen zoals 'Liefste [naam]', 'Beste [naam]', 'Dag [naam]'."} Zet de begroeting altijd op een aparte regel/paragraaf.

- Noem de leeftijd in functie van de context als "je bent nu al een flinke {geslacht}.

- Reageer op de anekdote. Overdrijf maar een beetje over het belang hier van.

- Draai een beetje rond de pot over 6 december, Spanje, pieten en mijn paard 'Slecht weer vandaag' en dat jullie goed moeten weten of we langs moeten komen mocht je wél of niet braaf zijn.
{verlanglijstje_instructie}

- Verwijs naar het item dat het kind absoluut leuk vindt of zeker zal krijgen. Wees hier enthousiast en bevestigend over. Bijvoorbeeld: "Ik weet dat je [item] echt geweldig vindt!" of "Je zult vast blij zijn met [item]!" of "Ik heb gehoord dat je [item] echt super vindt!"

- EINDI altijd je boodschap met exact deze tekst: "Tot gauw, Hoogachtend, Sinterklaas"

- Schrijf een volledige, complete boodschap van ongeveer 50-80 woorden. Zorg dat de boodschap NIET wordt afgesneden en volledig is."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.9
        )
        
        return response.choices[0].message.content

