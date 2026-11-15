import streamlit as st
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from supabase import create_client
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
sb_url, sb_key = st.secrets.get("SUPABASE_URL", ""), st.secrets.get("SUPABASE_KEY", "")
sb = create_client(sb_url, sb_key) if (sb_url and sb_key) else None
MEESTER_FOTOS = {
    "Meester Julian": "julian.jpg", "Meester Marcus": "marcus.jpg", "Meester Victor": "victor.jpg",
    "Meesteres Elena": "elena.jpg", "Meesteres Sophia": "sophia.jpg", "Meesteres Clara": "clara.jpg"
}

for k, v in [("fase", "Intake"), ("rol", "Submissive"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"), ("module_nr", 0), ("sub_type", "Classic Submissive"), ("notitieboek_actief", False), ("grenzenlijst_actief", False), ("verbond_actief", False), ("meester_stijl", ""), ("dom_examen_actief", False), ("schuilnaam", ""), ("pincode", ""), ("laatste_les_tijd", ""), ("zorgmodus", False)]:
    if k not in st.session_state:
        st.session_state[k] = v
for k in ("chat_history", "notities"):
    if k not in st.session_state:
        st.session_state[k] = []
if "grenzen" not in st.session_state:
    st.session_state.grenzen = {}

def sla_op():
    if sb and st.session_state.schuilnaam and st.session_state.pincode:
        data = {k: st.session_state[k] for k in ("schuilnaam", "pincode", "rol", "mentor_naam", "mentor_foto", "module_nr", "sub_type", "grenzen", "notities", "chat_history", "verbond_actief", "meester_stijl", "laatste_les_tijd")}
        sb.table("dossiers").upsert(data).execute()

def vraag_mentor(prompt_tekst):
    client = genai.Client(api_key=api_key)
    modellen = (m.name for m in client.models.list() if "flash" in m.name.lower() and not any(x in m.name for x in ("1.5", "2.0", "2.5")))
    return client.models.generate_content(model=next(modellen, "gemini-3.8-flash"), contents=prompt_tekst, config=types.GenerateContentConfig(max_output_tokens=2000)).text

is_vale = "Vale" in st.session_state.mentor_naam
titel_txt = ("Master / Mistress" if is_en else "Meester / Meesteres") if st.session_state.verbond_actief else (("Ma'am or Miss" if is_en else "Mevrouw of Miss") if is_vale else ("Sir or Mr" if is_en else "Meneer of Mr"))

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("👑" if st.session_state.verbond_actief else "🏛️")
    st.header("📊 Academy Dossier")
    if st.session_state.schuilnaam:
        st.success(f"🔑 **{st.session_state.schuilnaam}**")
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
    if st.button("🏛️ Kennismaking Staf & Meesters" if not st.session_state.get("gids_open") else "🔙 Terug naar de Academie"):
        st.session_state.gids_open = not st.session_state.get("gids_open", False)
        st.rerun()
    if st.button("🆘 Zorgmodus (Direct hulp/rust)" if not st.session_state.zorgmodus else "✅ Zorgmodus sluiten"):
        st.session_state.zorgmodus = not st.session_state.zorgmodus
        st.rerun()
    if st.session_state.schuilnaam:
        if st.button("🚪 Uitloggen (Dossier veilig sluiten)"):
            sla_op()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    else:
        if st.button("🔄 Sessie resetten"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


if st.session_state.zorgmodus:
    st.warning("🆘 **24/7 Zorgmodus Actief:** Je bent helemaal veilig. Adem rustig in en uit. Jouw begeleider staat nu buiten elke rol naast je.")
if st.session_state.get("gids_open"):
    st.subheader("🏛️ Kennismaking: Staf, Meesters & Meesteressen")
    st.write("Ontdek welke begeleiders en stijlen van leidinggeven er binnen The Sovereign Academy bestaan.")
    for (geslacht, profiel), m_info in MEESTERS.items():
        naam = m_info.get("naam")
        with st.container(border=True):
            c1, c2 = st.columns((1, 3))
            with c1:
                st.image(MEESTER_FOTOS.get(naam, "bastian.jpg"), width=120)
            with c2:
                st.markdown(f"### {naam} — *{profiel}*")
                st.write(m_info.get("stijl"))
    st.stop()
    

if st.session_state.fase == "Intake":
    try:
        st.image("academy.jpg", use_container_width=True)
    except Exception:
        pass
    st.subheader("🏛️ Welkom bij The Sovereign Academy")
    with st.container(border=True):
        st.markdown("**Wat is The Sovereign Academy?**\nEen veilige, oordeelvrije leeromgeving voor bewuste overgave (Submissive) én verantwoord leiderschap (Dominant). 100% gratis en anoniem.")
        if sb:
            with st.expander("🔑 Heb je al een anonieme Dossiercode? Log hier in (of maak er een aan)"):
                c1, c2 = st.columns(2)
                in_naam = c1.text_input("Schuilnaam (bijv. Vlinder):")
                in_pin = c2.text_input("4-cijferige pincode:", type="password", max_chars=4)
                if st.button("📂 Open of Maak Dossier"):
                    if in_naam.strip() and len(in_pin.strip()) == 4:
                        res = sb.table("dossiers").select("*").eq("schuilnaam", in_naam.strip()).execute()
                        if res.data:
                            d = res.data
                            if d.get("pincode") == in_pin.strip():
                                for k in ("schuilnaam", "pincode", "rol", "mentor_naam", "mentor_foto", "module_nr", "sub_type", "grenzen", "notities", "chat_history", "verbond_actief", "meester_stijl", "laatste_les_tijd"):
                                    if d.get(k) is not None:
                                        st.session_state[k] = d[k]
                                st.session_state.notitieboek_actief = bool(st.session_state.notities)
                                st.session_state.grenzenlijst_actief = bool(st.session_state.grenzen)
                                st.session_state.fase = "Praktijkkamer" if st.session_state.module_nr > 0 else "Intake"
                                st.rerun()
                            else:
                                st.error("❌ Onjuiste pincode voor deze schuilnaam.")
                        else:
                            st.session_state.schuilnaam, st.session_state.pincode = in_naam.strip(), in_pin.strip()
                            sla_op()
                            st.success(f"✅ Nieuw anoniem dossier aangemaakt voor **{in_naam.strip()}**! Kies hieronder je traject.")
                    else:
                        st.warning("Vul een schuilnaam en een 4-cijferige pincode in.")

    st.subheader("👥 Maak kennis met de Academie-leiding")
    col_b, col_v = st.columns(2)
    with col_b:
        with st.container(border=True):
            try:
                st.image("bastian.jpg", width=140)
            except Exception:
                st.write("🎩")
            st.markdown("**Headmaster Bastian**\n*Kalm, gestructureerd en scherpzinnig.* Bastian bewaakt de kaders met vaderlijke rust, heldere regels en onverstoorbaar gezag.")
    with col_v:
        with st.container(border=True):
            try:
                st.image("vale.jpg", width=140)
            except Exception:
                st.write("👑")
            st.markdown("**Headmistress Vale**\n*Elegant, veeleisend en intuïtief.* Vale combineert warme geborgenheid met verfijnde etiquette en ziet direct waar jij nog vasthoudt.")

    with st.expander("🏛️ Bekijk alle Meesters & Meesteressen van de Academie (Fase 3)"):
        for (geslacht, profiel), m_info in MEESTERS.items():
            st.markdown(f"**{m_info.get('naam')}** (*{profiel} — {geslacht}*): {m_info.get('stijl')}")

    st.subheader("🚪 Start jouw traject")
    avatar_optie = st.radio("Kies jouw eigen profiel-icoon in de chat:", ("👤 Neutraal", "👩 Vrouw", "👨 Man"), horizontal=True)
    st.session_state.user_avatar = avatar_optie.split()
    rol_keuze = st.radio("Kies jouw traject:", ("Submissive (6 Modules + Begeleiding & Fase 3)", "Dominant (6 Modules + 60 Examenvragen & Praktijkexamen)"))
    mentor_keuze = st.radio("Kies jouw begeleider:", ("Headmaster Bastian", "Headmistress Vale"))
    if st.button("Start Module 1 ➡️"):
        st.session_state.rol = "Dominant" if "Dominant" in rol_keuze else "Submissive"
        st.session_state.mentor_naam = mentor_keuze
        st.session_state.mentor_foto = "vale.jpg" if "Vale" in mentor_keuze else "bastian.jpg"
        st.session_state.sub_type = "Dominant in Opleiding" if st.session_state.rol == "Dominant" else "Classic Submissive"
        st.session_state.module_nr = 1
        st.session_state.fase = "Les"
        sla_op()
        st.rerun()


elif st.session_state.fase == "Les":
    nr = max(1, st.session_state.module_nr)
    if st.session_state.rol == "Dominant":
        mod = DOM_MODULES.get(nr)
        st.subheader(f"🎓 {mod.get('titel')}")
        with st.expander("📖 Uitgebreide Theorie", expanded=True):
            st.markdown(mod.get("theorie"))
        antw = [st.radio(q.get("v"), q.get("o"), key=f"dq_{nr}_{i}") == q.get("a") for i, q in enumerate(mod.get("vragen"))]
        if st.button("Lever examenonderdeel in"):
            if sum(antw) >= 8:
                st.session_state.laatste_les_tijd = datetime.now().isoformat()
                st.session_state.fase = "Praktijkkamer"
                if not st.session_state.chat_history:
                    st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} knikt goedkeurend ({sum(antw)}/10).* Bespreek hier je inzichten uit Module {nr}."))
                sla_op()
                st.rerun()
            else:
                st.error(f"❌ Score: {sum(antw)}/10 (minimaal 8 vereist). Lees de theorie nog eens door.")

    else:
        mod = MODULES.get(nr)
        st.subheader(f"📚 {mod.get('titel')}")
        with st.expander("📖 Verplichte Theorie", expanded=True):
            st.markdown(mod.get("theorie"))
        t1 = st.radio(f"Vraag 1: {mod.get('v1')}", mod.get("o1"))
        t2 = st.radio(f"Vraag 2: {mod.get('v2')}", mod.get("o2"))
        if st.button("Lever toets in"):
            if t1 == mod.get("a1") and t2 == mod.get("a2"):
                st.session_state.laatste_les_tijd = datetime.now().isoformat()
                st.session_state.fase = "Praktijkkamer"
                if not st.session_state.chat_history:
                    st.session_state.chat_history.append(("assistant", f"*{st.session_state.mentor_naam} slaat je dossier dicht.* Goed. Spreek mij aan met 'u' en '{titel_txt}'. Vertel mij: wat zoek je hier?"))
                sla_op()
                st.rerun()
            else:
                st.error("❌ Nog niet helemaal juist. Lees de theorie nog eens door.")

elif st.session_state.fase == "Afstuderen":
    if st.session_state.rol == "Dominant":
        st.subheader("👑 Fase 3: Het Live Praktijkexamen (Dominant)")
        scenario = st.radio("Kies je examenscenario:", ("Scenario 1: Onrustige Brat ('stuiteren').", "Scenario 2: Submissive met zware Subdrop.", "Scenario 3: Onzekere beginner bij Soft Limit."))
        if st.button("🎭 Start Live Praktijkexamen"):
            st.session_state.dom_examen_actief, st.session_state.meester_stijl, st.session_state.fase = True, scenario, "Praktijkkamer"
            st.session_state.chat_history = [("assistant", f"*[{st.session_state.mentor_naam}]:* Examen gestart.\n\n**Simulatie-Sub:** *friemelt onrustig aan haar mouw* \"Ik weet niet of ik dit wel kan vanavond...\"")]
            sla_op()
            st.rerun()

    else:
        st.subheader("🎓 Fase 3: Diploma-uitreiking & Het Verbond")
        voorkeur = st.radio("Ik wens begeleid te worden door een:", ("Mannelijk", "Vrouwelijk"), horizontal=True)
        for (geslacht, profiel), info in MEESTERS.items():
            if geslacht == voorkeur:
                naam = info.get("naam")
                with st.container(border=True):
                    c1, c2 = st.columns((1, 3))
                    with c1:
                        st.image(MEESTER_FOTOS.get(naam, "bastian.jpg"), width=120)
                    with c2:
                        st.markdown(f"### {naam} — *{profiel}*")
                        st.write(info.get("stijl"))
                        if st.button(f"👑 Sluit Verbond met {naam}", key=f"btn_{naam}"):
                            st.session_state.mentor_naam, st.session_state.meester_stijl = naam, info.get("stijl")
                            st.session_state.mentor_foto = MEESTER_FOTOS.get(naam, "bastian.jpg")
                            st.session_state.verbond_actief = st.session_state.notitieboek_actief = st.session_state.grenzenlijst_actief = True
                            st.session_state.chat_history, st.session_state.fase = [("assistant", info.get("intro_nl"))], "Praktijkkamer"
                            sla_op()
                            st.rerun()


elif st.session_state.fase == "Praktijkkamer":
    mentor, mentor_img = st.session_state.mentor_naam, st.session_state.mentor_foto
    pauze_actief = False
    if st.session_state.laatste_les_tijd and not st.session_state.verbond_actief and not st.session_state.dom_examen_actief:
        verschil = datetime.now() - datetime.fromisoformat(st.session_state.laatste_les_tijd)
        if verschil < timedelta(hours=12):
            pauze_actief = True
            uren_over = 12 - int(verschil.total_seconds() // 3600)
            st.info(f"⏳ **Bezinkingspauze actief:** Laat de lesstof eerst rustig landen. Over ongeveer **{uren_over} uur** opent de volgende module (de chat, Zorgmodus en je notitieboekje blijven 24/7 bereikbaar).")

    if not pauze_actief and not st.session_state.verbond_actief and not st.session_state.dom_examen_actief:
        if st.session_state.module_nr < 6:
            if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
                st.session_state.module_nr += 1
                st.session_state.fase = "Les"
                sla_op()
                st.rerun()
        else:
            if st.button("👑 Ga naar Fase 3"):
                st.session_state.fase = "Afstuderen"
                sla_op()
                st.rerun()

    tab_namen = ["💬 Praktijkkamer", "🛍️ Aanbevolen & Steun"]
    if st.session_state.notitieboek_actief:
        tab_namen.insert(1, "📓 Notitieboekje")
    if st.session_state.grenzenlijst_actief:
        tab_namen.insert(1, "🔒 Grenzenlijst")
    tabs = st.tabs(tab_namen)

    with next(iter(tabs)):
        for role, text in st.session_state.chat_history:
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else "👤")):
                st.write(text)
        if user_input := st.chat_input("Typ je reactie..."):
            st.session_state.chat_history.append(("user", user_input))
            if "ROOD" in user_input.upper() or "RED" in user_input.upper():
                st.session_state.chat_history.append(("assistant", f"*{mentor} stopt direct.* Rustig maar, haal adem. Je bent helemaal veilig."))
                sla_op()
                st.rerun()
            zorg_txt = "CRITICAL: Student activated 24/7 Care Mode. Drop all strictness, offer immediate warmth, grounding, and emotional safety." if st.session_state.zorgmodus else ""
            regels = f"Respond in Dutch as {mentor} of The Sovereign Academy. {zorg_txt} Profile: {st.session_state.sub_type}, Limits: {st.session_state.grenzen}. Triggers: [OPEN_NOTITIEBOEK], [OPEN_GRENZENLIJST]."
            gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.chat_history)
            antwoord = vraag_mentor(f"{regels}\n\nHistory:\n{gesprek}\n\nResponse:")
            for trig, state_k in (("[OPEN_NOTITIEBOEK]", "notitieboek_actief"), ("[OPEN_GRENZENLIJST]", "grenzenlijst_actief")):
                if trig in antwoord:
                    antwoord = antwoord.replace(trig, "").strip()
                    st.session_state[state_k] = True
            st.session_state.chat_history.append(("assistant", antwoord))
            sla_op()
            st.rerun()

    if st.session_state.notitieboek_actief:
        with tabs[tab_namen.index("📓 Notitieboekje")]:
            notitie_tekst = st.text_area("Notitie / Check-in:", height=120)
            if st.button("Indienen") and notitie_tekst.strip():
                reactie = vraag_mentor(f"You are {mentor}. Respond calmly in Dutch to: \"{notitie_tekst}\"")
                st.session_state.notities.append({"tekst": notitie_tekst, "reactie": reactie})
                sla_op()
                st.rerun()
            for item in reversed(st.session_state.notities):
                with st.container(border=True):
                    st.write(item.get("tekst"))
                    st.markdown(f"**{mentor}:** {item.get('reactie')}")

    if st.session_state.grenzenlijst_actief:
        with tabs[tab_namen.index("🔒 Grenzenlijst")]:
            opties = ("⚪ Nog niet ingevuld", "🟢 Ja / Heerlijk", "🟡 Nieuwsgierig / Voorzichtig", "🟠 Soft Limit", "🔴 Absolute No-Go")
            nieuwe_grenzen = {}
            for cat, items in CHECKLIST_CATEGORIEEN.items():
                with st.expander(cat):
                    for item in items:
                        keuze = st.selectbox(item, opties, index=opties.index(st.session_state.grenzen.get(item, "⚪ Nog niet ingevuld")), key=f"chk_{item}")
                        if keuze != "⚪ Nog niet ingevuld":
                            nieuwe_grenzen[item] = keuze
            if st.button("💾 Sla checklist op"):
                st.session_state.grenzen = nieuwe_grenzen
                sla_op()
                st.success("✅ Opgeslagen in jouw database-dossier!")

    with tabs[tab_namen.index("🛍️ Aanbevolen & Steun")]:
        st.subheader("☕ Steun The Sovereign Academy")
        st.write("The Sovereign Academy blijft 100% gratis en anoniem zodat iedereen veilig kan leren. Wil je helpen de AI-kosten te dekken?")
        st.link_button("💛 Doe een vrijwillige donatie (Ko-fi)", "https://ko-fi.com")
        st.markdown("---")
        st.subheader("📚 Aanbevolen Uitrusting & Literatuur")
        with st.container(border=True):
            st.markdown("**1. Comfort & Houdingen (Knielkussens & Verzorging)**\nEen zacht ondersteunend kussen beschermt je knieën tijdens de Nadu-pose, en natuurlijke olie helpt bij ontspanning tijdens Aftercare.")
            st.link_button("🔗 Bekijk bij partner (Bol.com)", "https://bol.com")
        with st.container(border=True):
            st.markdown("**2. Veilige Beginners-attributen & Blinddoeken**\nDiscreet verzonden kwaliteitssets (zijden blinddoeken, zachte boeien en veiligheidsscharen) voor wie in Fase 3 verder wil verkennen.")
            st.link_button("🔗 Bekijk bij partner (EasyToys / Lovehoney)", "https://easytoys.nl")
