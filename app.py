import streamlit as st
from google import genai
from google.genai import types
from curriculum import MODULES

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")

taal = st.radio("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English"), horizontal=True)
is_en = "English" in taal

st.title("🏛️ The Sovereign Academy")
st.caption("Guidance, Discipline, Safety & Conscious Submission" if is_en else "Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
USER_AVATAR = "👤"

for key, val in [
    ("fase", "Intake"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"),
    ("module_nr", 1), ("sub_type", "Onbekend"), ("notitieboek_actief", False), ("grenzenlijst_actief", False)
]:
    if key not in st.session_state:
        st.session_state[key] = val
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "notities" not in st.session_state:
    st.session_state.notities = []
if "grenzen" not in st.session_state:
    st.session_state.grenzen = {}

is_vale = "Vale" in st.session_state.mentor_naam
titel_txt = ("Ma'am or Miss" if is_en else "Mevrouw of Miss") if is_vale else ("Sir or Mr" if is_en else "Meneer of Mr")

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("🏛️")
    st.header("📊 Academy Dossier")
    st.write(f"**Mentor:** {st.session_state.mentor_naam}")
    st.write(f"**Address / Titel:** {'Formal & ' + titel_txt if is_en else 'U & ' + titel_txt}")
    st.write(f"**Profile:** {st.session_state.sub_type}")
    st.write(f"**Module:** {st.session_state.module_nr} / 6")
    st.progress(min(st.session_state.module_nr / 6, 1.0))
    st.markdown("---")
    st.info("🚨 **Safeword:** **RED**" if is_en else "🚨 **Noodrem:** **ROOD**")
    if st.button("🔄 Reset / Opnieuw beginnen"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

def vraag_mentor(prompt_tekst):
    client = genai.Client(api_key=api_key)
    modellen = (m.name for m in client.models.list() if "flash" in m.name.lower() and not any(x in m.name for x in ("1.5", "2.0", "2.5")))
    response = client.models.generate_content(
        model=next(modellen, "gemini-3.8-flash"),
        contents=prompt_tekst,
        config=types.GenerateContentConfig(max_output_tokens=2000)
    )
    return response.text

if st.session_state.fase == "Intake":
    if is_en:
        st.subheader("🏛️ Welcome to The Sovereign Academy")
        with st.container(border=True):
            st.markdown(
                "**What is The Sovereign Academy?**\n"
                "The Sovereign Academy is a safe, judgment-free learning environment dedicated to conscious submission, personal growth, and healthy D/s dynamics. Here, we do not break you down; we build you up. Surrendering control is not a sign of weakness, but an act of deep trust and inner strength.\n\n"
                "**How does it work?**\n"
                "1. **Assessment & Guidance:** Choose your Academy guide (*Headmaster Bastian* or *Headmistress Vale*) and complete a brief intake to determine your dynamic.\n"
                "2. **The 6 Modules:** Learn the essential foundations of safety, consent, subspace, poses, and etiquette, each concluded with a short knowledge check.\n"
                "3. **The Practice Room:** Engage in personal mentoring, unlock tools like your daily check-in journal or limits checklist when needed, and grow at your own pace.\n\n"
                "*Your boundaries are sacred. Use the safeword **RED** at any moment to immediately pause everything.*"
            )
        st.subheader("🚪 Phase 1: Your Assessment")
    else:
        st.subheader("🏛️ Welkom bij The Sovereign Academy")
        with st.container(border=True):
            st.markdown(
                "**Wat is The Sovereign Academy?**\n"
                "The Sovereign Academy is een veilige, oordeelvrije leeromgeving voor wie zich wil verdiepen in bewuste overgave, persoonlijke groei en gezonde D/s-dynamieken. Hier breken we niemand af; we bouwen op. De controle uit handen geven is geen zwakte, maar een bewuste keuze die vraagt om vertrouwen en innerlijke kracht.\n\n"
                "**Hoe werkt het?**\n"
                "1. **Nulmeting & Begeleider:** Kies jouw begeleider (*Headmaster Bastian* of *Headmistress Vale*) en beantwoord een paar korte vragen over wie jij bent.\n"
                "2. **De 6 Modules:** Je doorloopt zes overzichtelijke lessen over veiligheid, mentale processen, houdingen, etiquette en zelfbescherming, telkens afgesloten met een korte kennistest.\n"
                "3. **De Praktijkkamer:** Je gaat in gesprek met jouw begeleider, krijgt persoonlijke reflectie-opdrachten en groeit stap voor stap in jouw eigen tempo.\n\n"
                "*Jouw grenzen zijn altijd leidend. Met het noodwoord **ROOD** kun je op elk gewenst moment direct alles stopzetten.*"
            )
        st.subheader("🚪 Fase 1: Jouw Nulmeting")

    mentor_keuze = st.radio("Choose your Academy guide:" if is_en else "Kies jouw begeleider:", ("Headmaster Bastian", "Headmistress Vale"))
    v1 = st.radio("1. How do you react to a clear rule from authority?" if is_en else "1. Hoe reageer jij op een duidelijke regel?", (
        "I feel calm and want to follow it precisely." if is_en else "Ik voel rust en wil de opdracht goed uitvoeren.",
        "I tend to push back and test boundaries." if is_en else "Ik geef graag tegengas en test de grenzen.",
        "I want to surrender control completely." if is_en else "Ik wil de controle helemaal loslaten."
    ))
    if st.button("Start Module 1 ➡️"):
        st.session_state.mentor_naam = mentor_keuze
        st.session_state.mentor_foto = "vale.jpg" if "Vale" in mentor_keuze else "bastian.jpg"
        st.session_state.sub_type = "Brat" if ("tegengas" in v1 or "push back" in v1) else ("Slave / Slavin" if ("loslaten" in v1 or "completely" in v1) else "Classic Submissive")
        st.session_state.fase = "Les"
        st.rerun()

elif st.session_state.fase == "Les":
    mod = MODULES.get(st.session_state.module_nr)
    if is_en and api_key:
        with st.spinner(f"Loading Module {st.session_state.module_nr}..."):
            tekst_vert = vraag_mentor(f"Translate this BDSM Academy module and quiz into natural, authoritative English:\nTitle: {mod.get('titel')}\nTheory: {mod.get('theorie')}\nQ1: {mod.get('v1')} Options: {mod.get('o1')}\nQ2: {mod.get('v2')} Options: {mod.get('o2')}")
            st.markdown(tekst_vert)
            if st.button("Enter Practice Room ➡️"):
                st.session_state.fase = "Praktijkkamer"
                st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} closes your dossier.* Good. Address me strictly as '{titel_txt}'. Titles like Master or Mistress must be earned after graduation. Tell me: what brings you here?"))
                st.rerun()
    else:
        st.subheader(f"📚 {mod.get('titel')}")
        with st.expander("📖 Verplichte Theorie", expanded=True):
            st.markdown(mod.get("theorie"))
        t1 = st.radio(f"Vraag 1: {mod.get('v1')}", mod.get("o1"))
        t2 = st.radio(f"Vraag 2: {mod.get('v2')}", mod.get("o2"))
        if st.button("Lever toets in"):
            if t1 == mod.get("a1") and t2 == mod.get("a2"):
                st.session_state.fase = "Praktijkkamer"
                if not st.session_state.chat_history:
                    st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} slaat je dossier dicht.* Goed. Spreek mij aan met 'u' en '{titel_txt}'. De titel Meester of Meesteres verdien je pas na je opleiding. Vertel mij: waar liep je tegenaan en wat zoek je hier?"))
                st.rerun()
            else:
                st.error("❌ Nog niet helemaal juist. Lees de theorie nog eens door.")
