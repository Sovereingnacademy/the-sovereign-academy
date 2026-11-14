import streamlit as st
import google.generativeai as genai

# 1. Pagina-instellingen
st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")
st.title("🏛️ The Sovereign Academy")
st.caption("Onderwijs, Discipline, Veiligheid & Bewuste Overgave")

# 2. Gratis Google Gemini API Koppeling
# Plak je gratis API-sleutel (van ://google.com) in de Secrets van Hugging Face onder 'GEMINI_API_KEY'
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# 3. Initialiseer het geheugen van de app
if "fase" not in st.session_state:
    st.session_state.fase = "Fase 1: Intake"
if "sub_type" not in st.session_state:
    st.session_state.sub_type = "Onbekend"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Zijbalk voor jou als Analist / Beheerder
with st.sidebar:
    st.header("📊 Academy Dossier")
    st.write(f"**Huidige Fase:** {st.session_state.fase}")
    st.write(f"**Toegewezen Profiel:** {st.session_state.sub_type}")
    st.markdown("---")
    st.info("🚨 **Noodrem:** Typ op elk gewenst moment **ROOD** in de chat om een sessie direct te stoppen.")

# ==========================================
# FASE 1: DE INTAKE & TYPE-BEPALING
# ==========================================
if st.session_state.fase == "Fase 1: Intake":
    st.subheader("🚪 Fase 1: Welkom & Nulmeting")
    st.write("""
    *Het zware eikenhouten portaal sluit achter je. Voor je staat een man in een strak gesneden pak. Zijn houding straalt absolute kalmte en natuurlijk gezag uit.*
    
    **Headmaster Bastian spreekt:**  
    *"Welkom bij The Sovereign Academy. Wij breken niemand af; wij bouwen op. Voordat jij onze lessen betreedt, moet ik weten wie ik voor me heb. Vul deze nulmeting in. Wees radicaal eerlijk."*
    """)
    
    v1 = st.radio("1. Hoe reageer jij wanneer iemand met gezag jou een duidelijke regel geeft?", [
        "Ik voel rust en wil de opdracht zo precies mogelijk uitvoeren.",
        "Ik krijg de neiging om tegengas te geven en te testen of die persoon de leiding aankan.",
        "Ik wil de controle volledig uit handen geven en mijzelf helemaal ondergeschikt maken."
    ])
    
    v2 = st.radio("2. Wat zoek jij het meeste in een D/s-dynamiek?", [
        "Duidelijke kaders, veiligheid, bescherming en een mentor die mij helpt groeien.",
        "Spanning, psychologisch spel en iemand die onverstoorbaar blijft als ik uitdaag.",
        "Totale overgave, diepe discipline en vaste protocollen in het dagelijks leven."
    ])
    
    if st.button("Voltooi Intake & Open Dossier"):
        if "tegengas" in v1 or "uitdaag" in v2:
            st.session_state.sub_type = "Brat"
        elif "volledig uit handen" in v1 or "Totale overgave" in v2:
            st.session_state.sub_type = "Slavin"
        else:
            st.session_state.sub_type = "Klassieke Submissive"
            
        st.session_state.fase = "Module 1: Theorie & Toets"
        st.rerun()

