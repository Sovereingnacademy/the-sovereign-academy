import streamlit as st
from google import genai
from google.genai import types
from curriculum import MODULES

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")

taal = st.selectbox("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English", "🇩🇪 Deutsch", "🇫🇷 Français", "🇪🇸 Español"))

TAAL_CONFIG = {
    "🇳🇱 Nederlands": {"code": "Dutch", "bastian": "U & Meneer / Mr", "vale": "U & Mevrouw / Miss", "stop": "ROOD", "sub": "Begeleiding, Discipline, Veiligheid & Bewuste Overgave"},
    "🇬🇧 English": {"code": "English", "bastian": "Sir or Mr", "vale": "Ma'am or Miss", "stop": "RED", "sub": "Guidance, Discipline, Safety & Conscious Submission"},
    "🇩🇪 Deutsch": {"code": "German", "bastian": "Sie & Herr / Mr", "vale": "Sie & Frau / Miss", "stop": "ROT", "sub": "Führung, Disziplin, Sicherheit & Bewusste Hingabe"},
    "🇫🇷 Français": {"code": "French", "bastian": "Vous & Monsieur / Mr", "vale": "Vous & Madame / Miss", "stop": "ROUGE", "sub": "Guidance, Discipline, Sécurité & Soumission Consciente"},
    "🇪🇸 Español": {"code": "Spanish", "bastian": "Usted & Señor / Mr", "vale": "Usted & Señora / Miss", "stop": "ROJO", "sub": "Guía, Disciplina, Seguridad y Sumisión Consciente"}
}
cfg = TAAL_CONFIG[taal]
is_nl = taal == "🇳🇱 Nederlands"

st.title("🏛️ The Sovereign Academy")
st.caption(cfg["sub"])

api_key = st.secrets.get("GEMINI_API_KEY", "")
USER_AVATAR = "👤"

for key, val in [("fase", "Intake"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"), ("module_nr", 1), ("sub_type", "Onbekend")]:
    if key not in st.session_state:
        st.session_state[key] = val
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

is_vale = "Vale" in st.session_state.mentor_naam
titel_txt = cfg["vale"] if is_vale else cfg["bastian"]

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("🏛️")
    st.header("📊 Academy Dossier")
    st.write(f"**Mentor:** {st.session_state.mentor_naam}")
    st.write(f"**Address / Titel:** {titel_txt}")
    st.write(f"**Profile:** {st.session_state.sub_type}")
    st.write(f"**Module:** {st.session_state.module_nr} / 6")
    st.progress(min(st.session_state.module_nr / 6, 1.0))
    st.markdown("---")
    st.info(f"🚨 **Safeword:** **{cfg['stop']}**")

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
    st.subheader("🚪 Fase 1: Welkom & Nulmeting" if is_nl else "🚪 Phase 1: Welcome & Assessment")
    mentor_keuze = st.radio("Kies jouw begeleider:" if is_nl else "Choose your Academy guide:", (
        "Headmaster Bastian",
        "Headmistress Vale"
    ))
    v1 = st.radio("1. Hoe reageer jij op een duidelijke regel?" if is_nl else "1. How do you react to a clear rule from authority?", (
        "Ik voel rust en wil de opdracht goed uitvoeren." if is_nl else "I feel calm and want to follow it precisely.",
        "Ik geef graag tegengas en test de grenzen." if is_nl else "I tend to push back and test boundaries.",
        "Ik wil de controle helemaal loslaten." if is_nl else "I want to surrender control completely."
    ))
    if st.button("Start Module 1 ➡️"):
        st.session_state.mentor_naam = mentor_keuze
        st.session_state.mentor_foto = "vale.jpg" if "Vale" in mentor_keuze else "bastian.jpg"
        st.session_state.sub_type = "Brat" if ("tegengas" in v1 or "push back" in v1) else ("Slave / Slavin" if ("loslaten" in v1 or "completely" in v1) else "Classic Submissive")
        st.session_state.fase = "Les"
        st.rerun()

elif st.session_state.fase == "Les":
    mod = MODULES.get(st.session_state.module_nr)
    if not is_nl and api_key:
        with st.spinner(f"Loading Module {st.session_state.module_nr} in {cfg['code']}..."):
            tekst_vert = vraag_mentor(f"Translate this BDSM Academy module and quiz into natural, authoritative {cfg['code']}. Keep the exact structure:\nTitle: {mod.get('titel')}\nTheory: {mod.get('theorie')}\nQ1: {mod.get('v1')} Options: {mod.get('o1')}\nQ2: {mod.get('v2')} Options: {mod.get('o2')}")
            st.markdown(tekst_vert)
            if st.button("Enter Practice Room ➡️"):
                st.session_state.fase = "Praktijkkamer"
                intro = vraag_mentor(f"You are {st.session_state.mentor_naam}. Write a short 3-sentence welcome in {cfg['code']} to your new student ({st.session_state.sub_type}). Tell them they must address you strictly as '{titel_txt}' and earn the title Master/Mistress after graduation. Ask what brings them here.")
                st.session_state.chat_history.append(("assistant", intro))
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
                    st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} slaat je dossier dicht.* Goed. Spreek mij aan met '{titel_txt}'. De titel Meester of Meesteres verdien je pas na je opleiding. Vertel mij: waar liep je tegenaan en wat zoek je hier?"))
                st.rerun()
            else:
                st.error("❌ Nog niet helemaal juist. Lees de theorie nog eens door.")

elif st.session_state.fase == "Praktijkkamer":
    mentor = st.session_state.mentor_naam
    mentor_img = st.session_state.mentor_foto
    if st.session_state.module_nr < 6:
        if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
            st.session_state.module_nr += 1
            st.session_state.fase = "Les"
            st.rerun()

    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar=(mentor_img if role == "assistant" else USER_AVATAR)):
            st.write(text)
            
    if user_input := st.chat_input(f"... ({titel_txt})"):
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(user_input)
        if any(w in user_input.upper() for w in ("ROOD", "RED", "ROT", "ROUGE", "ROJO")):
            nood = vraag_mentor(f"You are {mentor}. The student just used the safeword. Immediately drop all dominance, be warm, gentle and reassuring in {cfg['code']} in 2 short sentences.")
            st.session_state.chat_history.append(("assistant", nood))
            st.rerun()
        else:
            with st.chat_message("assistant", avatar=mentor_img):
                taal_regels = (
                    f"Respond strictly in natural {cfg['code']}. "
                    f"Enforce strict etiquette: the student MUST address you formally as '{titel_txt}'. "
                    "If they use informal pronouns, your first name, or call you 'Master'/'Mistress'/'Meester'/'Meesteres', correct them calmly and strictly, reminding them those titles must be earned after graduating."
                )
                gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.chat_history)
                antwoord = vraag_mentor(f"You are {mentor} of The Sovereign Academy. Student profile: {st.session_state.sub_type}. {taal_regels}\n\nHistory:\n{gesprek}\n\nResponse:")
                st.write(antwoord)
                st.session_state.chat_history.append(("assistant", antwoord))
