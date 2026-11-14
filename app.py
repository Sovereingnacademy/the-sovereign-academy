import streamlit as st
from google import genai

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")
st.title("🏛️ The Sovereign Academy")
st.caption("Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")

if "fase" not in st.session_state:
    st.session_state.fase = "Fase 1: Intake"
if "sub_type" not in st.session_state:
    st.session_state.sub_type = "Onbekend"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("📊 Academy Dossier")
    st.write(f"**Huidige Fase:** {st.session_state.fase}")
    st.write(f"**Jouw Profiel:** {st.session_state.sub_type}")
    st.markdown("---")
    st.info("🚨 **Noodrem:** Typ op elk gewenst moment **ROOD** in de chat om een sessie direct te stoppen.")

if st.session_state.fase == "Fase 1: Intake":
    st.subheader("🚪 Fase 1: Welkom & Nulmeting")
    st.write("""
    *De zware houten deur valt achter je in het slot. In de ontvangsthal hangt een serene rust. Voor je staat een man in een donker, strak gesneden pak. Hij kijkt je kalm aan, zonder enig oordeel in zijn blik.*
    
    **Headmaster Bastian:**  
    *"Welkom bij The Sovereign Academy. Veel mensen stappen hier binnen met verkeerde verwachtingen, gevormd door verhalen van buitenaf of slechte ervaringen. Hier werken we anders. We breken niemand af; we bouwen op. Voordat we beginnen, wil ik weten wie ik voor me heb. Vul deze vragenlijst in. Wees gewoon eerlijk."*
    """)
    
    v1 = st.radio("1. Hoe reageer jij van nature als iemand met gezag jou een duidelijke regel geeft?", [
        "Ik voel rust en wil de opdracht zo goed mogelijk uitvoeren.",
        "Ik krijg meteen de neiging om tegengas te geven en te kijken hoever ik kan gaan.",
        "Ik wil de controle het liefst helemaal loslaten en mij volledig voegen naar de ander."
    ])
    
    v2 = st.radio("2. Wat zoek jij op dit moment het meeste?", [
        "Duidelijke kaders, veiligheid en een mentor die mij helpt groeien.",
        "Spanning, uitdaging en iemand die onverstoorbaar blijft als ik de grenzen opzoek.",
        "Totale overgave, diepe discipline en vaste regels in het dagelijks leven."
    ])
    
    if st.button("Sla gegevens op & Ga verder"):
        if "tegengas" in v1 or "grenzen opzoek" in v2:
            st.session_state.sub_type = "Brat"
        elif "helemaal loslaten" in v1 or "Totale overgave" in v2:
            st.session_state.sub_type = "Slavin"
        else:
            st.session_state.sub_type = "Klassieke Submissive"
            
        st.session_state.fase = "Module 1: Theorie & Toets"
        st.rerun()

