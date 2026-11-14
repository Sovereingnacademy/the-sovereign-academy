import streamlit as st
from google import genai
from google.genai import types
from curriculum import MODULES
from checklist import CHECKLIST_CATEGORIEEN
from meesters import MEESTERS
from dom_curriculum import DOM_MODULES

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")

taal = st.radio("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English"), horizontal=True)
is_en = "English" in taal

st.title("🏛️ The Sovereign Academy")
st.caption("Guidance, Discipline, Safety & Conscious Submission" if is_en else "Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
USER_AVATAR = "👤"

for key, val in [
    ("fase", "Intake"), ("rol", "Submissive"), ("mentor_naam", "Headmaster Bastian"),
    ("mentor_foto", "bastian.jpg"), ("module_nr", 0), ("sub_type", "Classic Submissive"),
    ("notitieboek_actief", False), ("grenzenlijst_actief", False), ("verbond_actief", False),
    ("meester_stijl", ""), ("dom_examen_actief", False)
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
    st.write(f"**Track / Rol:** {st.session_state.rol}")
    st.write(f"**{'Dominant' if st.session_state.verbond_actief else 'Mentor'}:** {st.session_state.mentor_naam}")
    if st.session_state.rol == "Submissive":
        st.write(f"**Address / Titel:** {titel_txt}")
        st.write(f"**Profile:** {st.session_state.sub_type}")
    if st.session_state.verbond_actief or st.session_state.dom_examen_actief:
        st.success("👑 **Fase 3 Actief**")
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
    st.subheader("🏛️ Welcome to The Sovereign Academy" if is_en else "🏛️ Welkom bij The Sovereign Academy")
    with st.container(border=True):
        st.markdown(
            "**What is The Sovereign Academy?**\nA safe, judgment-free learning environment for conscious submission AND responsible, protective dominance. Choose your path below." if is_en else
            "**Wat is The Sovereign Academy?**\nEen veilige, oordeelvrije leeromgeving voor zowel bewuste overgave (Submissive) als verantwoord, beschermend leiderschap (Dominant). Kies hieronder jouw traject."
        )
    rol_keuze = st.radio("Select your path / Kies jouw traject:", (
        "Submissive (6 Modules + Personal Mentoring & Phase 3 Bond)",
        "Dominant (6 Intensive Modules + 60 Exam Questions & Live Practice Exam)"
    ))
    mentor_keuze = st.radio("Choose your Academy guide / Kies jouw begeleider:", ("Headmaster Bastian", "Headmistress Vale"))
    
    if "Submissive" in rol_keuze:
        v1 = st.radio("1. How do you react to a clear rule from authority?" if is_en else "1. Hoe reageer jij op een duidelijke regel?", (
            "I feel calm and want to follow it precisely." if is_en else "Ik voel rust en wil de opdracht goed uitvoeren.",
            "I tend to push back and test boundaries." if is_en else "Ik geef graag tegengas en test de grenzen.",
            "I want to surrender control completely." if is_en else "Ik wil de controle helemaal loslaten."
        ))
    else:
        v1 = st.radio("1. What is your primary motivation as a Dominant?" if is_en else "1. Wat is jouw belangrijkste drijfveer als Dominant?", (
            "Providing safety, structure, and helping a submissive grow." if is_en else "Veiligheid, structuur en geborgenheid bieden zodat een sub kan groeien.",
            "Challenging boundaries safely while staying calm and grounded." if is_en else "Grenzen op een verantwoorde manier verleggen met rust en zelfbeheersing."
        ))

    if st.button("Start Module 1 ➡️"):
        st.session_state.rol = "Dominant" if "Dominant" in rol_keuze else "Submissive"
        st.session_state.mentor_naam = mentor_keuze
        st.session_state.mentor_foto = "vale.jpg" if "Vale" in mentor_keuze else "bastian.jpg"
        if st.session_state.rol == "Submissive":
            st.session_state.sub_type = "Brat" if ("tegengas" in v1 or "push back" in v1) else ("Slave / Slavin" if ("loslaten" in v1 or "completely" in v1) else "Classic Submissive")
        else:
            st.session_state.sub_type = "Dominant in Opleiding"
        st.session_state.module_nr = 1
        st.session_state.fase = "Les"
        st.rerun()

elif st.session_state.fase == "Les":
    nr = max(1, st.session_state.module_nr)
    if st.session_state.rol == "Dominant":
        mod = DOM_MODULES.get(nr)
        st.subheader(f"🎓 {mod.get('titel')}")
        with st.expander("📖 Uitgebreide Theorie (Bestudeer dit grondig)", expanded=True):
            st.markdown(mod.get("theorie"))
        st.markdown("---")
        st.write("📝 **Kennistest (Minimaal 8 van de 10 vragen goed om te slagen)**")
        antwoorden_gebruiker = []
        for idx, q in enumerate(mod.get("vragen")):
            keuze = st.radio(q.get("v"), q.get("o"), key=f"dom_q_{nr}_{idx}")
            antwoorden_gebruiker.append((keuze, q.get("a")))
        if st.button("Lever examenonderdeel in"):
            score = sum(1 for gekozen, juist in antwoorden_gebruiker if gekozen == juist)
            if score >= 8:
                st.success(f"✅ Geslaagd! Je hebt **{score} van de 10** vragen goed beantwoord.")
                st.session_state.fase = "Praktijkkamer"
                if not st.session_state.chat_history:
                    st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} legt de examenuitslag voor zich neer.* Goed werk ({score}/10). Als Dominant draag je een grote verantwoordelijkheid. Bespreek hier je inzichten uit Module {nr}, of ga door naar de volgende module."))
                st.rerun()
            else:
                st.error(f"❌ Je hebt **{score} van de 10** goed (minimaal 8 vereist). Lees de theorie nog eens aandachtig door en probeer het opnieuw.")
    else:
        mod = MODULES.get(nr)
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
    if st.session_state.rol == "Dominant":
        st.subheader("👑 Fase 3: Het Live Praktijkexamen (Dominant)")
        st.info("Je hebt alle 6 modules en 60 examenvragen succesvol afgerond! Nu volgt de praktijktest: kies een simulatie-scenario waarin jij laat zien hoe je veilig, kalm en beschermend leidinggeeft.")
        scenario = st.radio("Kies je examenscenario:", (
            "Scenario 1: Een onrustige Brat ('stuiteren') die grenzen test en onrustig is in de avond.",
            "Scenario 2: Een submissive die 24 uur na een sessie last heeft van een zware Subdrop en aan zichzelf twijfelt.",
            "Scenario 3: Een onzekere beginner die een spannende Soft Limit wil verkennen maar dichtklapt."
        ))
        if st.button("🎭 Start Live Praktijkexamen"):
            st.session_state.dom_examen_actief = True
            st.session_state.meester_stijl = scenario
            st.session_state.chat_history = [("assistant", f"*[{st.session_state.mentor_naam} opent het observatievenster]:* Het examen begint nu. Reageer zoals je in het echt als Dominant zou doen.\n\n**Simulatie-Sub:** *kijkt onrustig naar de grond en friemelt aan haar mouw* \"Ik weet niet of ik dit wel kan... mijn hoofd zit helemaal vol en ik heb eigenlijk helemaal geen zin om braaf te luisteren vanavond.\"")]
            st.session_state.fase = "Praktijkkamer"
            st.rerun()
    else:
        st.subheader("🎓 Fase 3: Diploma-uitreiking & Het Verbond")
        st.success(f"Gefeliciteerd! Je hebt alle 6 modules afgerond. Jouw profiel: **{st.session_state.sub_type}**.")
        voorkeur = st.radio("Ik wens begeleid te worden door een:", ("Mannelijk (Meester)", "Vrouwelijk (Meesteres)"), horizontal=True)
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
    
    if not st.session_state.verbond_actief and not st.session_state.dom_examen_actief:
        if st.session_state.module_nr < 6:
            if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
                st.session_state.module_nr += 1
                st.session_state.fase = "Les"
                st.rerun()
        else:
            btn_tekst = "👑 Start Live Praktijkexamen" if st.session_state.rol == "Dominant" else "🎓 Studeer af & Ga naar Fase 3 (Het Verbond) 👑"
            if st.button(btn_tekst):
                st.session_state.fase = "Afstuderen"
                st.rerun()

    tab_namen = ["💬 Praktijkkamer"]
    if st.session_state.notitieboek_actief:
        tab_namen.append("📓 Notitieboekje")
    if st.session_state.grenzenlijst_actief:
        tab_namen.append("🔒 Grenzenlijst")

    tabs = st.tabs(tab_namen) if len(tab_namen) > 1 else None
    tab_chat = next(iter(tabs)) if tabs else st.container()

    with tab_chat:
        for role, text in st.session_state.chat_history:
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else USER_AVATAR)):
                st.write(text)
                
        if user_input := st.chat_input("Typ je reactie..."):
            st.session_state.chat_history.append(("user", user_input))
            with st.chat_message("user", avatar=USER_AVATAR):
                st.write(user_input)
            if "ROOD" in user_input.upper() or "RED" in user_input.upper():
                nood = f"*{mentor} stopt direct.* Rustig maar, haal adem. Je bent helemaal veilig."
                st.session_state.chat_history.append(("assistant", nood))
                st.rerun()
            else:
                with st.chat_message("assistant", avatar=mentor_img):
                    taal_txt = "English" if is_en else "Dutch"
                    if st.session_state.dom_examen_actief:
                        regels = (
                            f"Respond in {taal_txt}. You are playing TWO roles in a live BDSM Dominant exam: "
                            f"1) **Simulatie-Sub** (acting out: {st.session_state.meester_stijl}). React realistically to how the Dominant treats you (calm down if they offer safety/structure, or resist if they get angry/harsh). "
                            f"2) **[{mentor} - Mentor Feedback]** at the bottom in brackets, briefly grading their leadership, empathy, and boundary safety."
                        )
                    elif st.session_state.rol == "Dominant":
                        regels = f"Respond in {taal_txt}. You are {mentor}, training a student Dominant (Module {st.session_state.module_nr}/6). Discuss leadership, aftercare, subdrop, and safe boundary stretching on an equal, collegial mentor level."
                    elif st.session_state.verbond_actief:
                        regels = f"Respond in {taal_txt}. You are {mentor}, dedicated Dominant ({st.session_state.meester_stijl}). Require 'Meester'/'Master' or 'Meesteres'/'Mistress'. Respect limits: {st.session_state.grenzen}."
                    else:
                        regels = (
                            f"Respond in {taal_txt}. You are {mentor} of The Sovereign Academy (Profile: {st.session_state.sub_type}, Limits: {st.session_state.grenzen}). "
                            f"Address the student with 'je'/'jij'. Require them to address YOU as '{titel_txt}' and 'u'. ONLY correct them if they address YOU with 'jij'/'je', your first name, or call YOU Master/Mistress/Meester/Meesteres. "
                            "TRIGGERS (add invisibly at the very end only when appropriate): [OPEN_NOTITIEBOEK], [OPEN_GRENZENLIJST]."
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

    if st.session_state.notitieboek_actief and tabs:
        with tabs[tab_namen.index("📓 Notitieboekje")]:
            notitie_tekst = st.text_area("Notitie / Check-in:", height=120)
            if st.button("Indienen"):
                if notitie_tekst.strip() and api_key:
                    reactie = vraag_mentor(f"You are {mentor}. Respond calmly and supportively in {'English' if is_en else 'Dutch'} to this student journal entry: \"{notitie_tekst}\"")
                    st.session_state.notities.append({"tekst": notitie_tekst, "reactie": reactie})
                    st.rerun()
            for item in reversed(st.session_state.notities):
                with st.container(border=True):
                    st.write(item.get("tekst"))
                    st.markdown(f"**{mentor}:** {item.get('reactie')}")

    if st.session_state.grenzenlijst_actief and tabs:
        with tabs[tab_namen.index("🔒 Grenzenlijst")]:
            st.subheader("🔒 Uitgebreide Sub-Checklist")
            opties = ("⚪ Nog niet ingevuld", "🟢 Ja / Heerlijk", "🟡 Nieuwsgierig / Voorzichtig", "🟠 Soft Limit", "🔴 Absolute No-Go")
            nieuwe_grenzen = {}
            for categorie, items in CHECKLIST_CATEGORIEEN.items():
                with st.expander(categorie):
                    for item in items:
                        huidige = st.session_state.grenzen.get(item, "⚪ Nog niet ingevuld")
                        keuze = st.selectbox(item, opties, index=opties.index(huidige), key=f"chk_{item}")
                        if keuze != "⚪ Nog niet ingevuld":
                            nieuwe_grenzen[item] = keuze
                            if st.button("💾 Sla volledige checklist op"):
    st.session_state.grenzen = nieuwe_grenzen
    st.success("✅ Opgeslagen in jouw dossier!")