# ==========================================
# FASE 2: MODULE 1 (THEORIE & VERPLICHTE TOETS)
# ==========================================
elif st.session_state.fase == "Module 1: Theorie & Toets":
    st.subheader("📚 Module 1: Veiligheid, Het Fundament & Rechten")
    st.success(f"Dossier aangemaakt. Jij bent geclassificeerd als: **{st.session_state.sub_type}**.")
    
    with st.expander("📖 Lees hier de verplichte theorie (Klik om te openen)", expanded=True):
        st.markdown("""
        *   **RACK & Kracht:** Binnen The Sovereign Academy werken we volgens *Risk-Aware Consensual Kink*. Onderwerping is geen zwakte, maar een bewuste keuze van een krachtige geest. Zonder submissive is geen Dominant mogelijk.
        *   **Het Verkeerslichtsysteem:** **ROOD** = Onmiddellijke noodstop zonder discussie. **GEEL** = Grens nadert, doe rustiger aan. **GROEN** = Alles is veilig.
        *   **Plichten:** De Dom(me) beschermt, cultiveert en geeft altijd *aftercare*. Negeren als straf is foute boel. De submissive heeft één harde plicht: 100% radicale eerlijkheid.
        """)
        
    st.markdown("---")
    st.write("📝 **Verplichte Kennistest** (Beantwoord alle vragen goed om de praktijkkamer te openen)")
    
    t1 = st.radio("Vraag 1: Wat betekent het safe word 'GEEL'?", [
        "Onmiddellijk stoppen met de sessie.",
        "Ik nader een grens; verlaag de intensiteit of verander de handeling, maar we gaan door.",
        "Ik wil mijn mentor bewust uitdagen."
    ])
    t2 = st.radio("Vraag 2: Wie bepaalt op de achtergrond altijd de harde grenzen?", [
        "De Dominant, want die heeft de leiding.",
        "De submissive, via haar consent, eerlijkheid en safe words."
    ])
    
    if st.button("Verzend Toets"):
        if "verlaag de intensiteit" in t1 and "De submissive" in t2:
            st.session_state.fase = "Praktijkkamer: Vrije Chat"
            st.session_state.chat_history.append(("assistant", f"*Headmaster Bastian sluit je dossier en kijkt je rustig aan.* Je hebt de basis veiliggesteld, {st.session_state.sub_type}. Welkom in mijn praktijkkamer. Vertel me: wat hoop jij hier als eerste te overwinnen of te leren?"))
            st.rerun()
        else:
            st.error("❌ **Headmaster Bastian schudt zijn hoofd:** *\"Niet correct. Ik laat je niet toe tot de praktijk zonder dat je de basisveiligheid beheerst. Lees de theorie opnieuw.\"*")

# ==========================================
# FASE 3: DE VRIJE CHAT MET HEADMASTER BASTIAN
# ==========================================
elif st.session_state.fase == "Praktijkkamer: Vrije Chat":
    st.subheader("💬 Praktijkkamer: Headmaster Bastian")
    
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)
            
    if user_input := st.chat_input("Typ je reactie naar Headmaster Bastian..."):
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)
            
        # Harde noodstop-code
        if "ROOD" in user_input.upper():
            nood_tekst = "*Headmaster Bastian stopt direct met alles, laat elke vorm van controle los en pakt een warme deken.* Rustig maar. De sessie is direct beëindigd. Haal adem, je bent helemaal veilig. Neem alle tijd die je nodig hebt."
            st.session_state.chat_history.append(("assistant", nood_tekst))
            with st.chat_message("assistant"):
                st.write(nood_tekst)
        else:
            # Koppel met de gratis Google Gemini AI
            with st.chat_message("assistant"):
                if not api_key:
                    st.warning("⚠️ Voeg eerst je gratis Google Gemini API-sleutel toe in de Hugging Face Secrets om Bastian live te laten antwoorden!")
                else:
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        systeem_instructie = f"""
                        Je bent Headmaster Bastian, het hoofd van The Sovereign Academy. 
                        De gebruiker is geclassificeerd als: {st.session_state.sub_type}.
                        Je bent streng, kalm, respectvol en trauma-informed. Je breekt nooit af, maar bouwt op en leert de sub dat overgave kracht is.
                        Schrijf fysieke handelingen en houdingen altijd tussen asterisken (bijv. *leunt rustig achterover*).
                        Reageer direct en inhoudelijk op wat de gebruiker typt: {user_input}
                        """
                        response = model.generate_content(systeem_instructie)
                        st.write(response.text)
                        st.session_state.chat_history.append(("assistant", response.text))
                    except Exception as e:
                        st.error(f"Er ging iets mis met de AI-verbinding: {e}")
