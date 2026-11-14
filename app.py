import streamlit as st
from google import genai
from google.genai import types
from curriculum import MODULES
from checklist import CHECKLIST_CATEGORIEEN
from meesters import MEESTERS

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")

taal = st.radio("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English"), horizontal=True)
is_en = "English" in taal

st.title("🏛️ The Sovereign Academy")
st.caption("Guidance, Discipline, Safety & Conscious Submission" if is_en else "Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
USER_AVATAR = "👤"

for key, val in [
    ("fase", "Intake"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"),
    ("module_nr", 0), ("sub_type", "Classic Submissive"), ("notitieboek_actief", False),
    ("grenzenlijst_actief", False), ("verbond_actief", False), ("meester_stijl", "")
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
if st.session_state.verbond_actief:
    titel_txt = "Master / Mistress" if is_en else "Meester / Meesteres"
else:
    titel_txt = ("Ma'am or Miss" if is_en else "Mevrouw of Miss") if is_vale else ("Sir or Mr" if is_en else "Meneer of Mr")

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("👑" if st.session_state.verbond_actief else "🏛️")
    st.header("📊 Academy Dossier")
    st.write(f"**{'Dominant' if st.session_state.verbond_actief else 'Mentor'}:** {st.session_state.mentor_naam}")
    st.write(f"**Address / Titel:** {titel_txt}")
    st.write(f"**Profile:** {st.session_state.sub_type}")
    if st.session_state.verbond_actief:
        st.success("👑 **Fase 3: Het Verbond Actief**")
    else:
        st.write(f"**Module:** {st.session_state.module_nr} / 6")
        st.progress(min(st.session_state.module_nr / 6, 1.0))
    st.markdown("---")
    st.info("🚨 **Safeword:** **RED**" if is_en else "🚨 **Safewoord:** **ROOD**")
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
                "1. **Assessment & Guidance:** Choose your Academy guide (*Headmaster Bastian* or *Headmistress Vale*) and complete a brief intake.\n"
                "2. **The 6 Modules:** Learn safety, consent, subspace, poses, and etiquette.\n"
                "3. **Phase 3 (The Bond):** Graduate and choose between two matched Masters or Mistresses for daily structure.\n\n"
                "*Use the safeword **RED** at any moment to immediately pause everything.*"
            )
        st.subheader("🚪 Phase 1: Your Assessment")
    else:
        st.subheader("🏛️ Welkom bij The Sovereign Academy")
        with st.container(border=True):
            st.markdown(
                "**Wat is The Sovereign Academy?**\n"
                "The Sovereign Academy is een veilige, oordeelvrije leeromgeving voor wie zich wil verdiepen in bewuste overgave, persoonlijke groei en gezonde D/s-dynamieken. Hier breken we niemand af; we bouwen op. De controle uit handen geven is geen zwakte, maar een bewuste keuze die vraagt om vertrouwen en innerlijke kracht.\n\n"
                "**Hoe werkt het?**\n"
                "1. **Nulmeting & Begeleider:** Kies jouw begeleider (*Headmaster Bastian* of *Headmistress Vale*) en beantwoord de nulmeting.\n"
                "2. **De 6 Modules:** Doorloop de lessen over veiligheid, mentale processen, houdingen, etiquette en zelfbescherming.\n"
                "3. **Fase 3 (Het Verbond):** Studeer af en kies uit twee geselecteerde Meesters of Meesteressen voor dagelijkse structuur.\n\n"
                "*Met het safewoord **ROOD** kun je op elk gewenst moment direct alles stopzetten.*"
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
        st.session_state.module_nr = 1
        st.session_state.fase = "Les"
        st.rerun()

elif st.session_state.fase == "Les":
    mod = MODULES.get(max(1, st.session_state.module_nr))
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

elif st.session_state.fase == "Afstuderen":
    st.subheader("🎓 Fase 3: Diploma-uitreiking & Het Verbond" if not is_en else "🎓 Phase 3: Graduation & The Bond")
    st.success(f"Gefeliciteerd! Je hebt alle 6 modules succesvol afgerond. Jouw profiel: **{st.session_state.sub_type}**." if not is_en else f"Congratulations! You completed all 6 modules. Your profile: **{st.session_state.sub_type}**.")
    st.write("Op basis van jouw traject heeft de Academie **twee geschikte kandidaten** geselecteerd. Lees hun kennismaking en maak jouw definitieve keuze:" if not is_en else "Based on your journey, the Academy has selected **two suitable candidates**. Read their introductions and make your final choice:")
    
    voorkeur = st.radio("Ik wens begeleid te worden door een:" if not is_en else "I wish to be guided by a:", ("Mannelijk (Meester)", "Vrouwelijk (Meesteres)"), horizontal=True)
    geslacht = "Mannelijk" if "Mannelijk" in voorkeur else "Vrouwelijk"
    
    if geslacht == "Mannelijk":
        kandidaten = ("Meester Julian", "Meester Marcus") if st.session_state.sub_type == "Brat" else (("Meester Marcus", "Meester Viktor") if "Slav" in st.session_state.sub_type else ("Meester Viktor", "Meester Julian"))
    else:
        kandidaten = ("Meesteres Elena", "Meesteres Sophia") if st.session_state.sub_type == "Brat" else (("Meesteres Sophia", "Meesteres Clara") if "Slav" in st.session_state.sub_type else ("Meesteres Clara", "Meesteres Elena"))
        
    for naam in kandidaten:
        info = MEESTERS.get(naam)
        with st.container(border=True):
            c1, c2 = st.columns((1, 3))
            with c1:
                try:
                    st.image(info.get("foto"), width=120)
                except Exception:
                    st.write("👑")
            with c2:
                st.markdown(f"### {naam} — *{info.get('specialisatie')}*")
                st.write(info.get("bio_en" if is_en else "bio_nl"))
                if st.button(f"👑 Sluit Verbond met {naam}", key=f"btn_{naam}"):
                    st.session_state.mentor_naam = naam
                    st.session_state.meester_stijl = info.get("stijl")
                    st.session_state.mentor_foto = info.get("foto")
                    st.session_state.verbond_actief = True
                    st.session_state.notitieboek_actief = True
                    st.session_state.grenzenlijst_actief = True
                    st.session_state.chat_history = [("assistant", info.get("intro_en" if is_en else "intro_nl"))]
                    st.session_state.fase = "Praktijkkamer"
                    st.rerun()

elif st.session_state.fase == "Praktijkkamer":
    mentor = st.session_state.mentor_naam
    mentor_img = st.session_state.mentor_foto
    
    if not st.session_state.verbond_actief:
        if st.session_state.module_nr < 6:
            if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
                st.session_state.module_nr += 1
                st.session_state.fase = "Les"
                st.rerun()
        else:
            if st.button("🎓 Studeer af & Ga naar Fase 3 (Het Verbond) 👑"):
                st.session_state.fase = "Afstuderen"
                st.rerun()

    tab_namen = ["💬 Practice Room" if is_en else "💬 Praktijkkamer"]
    if st.session_state.notitieboek_actief:
        tab_namen.append("📓 Journal" if is_en else "📓 Notitieboekje")
    if st.session_state.grenzenlijst_actief:
        tab_namen.append("🔒 Limits" if is_en else "🔒 Grenzenlijst")

    if len(tab_namen) > 1:
        tabs = st.tabs(tab_namen)
        tab_chat = next(iter(tabs))
    else:
        tab_chat = st.container()

    with tab_chat:
        for role, text in st.session_state.chat_history:
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else USER_AVATAR)):
                st.write(text)
                
        if user_input := st.chat_input(f"... ({titel_txt})"):
            st.session_state.chat_history.append(("user", user_input))
            with st.chat_message("user", avatar=USER_AVATAR):
                st.write(user_input)
            if "ROOD" in user_input.upper() or "RED" in user_input.upper():
                nood = f"*{mentor} stops immediately.* Breathe. You are completely safe." if is_en else f"*{mentor} stopt direct.* Rustig maar, haal adem. Je bent helemaal veilig."
                st.session_state.chat_history.append(("assistant", nood))
                st.rerun()
            else:
                with st.chat_message("assistant", avatar=mentor_img):
                    taal_txt = "English" if is_en else "Dutch"
                    grenzen_txt = str(st.session_state.grenzen) if st.session_state.grenzen else "None yet"
                    if st.session_state.verbond_actief:
                        etiquette_regel = (
                            f"You are {mentor}, the student's dedicated Dominant in Phase 3 (The Bond). Your personality: {st.session_state.meester_stijl}. "
                            "The student has graduated and MUST address YOU as 'Meester' or 'Master' (or 'Meesteres' / 'Mistress' if female). "
                            "Give them real-life daily structure, gentle discipline, and check-in tasks while strictly respecting their Hard Limits."
                        )
                    else:
                        etiquette_regel = (
                            f"You are {mentor} of The Sovereign Academy. Address the student with 'je'/'jij' (Dutch) or 'you' (English). "
                            f"The student MUST address YOU formally as '{titel_txt}' (and 'u' in Dutch). ONLY correct them if they address YOU with 'jij'/'je', your first name, or call YOU Master/Mistress/Meester/Meesteres before graduating."
                        )
                    regels = (
                        f"Respond strictly in natural {taal_txt}. Student profile: {st.session_state.sub_type}, Limits: {grenzen_txt}. "
                        f"{etiquette_regel} "
                        "TRIGGERS (add invisibly at the very end only when appropriate): [OPEN_NOTITIEBOEK] for daily check-in/reflection, [OPEN_GRENZENLIJST] to fill out limits."
                    )
                    gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.chat_history)
                    antwoord = vraag_mentor(f"{regels}\n\nHistory:\n{gesprek}\n\nResponse in {taal_txt}:")
                    herladen = False
                    if "[OPEN_NOTITIEBOEK]" in antwoord:
                        antwoord = antwoord.replace("[OPEN_NOTITIEBOEK]", "").strip()
                        st.session_state.notitieboek_actief = True
                        herladen = True
                    if "[OPEN_GRENZENLIJST]" in antwoord:
                        antwoord = antwoord.replace("[OPEN_GRENZENLIJST]", "").strip()
                        st.session_state.grenzenlijst_actief = True
                        herladen = True
                    st.write(antwoord)
                    st.session_state.chat_history.append(("assistant", antwoord))
                    if herladen:
                        st.rerun()

    if st.session_state.notitieboek_actief:
        idx = tab_namen.index("📓 Journal" if is_en else "📓 Notitieboekje")
        with tabs[idx]:
            notitie_tekst = st.text_area("Journal / Check-in:", height=120)
            if st.button("Submit / Indienen"):
                if notitie_tekst.strip() and api_key:
                    reactie = vraag_mentor(f"You are {mentor}. Respond calmly and supportively in {'English' if is_en else 'Dutch'} to this student journal entry: \"{notitie_tekst}\"")
                    st.session_state.notities.append({"tekst": notitie_tekst, "reactie": reactie})
                    st.rerun()
            for item in reversed(st.session_state.notities):
                with st.container(border=True):
                    st.write(item.get("tekst"))
                    st.markdown(f"**{mentor}:** {item.get('reactie')}")

    if st.session_state.grenzenlijst_actief:
        idx = tab_namen.index("🔒 Limits" if is_en else "🔒 Grenzenlijst")
        with tabs[idx]:
            st.subheader("🔒 Uitgebreide Sub-Checklist" if not is_en else "🔒 Complete Sub-Checklist")
            st.write("*Vul per categorie jouw wensen en grenzen in. Alles wat op 'Absolute No-Go' staat, wordt onvoorwaardelijk gerespecteerd.*" if not is_en else "*Fill out your desires and limits per category. Every 'Hard Limit' is strictly respected.*")
            opties = (
                "⚪ Nog niet ingevuld",
                "🟢 Ja / Heerlijk",
                "🟡 Nieuwsgierig / Voorzichtig",
                "🟠 Soft Limit (Alleen bij diep vertrouwen)",
                "🔴 Absolute No-Go (Hard Limit)"
            )
            nieuwe_grenzen = {}
            for categorie, items in CHECKLIST_CATEGORIEEN.items():
                with st.expander(categorie):
                    for item in items:
                        huidige_waarde = st.session_state.grenzen.get(item, "⚪ Nog niet ingevuld")
                        keuze = st.selectbox(item, opties, index=opties.index(huidige_waarde), key=f"chk_{item}")
                        if keuze != "⚪ Nog niet ingevuld":
                            nieuwe_grenzen[item] = keuze
            if st.button("💾 Sla volledige checklist op / Save Checklist"):
                st.session_state.grenzen = nieuwe_grenzen
                st.success("✅ Opgeslagen in jouw dossier! Jouw begeleider neemt al jouw keuzes en No-Go's direct mee.")
