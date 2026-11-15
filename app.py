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

st.set_page_config(page_title="The Sovereign Academy", page_icon="logo.png", layout="centered")
taal = st.radio("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English"), horizontal=True)
is_en = "English" in taal
st.title("🏛️ The Sovereign Academy")
st.caption("Guidance, Discipline, Safety & Conscious Submission" if is_en else "Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
sb_url, sb_key = st.secrets.get("SUPABASE_URL", ""), st.secrets.get("SUPABASE_KEY", "")
sb = create_client(sb_url, sb_key) if (sb_url and sb_key) else None
MEESTER_FOTOS = {"Meester Julian": "julian.jpg", "Meester Marcus": "marcus.jpg", "Meester Viktor": "victor.jpg", "Meesteres Elena": "elena.jpg", "Meesteres Sophia": "sophia.jpg", "Meesteres Clara": "clara.jpg"}

for k, v in [("fase", "Intake"), ("rol", "Submissive"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"), ("module_nr", 0), ("sub_type", "Classic Submissive"), ("notitieboek_actief", False), ("grenzenlijst_actief", False), ("verbond_actief", False), ("meester_stijl", ""), ("dom_examen_actief", False), ("schuilnaam", ""), ("pincode", ""), ("laatste_les_tijd", ""), ("zorgmodus", False), ("gids_open", False), ("steun_open", False), ("user_avatar", "👤"), ("straf_start", ""), ("sub_examen_gedaan", False)]:
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

def toon_steun_en_feedback(sleutel_prefix):
    st.subheader("☕ Support The Sovereign Academy" if is_en else "☕ Steun The Sovereign Academy")
    st.write("The Sovereign Academy remains 100% free and anonymous so everyone can learn safely. Would you like to help cover the AI costs?" if is_en else "The Sovereign Academy blijft 100% gratis en anoniem zodat iedereen veilig kan leren. Wil je helpen de AI-kosten te dekken?")
    st.link_button("💛 Make a voluntary donation (Ko-fi)" if is_en else "💛 Doe een vrijwillige donatie (Ko-fi)", "https://ko-fi.com")
    st.markdown("---")
    st.subheader("📚 Recommended Gear, Books & Care" if is_en else "📚 Aanbevolen Uitrusting, Boeken & Verzorging")
    st.caption("🔄 *This curated list is updated regularly with new safe recommendations.*" if is_en else "🔄 *Deze lijst wordt van tijd tot tijd aangevuld met nieuwe, zorgvuldig gekozen aanbevelingen.*")
    with st.container(border=True):
        st.markdown("**1. Comfort, Kneeling Pads & Aftercare**\nSupportive cushions for Nadu poses, luxury journals for check-ins, and natural massage oils for Aftercare." if is_en else "**1. Comfort, Knielkussens & Aftercare**\nOndersteunende kussens voor de Nadu-pose, luxe notitieboeken en natuurlijke massage-olie voor Aftercare.")
        st.link_button("🔗 View selection (Bol.com)" if is_en else "🔗 Bekijk selectie (Bol.com)", "https://bol.com")
    with st.container(border=True):
        st.markdown("**2. Safe Beginner Gear & Blindfolds**\nDiscreetly shipped quality sets (silk blindfolds, soft cuffs, and safety shears) for Phase 3." if is_en else "**2. Veilige Beginners-attributen & Blinddoeken**\nDiscreet verzonden kwaliteitssets (zijden blinddoeken, zachte boeien en veiligheidsscharen) voor Fase 3.")
        st.link_button("🔗 View selection (EasyToys / Lovehoney)" if is_en else "🔗 Bekijk selectie (EasyToys / Lovehoney)", "https://easytoys.nl")
    with st.container(border=True):
        st.markdown("**3. Essential Books on D/s Psychology & Communication**\nRecommended reading on consent, negotiation, and healthy power dynamics." if is_en else "**3. Verdiepende Boeken over D/s-Psychologie & Communicatie**\nAanbevolen literatuur over consent, negotiation en gezonde machtsverhoudingen.")
        st.link_button("🔗 View reading list (Amazon NL)" if is_en else "🔗 Bekijk boekenlijst (Amazon NL)", "https://amazon.nl")
    with st.container(border=True):
        st.markdown("**4. App-Controlled Play & Long-Distance Control (Lovense — Official Store)**\nPersonal Academy favorite: high-quality, app-controlled toys for long-distance D/s dynamics and remote control. Discreetly shipped from within Europe with a 1-year warranty (PayPal, Klarna & Card)." if is_en else "**4. App-Gestuurde Interactie & Afstandsbediening (Lovense — Officiële Shop)**\nPersoonlijke favoriet van de Academie: hoogwaardige, app-gestuurde toys voor D/s-dynamieken op afstand. Discreet en snel verzonden vanuit Europa (geen douanekosten, 1 jaar garantie, betalen via o.a. Klarna, PayPal of creditcard).")
        st.link_button("🔗 View Official Lovense Store" if is_en else "🔗 Bekijk Officiële Lovense Shop", "https://lovense.com")
    st.markdown("---")
    st.subheader("💡 Anonymous Feedback, Questions & Wishes" if is_en else "💡 Anonieme Feedback, Vragen & Wensen")
    st.write("Missing a topic, want to dive deeper into something, or have a question about the app? Leave an anonymous message below (100% private)." if is_en else "Mis je een onderwerp, wil je ergens dieper op ingaan of heb je een vraag over de app? Laat hieronder een anoniem bericht achter (100% privé).")
    fb_cat = st.selectbox("Topic:" if is_en else "Onderwerp:", ("Nieuw lesonderwerp / verdieping", "Vraag over de app", "Suggestie / verbeterpunt", "Compliment") if not is_en else ("New lesson topic / deeper dive", "Question about the app", "Suggestion / improvement", "Compliment"), key=f"{sleutel_prefix}_cat")
    fb_tekst = st.text_area("Your anonymous message:" if is_en else "Jouw anonieme bericht:", height=100, key=f"{sleutel_prefix}_txt")
    if st.button("📩 Send Anonymously" if is_en else "📩 Verstuur Anoniem", key=f"{sleutel_prefix}_btn") and fb_tekst.strip():
        if sb:
            sb.table("feedback").insert({"tijdstip": datetime.now().isoformat(), "onderwerp": fb_cat, "bericht": fb_tekst.strip()}).execute()
        st.success("✅ Thank you! Your message has been received anonymously." if is_en else "✅ Dankjewel! Je bericht is volledig anoniem ontvangen.")

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
        st.session_state.steun_open = False
        st.rerun()
    if st.button(("🛍️ Recommended & Support" if is_en else "🛍️ Aanbevolen & Steun") if not st.session_state.steun_open else ("🔙 Back to Academy" if is_en else "🔙 Terug naar de Academie")):
        st.session_state.steun_open = not st.session_state.steun_open
        st.session_state.gids_open = False
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

if st.session_state.steun_open:
    toon_steun_en_feedback("menu")
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

elif st.session_state.fase == "Praktijkkamer":
    mentor, mentor_img = st.session_state.mentor_naam, st.session_state.mentor_foto
    pauze_actief = False
    if st.session_state.laatste_les_tijd and not st.session_state.verbond_actief and not st.session_state.dom_examen_actief:
        verschil = datetime.now() - datetime.fromisoformat(st.session_state.laatste_les_tijd)
        if verschil < timedelta(hours=12):
            pauze_actief = True
            uren_over = 12 - int(verschil.total_seconds() // 3600)
            st.info(f"⏳ **Reflection pause active:** Let the material settle first. The next module opens in about **{uren_over} hours** (chat, Care Mode, and your notebook remain available 24/7)." if is_en else f"⏳ **Bezinkingspauze actief:** Laat de lesstof eerst rustig landen. Over ongeveer **{uren_over} uur** opent de volgende module (de chat, Zorgmodus en je notitieboekje blijven 24/7 bereikbaar).")

    if not pauze_actief and not st.session_state.verbond_actief and not st.session_state.dom_examen_actief:
        if st.session_state.module_nr < 6:
            if st.button(f"Start Module {st.session_state.module_nr + 1} ➡️"):
                st.session_state.module_nr += 1
                st.session_state.fase = "Les"
                sla_op()
                st.rerun()
        else:
            if st.button("👑 Proceed to Phase 3" if is_en else "👑 Ga naar Fase 3"):
                st.session_state.fase = "Afstuderen"
                sla_op()
                st.rerun()

    t_chat = "💬 Practice Room" if is_en else "💬 Praktijkkamer"
    t_disc = "⏱️ Discipline & Lines" if is_en else "⏱️ Discipline & Strafregels"
    t_shop = "🛍️ Recommended & Support" if is_en else "🛍️ Aanbevolen & Steun"
    t_note = "📓 Notebook" if is_en else "📓 Notitieboekje"
    t_lim = "🔒 Limits Checklist" if is_en else "🔒 Grenzenlijst"

    tab_namen = [t_chat, t_disc, t_shop]
    if st.session_state.notitieboek_actief:
        tab_namen.insert(1, t_note)
    if st.session_state.grenzenlijst_actief:
        tab_namen.insert(1, t_lim)
    tabs = st.tabs(tab_namen)

    with next(iter(tabs)):
        for role, text in st.session_state.chat_history:
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else st.session_state.user_avatar)):
                st.write(text)
        if user_input := st.chat_input("Type your response..." if is_en else "Typ je reactie..."):
            st.session_state.chat_history.append(("user", user_input))
            if "ROOD" in user_input.upper() or "RED" in user_input.upper():
                st.session_state.chat_history.append(("assistant", f"*{mentor} stops immediately.* Easy now, breathe. You are completely safe." if is_en else f"*{mentor} stopt direct.* Rustig maar, haal adem. Je bent helemaal veilig."))
                sla_op()
                st.rerun()
            zorg_txt = "CRITICAL: Student activated 24/7 Care Mode. Drop all strictness, offer immediate warmth, grounding, and emotional safety." if st.session_state.zorgmodus else ""
            taal_instr = "in English" if is_en else "in Dutch"
            regels = f"Respond {taal_instr} as {mentor} of The Sovereign Academy. {zorg_txt} Profile: {st.session_state.sub_type}, Limits: {st.session_state.grenzen}. Triggers: [OPEN_NOTITIEBOEK], [OPEN_GRENZENLIJST], [PROFIEL:Brat], [PROFIEL:Classic Submissive], [PROFIEL:Slave / Slavin]."
            gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.chat_history)
            antwoord = vraag_mentor(f"{regels}\n\nHistory:\n{gesprek}\n\nResponse:")
            for trig, state_k in (("[OPEN_NOTITIEBOEK]", "notitieboek_actief"), ("[OPEN_GRENZENLIJST]", "grenzenlijst_actief")):
                if trig in antwoord:
                    antwoord = antwoord.replace(trig, "").strip()
                    st.session_state[state_k] = True
            for p_naam in ("Brat", "Classic Submissive", "Slave / Slavin"):
                if f"[PROFIEL:{p_naam}]" in antwoord:
                    antwoord = antwoord.replace(f"[PROFIEL:{p_naam}]", "").strip()
                    st.session_state.sub_type = p_naam
            st.session_state.chat_history.append(("assistant", antwoord))
            sla_op()
            st.rerun()

    if st.session_state.notitieboek_actief:
        with tabs[tab_namen.index(t_note)]:
            notitie_tekst = st.text_area("Note / Check-in:" if is_en else "Notitie / Check-in:", height=120)
            if st.button("Submit" if is_en else "Indienen") and notitie_tekst.strip():
                reactie = vraag_mentor(f"You are {mentor}. Respond calmly {'in English' if is_en else 'in Dutch'} to: \"{notitie_tekst}\"")
                st.session_state.notities.append({"tekst": notitie_tekst, "reactie": reactie})
                sla_op()
                st.rerun()
            for item in reversed(st.session_state.notities):
                with st.container(border=True):
                    st.write(item.get("tekst"))
                    st.markdown(f"**{mentor}:** {item.get('reactie')}")

    if st.session_state.grenzenlijst_actief:
        with tabs[tab_namen.index(t_lim)]:
            opties = ("⚪ Nog niet ingevuld", "🟢 Ja / Heerlijk", "🟡 Nieuwsgierig / Voorzichtig", "🟠 Soft Limit", "🔴 Absolute No-Go")
            nieuwe_grenzen = {}
            for cat, items in CHECKLIST_CATEGORIEEN.items():
                with st.expander(cat):
                    for item in items:
                        keuze = st.selectbox(item, opties, index=opties.index(st.session_state.grenzen.get(item, "⚪ Nog niet ingevuld")), key=f"chk_{item}")
                        if keuze != "⚪ Nog niet ingevuld":
                            nieuwe_grenzen[item] = keuze
            if st.button("💾 Save checklist" if is_en else "💾 Sla checklist op"):
                st.session_state.grenzen = nieuwe_grenzen
                sla_op()
                st.success("✅ Saved to your dossier!" if is_en else "✅ Opgeslagen in jouw database-dossier!")

    with tabs[tab_namen.index(t_disc)]:
        st.subheader("⏱️ Corner & Pose Timer" if is_en else "⏱️ Strafhoek- & Pose-Timer")
        if not st.session_state.straf_start:
            if st.button("▶️ Clock In (Start Pose / Corner)" if is_en else "▶️ Inklokken (Start Houding / Strafhoek)"):
                st.session_state.straf_start = datetime.now().isoformat()
                st.rerun()
        else:
            start_dt = datetime.fromisoformat(st.session_state.straf_start)
            st.info(f"⏳ Active since **{start_dt.strftime('%H:%M:%S')}**..." if is_en else f"⏳ Bezig sinds **{start_dt.strftime('%H:%M:%S')}**...")
            if st.button("⏹️ Clock Out & Report" if is_en else "⏹️ Uitklokken & Melden"):
                minuten = round((datetime.now() - start_dt).total_seconds() / 60, 1)
                st.session_state.straf_start = ""
                st.session_state.chat_history.append(("user", f"*[Time log: I just completed {minuten} minutes in my pose / corner.]*" if is_en else f"*[Tijdregistratie: Ik heb zojuist {minuten} minuten in mijn houding / de strafhoek gezeten.]*"))
                sla_op()
                st.rerun()
        st.markdown("---")
        st.subheader("✍️ Automatic Line Writing Check" if is_en else "✍️ Automatische Strafregel-Controle")
        standaard_zin = "I will always address my mentor with respect." if is_en else "Ik spreek mijn begeleider altijd met respect aan."
        doel_zin = st.text_input("Assigned line (exact text):" if is_en else "Opgegeven strafregel (exacte tekst):", value=standaard_zin)
        aantal_regels = st.number_input("Number of assigned lines:" if is_en else "Aantal opgedragen regels:", min_value=1, max_value=100, value=10)
        ingevoerd = st.text_area("Type your lines here (one per line, no copy-pasting):" if is_en else "Typ hier jouw strafregels (elke regel op een nieuwe lijn, niet kopiëren/plakken):", height=160)
        if st.button("🔍 Check Lines" if is_en else "🔍 Controleer Strafregels"):
            regels_lijst = [r.strip() for r in ingevoerd.strip().splitlines() if r.strip()]
            fouten = [i + 1 for i, r in enumerate(regels_lijst) if r != doel_zin.strip()]
            if len(regels_lijst) != aantal_regels:
                st.error(f"❌ Incomplete: you wrote {len(regels_lijst)} out of {aantal_regels} lines." if is_en else f"❌ Onvolledig: je hebt {len(regels_lijst)} van de {aantal_regels} regels geschreven.")
            elif fouten:
                st.error(f"❌ Spelling or punctuation error on line(s): {fouten}. Check capitalization and periods!" if is_en else f"❌ Spel- of leestekenfout gevonden op regel(s): {fouten}. Let op hoofdletters en punten!")
            else:
                st.success(f"✅ All {aantal_regels} lines are 100% error-free!" if is_en else f"✅ Alle {aantal_regels} regels zijn 100% foutloos geschreven!")
                st.session_state.chat_history.append(("user", f"*[Lines completed: I wrote all {aantal_regels} lines without a single mistake.]*" if is_en else f"*[Strafregels voltooid: Ik heb alle {aantal_regels} regels foutloos uitgeschreven.]*"))
                sla_op()

    with tabs[tab_namen.index(t_shop)]:
        toon_steun_en_feedback("tab")
