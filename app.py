import streamlit as st
from google import genai
from google.genai import types
from curriculum import MODULES

st.set_page_config(page_title="The Sovereign Academy", page_icon="🏛️", layout="centered")
st.title("🏛️ The Sovereign Academy")
st.caption("Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
USER_AVATAR = "👤"

if "fase" not in st.session_state:
    st.session_state.fase = "Intake"
if "mentor_naam" not in st.session_state:
    st.session_state.mentor_naam = "Headmaster Bastian"
if "mentor_foto" not in st.session_state:
    st.session_state.mentor_foto = "bastian.jpg"
if "mentor_titel" not in st.session_state:
    st.session_state.mentor_titel = "Meneer of Mr"
if "module_nr" not in st.session_state:
    st.session_state.module_nr = 1
if "sub_type" not in st.session_state:
    st.session_state.sub_type = "Onbekend"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "notities" not in st.session_state:
    st.session_state.notities = []
if "notitieboek_actief" not in st.session_state:
    st.session_state.notitieboek_actief = False
if "grenzenlijst_actief" not in st.session_state:
    st.session_state.grenzenlijst_actief = False
if "grenzen" not in st.session_state:
    st.session_state.grenzen = {}

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("🏛️")
    st.header("📊 Academy Dossier")
    st.write(f"**Begeleider:** {st.session_state.mentor_naam}")
    st.write(f"**Aanspreekvorm:** U & {st.session_state.mentor_titel}")
    st.write(f"**Profiel:** {st.session_state.sub_type}")
    st.write(f"**Module Voortgang:** {st.session_state.module_nr} / 6 voltooid")
    st.progress(min(st.session_state.module_nr / 6, 1.0))
    st.markdown("---")
    st.info("🚨 **Noodrem:** Typ op elk gewenst moment **ROOD** in de chat om direct te stoppen.")

def vraag_mentor(prompt_tekst):
    client = genai.Client(api_key=api_key)
    alle_modellen = (
        m.name for m in client.models.list() 
        if "flash" in m.name.lower() 
        and "1.5" not in m.name 
        and "2.0" not in m.name 
        and "2.5" not in m.name
    )
    gekozen_model = next(alle_modellen, "gemini-3.8-flash")
    response = client.models.generate_content(
        model=gekozen_model,
        contents=prompt_tekst,
        config=types.GenerateContentConfig(max_output_tokens=2000)
    )
    return response.text

if st.session_state.fase == "Intake":
    st.subheader("🚪 Fase 1: Welkom & Nulmeting")
    st.write("*De zware houten deur valt achter je in het slot. In de ontvangsthal hangt een serene rust. Kies eerst door wie jij binnen de Academie begeleid wilt worden.*")
    
    mentor_keuze = st.radio("Kies jouw begeleider op de Academie:", (
        "Headmaster Bastian (Mannelijke leiding - aanspreken met U & Meneer / Mr)",
        "Headmistress Vale (Vrouwelijke leiding - aanspreken met U & Mevrouw / Miss)"
    ))
    
    st.markdown("---")
    v1 = st.radio("1. Hoe reageer jij van nature als iemand met gezag jou een duidelijke regel geeft?", (
        "Ik voel rust en wil de opdracht zo goed mogelijk uitvoeren.",
        "Ik krijg meteen de neiging om tegengas te geven en te kijken hoever ik kan gaan.",
        "Ik wil de controle het liefst helemaal loslaten en mij volledig voegen naar de ander."
    ))
    v2 = st.radio("2. Wat zoek jij op dit moment het meeste?", (
        "Duidelijke kaders, veiligheid en een mentor die mij helpt groeien.",
        "Spanning, uitdaging en iemand die onverstoorbaar blijft als ik de grenzen opzoek.",
        "Totale overgave, diepe discipline en vaste regels in het dagelijks leven."
    ))
    
    if st.button("Sla gegevens op & Start Module 1"):
        if "Vale" in mentor_keuze:
            st.session_state.mentor_naam = "Headmistress Vale"
            st.session_state.mentor_foto = "vale.jpg"
            st.session_state.mentor_titel = "Mevrouw of Miss"
        else:
            st.session_state.mentor_naam = "Headmaster Bastian"
            st.session_state.mentor_foto = "bastian.jpg"
            st.session_state.mentor_titel = "Meneer of Mr"
            
        if "tegengas" in v1 or "grenzen opzoek" in v2:
            st.session_state.sub_type = "Brat"
        elif "helemaal loslaten" in v1 or "Totale overgave" in v2:
            st.session_state.sub_type = "Slavin"
        else:
            st.session_state.sub_type = "Klassieke Submissive"
        st.session_state.fase = "Les"
        st.rerun()

elif st.session_state.fase == "Les":
    mod = MODULES.get(st.session_state.module_nr)
    st.subheader(f"📚 {mod.get('titel')}")
    
    with st.expander("📖 Verplichte Theorie (Lees aandachtig door)", expanded=True):
        st.markdown(mod.get("theorie"))
        
    st.markdown("---")
    st.write("📝 **Kennistest** (Beantwoord beide vragen goed om naar de praktijkkamer te gaan)")
    
    t1 = st.radio(f"Vraag 1: {mod.get('v1')}", mod.get("o1"))
    t2 = st.radio(f"Vraag 2: {mod.get('v2')}", mod.get("o2"))
    
    if st.button("Lever toets in"):
        if t1 == mod.get("a1") and t2 == mod.get("a2"):
            st.session_state.fase = "Praktijkkamer"
            mentor = st.session_state.mentor_naam
            titel = st.session_state.mentor_titel
            if not st.session_state.chat_history:
                st.session_state.chat_history.append(("assistant", f"*{mentor} slaat je dossier dicht en kijkt je rustig aan.* Goed. De basis staat, {st.session_state.sub_type}. Neem plaats. Binnen deze Academie spreek je mij aan met 'u' en '{titel}'. De titel van Meester of Meesteres verdien je pas na je opleiding. Vertel mij nu eens in je eigen woorden: waar liep je tot nu toe tegenaan, en wat hoop je hier te vinden?"))
            else:
                st.session_state.chat_history.append(("assistant", f"*{mentor} knikt goedkeurend.* Je hebt {mod.get('titel')} succesvol afgerond. Hoe voelt deze stof voor jou, en roept het vragen op?"))
            st.rerun()
        else:
            st.error(f"❌ **{st.session_state.mentor_naam} schudt het hoofd:** *\"Nog niet helemaal juist. Lees de theorie hierboven nog eens rustig door voordat je verdergaat.\"*")

elif st.session_state.fase == "Praktijkkamer":
    mentor = st.session_state.mentor_naam
    mentor_img = st.session_state.mentor_foto
    titel = st.session_state.mentor_titel

    if st.session_state.module_nr <= 6:
        col_info, col_btn = st.columns((3, 1))
        with col_info:
            st.info(f"✅ Module {st.session_state.module_nr} afgerond. Bespreek je gedachten met {mentor} of ga door naar de volgende les.")
        with col_btn:
            if st.session_state.module_nr < 6:
                if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
                    st.session_state.module_nr += 1
                    st.session_state.fase = "Les"
                    st.rerun()
            else:
                st.success("🎓 Alle 6 modules voltooid!")

    tab_namen = ["💬 Praktijkkamer"]
    if st.session_state.notitieboek_actief:
        tab_namen.append("📓 Notitieboekje")
    if st.session_state.grenzenlijst_actief:
        tab_namen.append("🔒 Grenzenlijst")

    if len(tab_namen) > 1:
        tabs = st.tabs(tab_namen)
        tab_chat = tabs
    else:
        tab_chat = st.container()

    with tab_chat:
        for role, text in st.session_state.chat_history:
            avatar_img = mentor_img if role == "assistant" else USER_AVATAR
            with st.chat_message(role, avatar=avatar_img):
                st.write(text)
                
        if user_input := st.chat_input(f"Typ je reactie naar {mentor} (gebruik 'u' en '{titel}')..."):
            st.session_state.chat_history.append(("user", user_input))
            with st.chat_message("user", avatar=USER_AVATAR):
                st.write(user_input)
                
            if "ROOD" in user_input.upper():
                nood_tekst = f"*{mentor} stopt direct, laat elke vorm van controle los en pakt een zachte deken.* Rustig maar. Het is klaar. Haal even diep adem, je bent helemaal veilig."
                st.session_state.chat_history.append(("assistant", nood_tekst))
                with st.chat_message("assistant", avatar=mentor_img):
                    st.write(nood_tekst)
            else:
                with st.chat_message("assistant", avatar=mentor_img):
                    if not api_key:
                        st.warning("⚠️ Voeg eerst je gratis Google API-sleutel toe in de Secrets.")
                    else:
                        try:
                            gespreksverloop = ""
                            for rol, bericht in st.session_state.chat_history:
                                naam = "Leerling" if rol == "user" else mentor
                                gespreksverloop += f"{naam}: {bericht}\n\n"
                            
                            grenzen_tekst = str(st.session_state.grenzen) if st.session_state.grenzen else "Nog niet ingevuld."
                            
                            systeem_instructie = (
                                f"Je bent {mentor}, leidinggevende van The Sovereign Academy. Profiel leerling: {st.session_state.sub_type}. "
                                f"Afgeronde module: {st.session_state.module_nr}. Bekende grenzenlijst leerling: {grenzen_tekst}. "
                                "STRIKTE ETIQUETTE & AANSPREEKVORM (ZEER BELANGRIJK): "
                                f"- De leerling zit nog in de opleidingsfase en MOET jou aanspreken met 'u' en '{titel}'. "
                                "- Als de leerling 'jij', 'je', 'jouw', jouw voornaam gebruikt, of jou nu al 'Meester', 'Master', 'Meesteres' of 'Mistress' noemt, corrigeer haar dan direct op een kalme, strenge maar waardige manier. Leg uit dat 'u' en '{titel}' verplicht zijn op de Academie, en dat de titel Meester(es)/Master/Mistress pas gebruikt mag worden zodra ze haar opleiding heeft afgerond en haar eigen vaste Meester(es) heeft. "
                                "SCHRIJFSTIJL & REGELS: Schrijf natuurlijk, vloeiend en menselijk Nederlands. Kalm, ervaren, beschermend, nooit sadistisch. "
                                "Leer de sub dat bewuste overgave kracht is. Gebruik het gespreksgeheugen en respecteer altijd haar grenzen. "
                                "TRIGGERS (zet deze alleen onzichtbaar onderaan je bericht als het in het gesprek past): "
                                "- Zet [OPEN_NOTITIEBOEK] als je een reflectie-opdracht of dagelijkse check-in geeft. "
                                "- Zet [OPEN_GRENZENLIJST] als het tijd is dat zij haar wensen en harde grenzen (Sub-Checklist) invult.\n\n"
                                f"GESPREK:\n{gespreksverloop}\nAntwoord van {mentor}:"
                            )
                            antwoord = vraag_mentor(systeem_instructie)
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
                        except Exception as e:
                            st.error(f"Technische reden: {e}")

    if st.session_state.notitieboek_actief:
        idx = tab_namen.index("📓 Notitieboekje")
        with tabs[idx]:
            st.subheader("📓 Dagelijkse Check-in & Real-Life Rapportage")
            moment = st.selectbox("Moment:", ("Middag Check-in", "Avond Check-in", "Tussentijdse reflectie"))
            notitie_tekst = st.text_area("Schrijf hier eerlijk wat er in je omgaat:", height=120)
            if st.button("Leg notitie op het bureau"):
                if notitie_tekst.strip() and api_key:
                    with st.spinner(f"{mentor} leest je notitie..."):
                        reactie = vraag_mentor(f"Je bent {mentor}. Reageer kalm en ondersteunend op deze {moment} van je leerling: \"{notitie_tekst}\"")
                        st.session_state.notities.append({"moment": moment, "tekst": notitie_tekst, "reactie": reactie})
                        st.rerun()
            for item in reversed(st.session_state.notities):
                with st.container(border=True):
                    st.caption(f"📌 **{item.get('moment')}**")
                    st.write(item.get("tekst"))
                    st.markdown(f"**{mentor}:** {item.get('reactie')}")

    if st.session_state.grenzenlijst_actief:
        idx = tab_namen.index("🔒 Grenzenlijst")
        with tabs[idx]:
            st.subheader("🔒 Mijn Sub-Checklist (Grenzen & Voorkeuren)")
            st.write(f"*Jouw antwoorden worden direct opgenomen in jouw dossier. {mentor} respecteert elke 'Absolute No-Go' onvoorwaardelijk.*")
            opties = ("🟢 Dit ken ik / wil ik", "🟡 Nieuwsgierig / voorzichtig verkennen", "🔴 Absolute No-Go (Hard Limit)")
            g1 = st.selectbox("Fysieke discipline (paddle / spanking)", opties)
            g2 = st.selectbox("Vastgebonden / geketend worden (Bondage)", opties)
            g3 = st.selectbox("Strikte dagelijkse regels & avondklok", opties)
            g4 = st.selectbox("Poses & etiquette (Nadu, toestemming vragen)", opties)
            g5 = st.selectbox("Petplay / Littlespace / Rollenspel", opties)
            if st.button("Sla grenzen op in mijn dossier"):
                st.session_state.grenzen = {
                    "Fysieke discipline": g1, "Bondage": g2, "Dagelijkse regels": g3, "Poses & etiquette": g4, "Stromingen": g5
                }
                st.success(f"✅ Jouw grenzen zijn opgeslagen. {mentor} neemt deze vanaf nu mee in elk gesprek!")