elif st.session_state.fase == "Module 1: Theorie & Toets":
    st.subheader("📚 Module 1: Veiligheid & Het Fundament")
    st.success(f"Jouw dossier is bijgewerkt. Profiel: **{st.session_state.sub_type}**.")
    
    with st.expander("📖 Lees eerst de basisregels door", expanded=True):
        st.markdown("""
        *   **Kracht & Keuze:** Onderwerping heeft niets met zwakte te maken. De controle bewust uit handen geven vraagt juist om enorme kracht en vertrouwen. Zonder jou is er geen dynamiek mogelijk; jij bepaalt op de achtergrond altijd de kaders.
        *   **Het Verkeerslicht:** **ROOD** = Direct stoppen, zonder discussie. **GEEL** = Ik nader een grens, doe rustiger aan. **GROEN** = Alles voelt goed en veilig.
        *   **Wederzijdse Plichten:** Een goede Dom(me) beschermt je en zorgt altijd voor nazorg (*aftercare*). Negeren als straf is uit den boze. Jouw enige harde plicht is volledige eerlijkheid over wat je voelt.
        """)
        
    st.markdown("---")
    st.write("📝 **Korte Kennistest** (Beantwoord de vragen goed om naar de praktijkkamer te gaan)")
    
    t1 = st.radio("Vraag 1: Wat betekent het safe word 'GEEL'?", [
        "We moeten onmiddellijk stoppen.",
        "Ik nader een grens; we doen het rustiger aan, maar de sessie loopt door.",
        "Ik wil mijn mentor bewust uitdagen."
    ])
    t2 = st.radio("Vraag 2: Wie bewaakt op de achtergrond altijd de harde grenzen?", [
        "De Dominant, want die bepaalt de regels.",
        "De submissive, door eerlijk te zijn en haar grenzen aan te geven."
    ])
    
    if st.button("Lever antwoorden in"):
        if "rustiger aan" in t1 and "De submissive" in t2:
            st.session_state.fase = "Praktijkkamer: Vrije Chat"
            st.session_state.chat_history.append(("assistant", f"*Headmaster Bastian slaat je dossier dicht en kijkt je rustig aan.* Goed. De basis staat, {st.session_state.sub_type}. Neem plaats. Vertel me eens in je eigen woorden: waar liep je tot nu toe tegenaan, en wat hoop je hier te vinden?"))
            st.rerun()
        else:
            st.error("❌ **Headmaster Bastian schudt zijn hoofd:** *\"Nog niet helemaal. Ik laat je pas toe in de praktijkkamer als ik zeker weet dat je de veiligheidsregels snapt. Lees de tekst nog eens rustig door.\"*")

elif st.session_state.fase == "Praktijkkamer: Vrije Chat":
    st.subheader("💬 Praktijkkamer: Headmaster Bastian")
    
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    if user_input := st.chat_input("Typ je reactie naar Headmaster Bastian..."):
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)
            
        if "ROOD" in user_input.upper():
            nood_tekst = "*Bastian stopt direct, laat elke vorm van controle los en pakt een zachte deken.* Rustig maar. Het is klaar. Haal even diep adem, je bent helemaal veilig. Neem je tijd."
            st.session_state.chat_history.append(("assistant", nood_tekst))
            with st.chat_message("assistant"):
                st.write(nood_tekst)
        else:
            with st.chat_message("assistant"):
                if not api_key:
                    st.warning("⚠️ Voeg eerst je gratis Google API-sleutel toe in de Secrets.")
                else:
                    try:
                        client = genai.Client(api_key=api_key)
                        systeem_instructie = f"""
                        Je bent Headmaster Bastian, het hoofd van The Sovereign Academy. 
                        De gebruiker is geclassificeerd als: {st.session_state.sub_type}.
                        
                        BELANGRIJKE SCHRIJFSTIJL:
                        - Schrijf natuurlijk, vloeiend en menselijk Nederlands. Vermijd stijve AI-zinnen.
                        - Je bent kalm, ervaren, observant en hebt natuurlijk gezag. Je bent beschermend en respectvol, nooit sadistisch of vernederend.
                        - Je leert de sub dat bewuste overgave juist een teken van kracht is.
                        - Omschrijf kleine, realistische handelingen tussen asterisken (bijv. *knikt langzaam*).
                        - Reageer direct en invoelend op het bericht van de gebruiker: "{user_input}"
                        """
                        # Filtert alle oude 1.5, 2.0 en 2.5 modellen eruit en pakt alleen 3.x
                        alle_modellen = [
                            m.name for m in client.models.list() 
                            if "flash" in m.name.lower() 
                            and "1.5" not in m.name 
                            and "2.0" not in m.name 
                            and "2.5" not in m.name
                        ]
                        gekozen_model = alle_modellen if alle_modellen else "gemini-3.8-flash"
                        
                        response = client.models.generate_content(
                            model=gekozen_model,
                            contents=systeem_instructie
                        )
                        st.write(response.text)
                        st.session_state.chat_history.append(("assistant", response.text))
                    except Exception as e:
                        st.error(f"Technische reden: {e}")
