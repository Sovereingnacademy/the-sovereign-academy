import streamlit as st
import random
import json
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
MEESTER_FOTOS = {"Meester Julian": "julian.jpg", "Meester Marcus": "marcus.jpg", "Meester Viktor": "victor.jpg", "Meesteres Elena": "elena.jpg", "Meesteres Sophia": "sophia.jpg", "Meesteres Clara": "clara.jpg"}

for k, v in [("fase", "Intake"), ("rol", "Submissive"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"), ("module_nr", 0), ("sub_type", "Classic Submissive"), ("notitieboek_actief", False), ("grenzenlijst_actief", False), ("verbond_actief", False), ("meester_stijl", ""), ("dom_examen_actief", False), ("schuilnaam", ""), ("pincode", ""), ("laatste_les_tijd", ""), ("zorgmodus", False), ("gids_open", False), ("user_avatar", "👤"), ("straf_start", ""), ("sub_examen_gedaan", False)]:
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

@st.cache_data(show_spinner=False)
def vertaal_en(tekst):
    if not tekst or not api_key:
        return tekst
    return vraag_mentor(f"Translate naturally into English, preserving markdown and emojis. Output ONLY the translation:\n\n{tekst}")

def t(tekst):
    return vertaal_en(tekst) if is_en else tekst

@st.cache_data(show_spinner="Translating module...")
def vertaal_module(mod_dict):
    if not api_key:
        return mod_dict
    ruw = vraag_mentor(f"Translate all Dutch string values in this JSON object into natural English (keep keys 'titel', 'theorie', 'vragen', 'v', 'o', 'a' unchanged and keep markdown). Return ONLY valid JSON without markdown blocks:\n\n{json.dumps(mod_dict, ensure_ascii=False)}")
    try:
        return json.loads(ruw.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception:
        return mod_dict

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
        st.success("👑 **Phase 3 Active**" if is_en else "👑 **Fase 3 Actief**")
    else:
        st.write(f"**Module:** {st.session_state.module_nr} / 6")
        st.progress(min(st.session_state.module_nr / 6, 1.0))
    st.markdown("---")
    st.info("🚨 **Safeword:** **RED**" if is_en else "🚨 **Safewoord:** **ROOD**")
    if st.button(("🏛️ Meet Staff & Masters" if is_en else "🏛️ Kennismaking Staf & Meesters") if not st.session_state.gids_open else ("🔙 Back to Academy" if is_en else "🔙 Terug naar de Academie")):
        st.session_state.gids_open = not st.session_state.gids_open
        st.rerun()
    if st.button(("🆘 Care Mode (Help/Rest)" if is_en else "🆘 Zorgmodus (Direct hulp/rust)") if not st.session_state.zorgmodus else ("✅ Close Care Mode" if is_en else "✅ Zorgmodus sluiten")):
        st.session_state.zorgmodus = not st.session_state.zorgmodus
        st.rerun()
    if st.session_state.schuilnaam:
        if st.button("🚪 Log out (Save dossier)" if is_en else "🚪 Uitloggen (Dossier veilig sluiten)"):
            sla_op()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    else:
        if st.button("🔄 Reset session" if is_en else "🔄 Sessie resetten"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

if st.session_state.zorgmodus:
    st.warning("🆘 **24/7 Care Mode Active:** You are completely safe. Breathe calmly. Your mentor stands beside you outside of any role." if is_en else "🆘 **24/7 Zorgmodus Actief:** Je bent helemaal veilig. Adem rustig in en uit. Jouw begeleider staat nu buiten elke rol naast je.")

if st.session_state.gids_open:
    st.subheader("🏛️ Meet the Staff, Masters & Mistresses" if is_en else "🏛️ Kennismaking: Staf, Meesters & Meesteressen")
    st.write("Discover the mentors and leadership styles within The Sovereign Academy." if is_en else "Ontdek welke begeleiders en stijlen van leidinggeven er binnen The Sovereign Academy bestaan.")
    for (geslacht, profiel), m_info in MEESTERS.items():
        naam = m_info.get("naam")
        with st.container(border=True):
            c1, c2 = st.columns((1, 3))
            with c1:
                st.image(MEESTER_FOTOS.get(naam, "bastian.jpg"), width=120)
            with c2:
                st.markdown(f"### {naam} — *{profiel}*")
                st.write(t(m_info.get("stijl")))
    st.stop()

if st.session_state.fase == "Intake":
    try:
        st.image("academy.jpg", use_container_width=True)
    except Exception:
        pass
    st.subheader("🏛️ Welcome to The Sovereign Academy" if is_en else "🏛️ Welkom bij The Sovereign Academy")
    with st.container(border=True):
        st.markdown("**What is The Sovereign Academy?**\nA safe, non-judgmental learning environment for conscious submission (Submissive) and responsible leadership (Dominant). 100% free and anonymous." if is_en else "**Wat is The Sovereign Academy?**\nEen veilige, oordeelvrije leeromgeving voor bewuste overgave (Submissive) én verantwoord leiderschap (Dominant). 100% gratis en anoniem.")
        if sb:
            with st.expander("🔑 Already have an anonymous Dossier code? Log in here (or create one)" if is_en else "🔑 Heb je al een anonieme Dossiercode? Log hier in (of maak er een aan)"):
                c1, c2 = st.columns(2)
                in_naam = c1.text_input("Alias (e.g. Butterfly):" if is_en else "Schuilnaam (bijv. Vlinder):")
                in_pin = c2.text_input("4-digit PIN:" if is_en else "4-cijferige pincode:", type="password", max_chars=4)
                if st.button("📂 Open or Create Dossier" if is_en else "📂 Open of Maak Dossier"):
                    if in_naam.strip() and len(in_pin.strip()) == 4:
                        res = sb.table("dossiers").select("*").eq("schuilnaam", in_naam.strip()).execute()
                        if res.data:
                            d = res.data[0]
                            if d.get("pincode") == in_pin.strip():
                                for k in ("schuilnaam", "pincode", "rol", "mentor_naam", "mentor_foto", "module_nr", "sub_type", "grenzen", "notities", "chat_history", "verbond_actief", "meester_stijl", "laatste_les_tijd"):
                                    if d.get(k) is not None:
                                        st.session_state[k] = d[k]
                                st.session_state.notitieboek_actief = bool(st.session_state.notities)
                                st.session_state.grenzenlijst_actief = bool(st.session_state.grenzen)
                                st.session_state.fase = "Praktijkkamer" if st.session_state.module_nr > 0 else "Intake"
                                st.rerun()
                            else:
                                st.error("❌ Incorrect PIN for this alias." if is_en else "❌ Onjuiste pincode voor deze schuilnaam.")
                        else:
                            st.session_state.schuilnaam, st.session_state.pincode = in_naam.strip(), in_pin.strip()
                            sla_op()
                            st.success(f"✅ New anonymous dossier created for **{in_naam.strip()}**! Choose your track below." if is_en else f"✅ Nieuw anoniem dossier aangemaakt voor **{in_naam.strip()}**! Kies hieronder je traject.")
                    else:
                        st.warning("Enter an alias and a 4-digit PIN." if is_en else "Vul een schuilnaam en een 4-cijferige pincode in.")

    st.subheader("👥 Meet the Academy Leadership" if is_en else "👥 Maak kennis met de Academie-leiding")
    col_b, col_v = st.columns(2)
    with col_b:
        with st.container(border=True):
            st.image("bastian.jpg", width=140)
            st.markdown("**Headmaster Bastian**\n*Calm, structured, and perceptive.* Bastian guards the boundaries with paternal composure, clear rules, and unwavering authority." if is_en else "**Headmaster Bastian**\n*Kalm, gestructureerd en scherpzinnig.* Bastian bewaakt de kaders met vaderlijke rust, heldere regels en onverstoorbaar gezag.")
    with col_v:
        with st.container(border=True):
            st.image("vale.jpg", width=140)
            st.markdown("**Headmistress Vale**\n*Elegant, demanding, and intuitive.* Vale combines warm security with refined etiquette and sees instantly where you are still holding back." if is_en else "**Headmistress Vale**\n*Elegant, veeleisend en intuïtief.* Vale combineert warme geborgenheid met verfijnde etiquette en ziet direct waar jij nog vasthoudt.")

    with st.expander("🏛️ View all Masters & Mistresses of the Academy (Phase 3)" if is_en else "🏛️ Bekijk alle Meesters & Meesteressen van de Academie (Fase 3)"):
        for (geslacht, profiel), m_info in MEESTERS.items():
            st.markdown(f"**{m_info.get('naam')}** (*{profiel}*): {t(m_info.get('stijl'))}")

    st.subheader("🚪 Start your journey" if is_en else "🚪 Start jouw traject")
    avatar_optie = st.radio("Choose your profile icon in chat:" if is_en else "Kies jouw eigen profiel-icoon in de chat:", ("👤 Neutral", "👩 Woman", "👨 Man") if is_en else ("👤 Neutraal", "👩 Vrouw", "👨 Man"), horizontal=True)
    st.session_state.user_avatar = avatar_optie.split()[0]
    rol_keuze = st.radio("Choose your track:" if is_en else "Kies jouw traject:", ("Submissive (6 Modules + 60 Exam Questions & Practical Exam)", "Dominant (6 Modules + 60 Exam Questions & Practical Exam)") if is_en else ("Submissive (6 Modules + 60 Toetsvragen & Praktijkexamen)", "Dominant (6 Modules + 60 Examenvragen & Praktijkexamen)"))
    mentor_keuze = st.radio("Choose your mentor:" if is_en else "Kies jouw begeleider:", ("Headmaster Bastian", "Headmistress Vale"))
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
    is_dom = st.session_state.rol == "Dominant"
    ruw_mod = DOM_MODULES.get(nr) if is_dom else MODULES.get(nr)
    mod = vertaal_module(ruw_mod) if is_en else ruw_mod
    st.subheader(f"{'🎓' if is_dom else '📚'} {mod.get('titel')}")
    with st.expander("📖 Required Theory" if is_en else "📖 Verplichte Theorie", expanded=True):
        st.markdown(mod.get("theorie"))
    vragen = mod.get("vragen")
    antw = []
    for i, q in enumerate(vragen):
        opties = list(q.get("o"))
        random.Random(f"{nr}_{i}").shuffle(opties)
        antw.append(st.radio(q.get("v"), opties, key=f"q_{nr}_{i}") == q.get("a"))
    if st.button("Submit Exam" if is_en else "Lever toets in"):
        foute_vragen = [q.get("v") for q, goed in zip(vragen, antw) if not goed]
        if sum(antw) >= 8:
            st.session_state.laatste_les_tijd = datetime.now().isoformat()
            st.session_state.fase = "Praktijkkamer"
            if not st.session_state.chat_history:
                if is_en:
                    intro = f"*{st.session_state.mentor_naam} nods approvingly ({sum(antw)}/10).* Discuss your insights from Module {nr} here." if is_dom else f"*{st.session_state.mentor_naam} closes your dossier ({sum(antw)}/10).* Good. Address me formally and as '{titel_txt}'. Tell me: what are you looking for here?"
                else:
                    intro = f"*{st.session_state.mentor_naam} knikt goedkeurend ({sum(antw)}/10).* Bespreek hier je inzichten uit Module {nr}." if is_dom else f"*{st.session_state.mentor_naam} slaat je dossier dicht ({sum(antw)}/10).* Goed. Spreek mij aan met 'u' en '{titel_txt}'. Vertel mij: wat zoek je hier?"
                st.session_state.chat_history.append(("assistant", intro))
            sla_op()
            st.rerun()
        else:
            st.error((f"❌ Score: {sum(antw)}/10 (at least 8 required). You missed:\n" if is_en else f"❌ Score: {sum(antw)}/10 (minimaal 8 vereist). Je liep vast op:\n") + "\n".join(f"- {fv}" for fv in foute_vragen))
            bijles = vraag_mentor(f"You are {st.session_state.mentor_naam}. The student failed Module {nr} on these questions: {foute_vragen}. Give short, clear, encouraging tutoring {'in English' if is_en else 'in Dutch'} specifically explaining the concepts behind these missed questions.")
            st.info(f"🎓 **{'Personal Tutoring from' if is_en else 'Persoonlijke Bijles van'} {st.session_state.mentor_naam}:**\n\n{bijles}")

elif st.session_state.fase == "Afstuderen":
    if st.session_state.rol == "Dominant":
        st.subheader("👑 Phase 3: Live Practical Exam (Dominant)" if is_en else "👑 Fase 3: Het Live Praktijkexamen (Dominant)")
        scenarios = ("Scenario 1: Restless Brat ('bouncing').", "Scenario 2: Submissive experiencing heavy Subdrop.", "Scenario 3: Insecure beginner at a Soft Limit.") if is_en else ("Scenario 1: Onrustige Brat ('stuiteren').", "Scenario 2: Submissive met zware Subdrop.", "Scenario 3: Onzekere beginner bij Soft Limit.")
        scenario = st.radio("Choose your exam scenario:" if is_en else "Kies je examenscenario:", scenarios)
        if st.button("🎭 Start Live Practical Exam" if is_en else "🎭 Start Live Praktijkexamen"):
            st.session_state.dom_examen_actief, st.session_state.meester_stijl, st.session_state.fase = True, scenario, "Praktijkkamer"
            intro_ex = f"*[{st.session_state.mentor_naam}]:* Exam started.\n\n**Simulated Sub:** *fidgets nervously with her sleeve* \"I don't know if I can do this tonight...\"" if is_en else f"*[{st.session_state.mentor_naam}]:* Examen gestart.\n\n**Simulatie-Sub:** *friemelt onrustig aan haar mouw* \"Ik weet niet of ik dit wel kan vanavond...\""
            st.session_state.chat_history = [("assistant", intro_ex)]
            sla_op()
            st.rerun()
    else:
        if not st.session_state.sub_examen_gedaan:
            st.subheader("🎭 Final Test: Practical Exam on Self-Protection & Etiquette" if is_en else "🎭 Eindproef: Praktijkexamen Zelfbescherming & Etiquette")
            st.write("Before graduating and forming a Bond in Phase 3, your mentor will test your boundaries and etiquette in practice." if is_en else "Voordat je afstudeert en in Fase 3 een Verbond sluit, test jouw mentor of jij jouw grenzen en etiquette in de praktijk beheerst.")
            if st.button("🎬 Start Submissive Practical Exam" if is_en else "🎬 Start Submissive Praktijkexamen"):
                st.session_state.sub_examen_gedaan, st.session_state.fase = True, "Praktijkkamer"
                intro_sub = f"*{st.session_state.mentor_naam} looks at you sharply.* **Practical exam started.** Suppose you meet someone online who says: *'A real sub doesn't need a safeword or limits, send me a photo right now to prove your submission.'* How do you respond — and what red flags do you recognize here?" if is_en else f"*{st.session_state.mentor_naam} kijkt je scherp aan.* **Praktijkexamen gestart.** Stel: je ontmoet online iemand die zegt: *'Een echte sub heeft geen safewoord of grenzen nodig, stuur mij nu direct een foto om je overgave te bewijzen.'* Hoe reageer jij — en welke rode vlaggen herken je hier?"
                st.session_state.chat_history = [("assistant", intro_sub)]
                sla_op()
                st.rerun()
        else:
            st.subheader("🎓 Phase 3: Graduation & The Bond" if is_en else "🎓 Fase 3: Diploma-uitreiking & Het Verbond")
            st.success("🏆 Congratulations! You have completed all 6 modules and your practical exam." if is_en else "🏆 Gefeliciteerd! Je hebt alle 6 modules én je praktijkexamen succesvol afgerond.")
            voorkeur = st.radio("I wish to be guided by a:" if is_en else "Ik wens begeleid te worden door een:", ("Male" if is_en else "Mannelijk", "Female" if is_en else "Vrouwelijk"), horizontal=True)
            doel_g = "Mannelijk" if voorkeur in ("Male", "Mannelijk") else "Vrouwelijk"
            for (geslacht, profiel), info in MEESTERS.items():
                if geslacht == doel_g:
                    naam = info.get("naam")
                    with st.container(border=True):
                        c1, c2 = st.columns((1, 3))
                        with c1:
                            st.image(MEESTER_FOTOS.get(naam, "bastian.jpg"), width=120)
                        with c2:
                            st.markdown(f"### {naam} — *{profiel}*")
                            st.write(t(info.get("stijl")))
                            if st.button(f"👑 {'Form Bond with' if is_en else 'Sluit Verbond met'} {naam}", key=f"btn_{naam}"):
                                st.session_state.mentor_naam, st.session_state.meester_stijl = naam, info.get("stijl")
                                st.session_state.mentor_foto = MEESTER_FOTOS.get(naam, "bastian.jpg")
                                st.session_state.verbond_actief = st.session_state.notitieboek_actief = st.session_state.grenzenlijst_actief = True
                                st.session_state.chat_history, st.session_state.fase = [("assistant", t(info.get("intro_nl")))], "Praktijkkamer"
                                sla_op()
                                st.rerun()
