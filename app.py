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

st.set_page_config(page_title="The Sovereign Academy", page_icon="logo.jpg", layout="centered")
LOGO_URL = "https://githubusercontent.com"
st.markdown(f"""
    <script>
        var doc = window.parent.document;
        doc.querySelectorAll("link[rel*='icon']").forEach(e => e.remove());
        var link = doc.createElement('link');
        link.rel = 'icon';
        link.type = 'image/jpeg';
        link.href = '{LOGO_URL}';
        doc.head.appendChild(link);
        var apple = doc.createElement('link');
        apple.rel = 'apple-touch-icon';
        apple.href = '{LOGO_URL}';
        doc.head.appendChild(apple);
    </script>
    <style>
        .top-btn {{ position: fixed; bottom: 85px; right: 18px; z-index: 999; background: #262730; color: white; border: 1px solid #555; border-radius: 50%; width: 42px; height: 42px; text-align: center; line-height: 40px; font-size: 18px; text-decoration: none; box-shadow: 0 2px 6px rgba(0,0,0,0.4); }}
    </style>
    <div id="top-anchor"></div>
    <a href="#top-anchor" class="top-btn" title="Naar boven">⬆️</a>
""", unsafe_allow_html=True)

taal = st.radio("🌍 Language / Taal:", ("🇳🇱 Nederlands", "🇬🇧 English"), horizontal=True)
is_en = "English" in taal
st.caption("☰ *Tip (mobiel): Tik linksboven op **>>** om het Academy Menu, je Dossier & 24/7 Zorgmodus te openen.*" if not is_en else "☰ *Tip (mobile): Tap **>>** at the top left to open the Academy Menu, Dossier & 24/7 Care Mode.*")

col_logo, col_titel = st.columns((1, 5))
with col_logo:
    st.image("logo.jpg", width=85)
with col_titel:
    st.title("The Sovereign Academy")
    st.caption("Guidance, Discipline, Safety & Conscious Submission" if is_en else "Begeleiding, Discipline, Veiligheid & Bewuste Overgave")

api_key = st.secrets.get("GEMINI_API_KEY", "")
sb_url, sb_key = st.secrets.get("SUPABASE_URL", ""), st.secrets.get("SUPABASE_KEY", "")
sb = create_client(sb_url, sb_key) if (sb_url and sb_key) else None
MEESTER_FOTOS = {"Meester Julian": "julian.jpg", "Meester Marcus": "marcus.jpg", "Meester Viktor": "victor.jpg", "Meesteres Elena": "elena.jpg", "Meesteres Sophia": "sophia.jpg", "Meesteres Clara": "clara.jpg"}

if sb and "bezoek_geteld" not in st.session_state:
    st.session_state.bezoek_geteld = True
    try:
        sb.table("bezoekers").insert({"tijdstip": datetime.now().isoformat()}).execute()
    except Exception:
        pass

for k, v in [("fase", "Intake"), ("rol", "Submissive"), ("mentor_naam", "Headmaster Bastian"), ("mentor_foto", "bastian.jpg"), ("module_nr", 0), ("sub_type", "Classic Submissive"), ("notitieboek_actief", False), ("grenzenlijst_actief", False), ("verbond_actief", False), ("meester_stijl", ""), ("dom_examen_actief", False), ("schuilnaam", ""), ("pincode", ""), ("laatste_les_tijd", ""), ("zorgmodus", False), ("gids_open", False), ("steun_open", False), ("user_avatar", "👤"), ("straf_start", ""), ("sub_examen_gedaan", False), ("poging", 0), ("safewoord", "ROOD"), ("partner_naam", "")]:
    if k not in st.session_state:
        st.session_state[k] = v
for k in ("chat_history", "notities"):
    if k not in st.session_state:
        st.session_state[k] = []
if "grenzen" not in st.session_state:
    st.session_state.grenzen = {}

def sla_op():
    if sb and st.session_state.schuilnaam and st.session_state.pincode:
        data = {k: st.session_state[k] for k in ("schuilnaam", "pincode", "rol", "mentor_naam", "mentor_foto", "module_nr", "sub_type", "grenzen", "notities", "chat_history", "verbond_actief", "meester_stijl", "laatste_les_tijd", "partner_naam", "safewoord")}
        try:
            sb.table("dossiers").upsert(data).execute()
        except Exception:
            for extra_k in ("partner_naam", "safewoord"):
                data.pop(extra_k, None)
            sb.table("dossiers").upsert(data).execute()

def vraag_mentor(prompt_tekst):
    try:
        client = genai.Client(api_key=api_key)
        modellen = (m.name for m in client.models.list() if "flash" in m.name.lower() and not any(x in m.name for x in ("1.5", "2.0", "2.5")))
        return client.models.generate_content(model=next(modellen, "gemini-3.8-flash"), contents=prompt_tekst, config=types.GenerateContentConfig(max_output_tokens=4000)).text
    except Exception:
        return "*(The connection to the Academy server paused briefly. Take a calm breath and resend your message in a few seconds.)*" if is_en else "*(De verbinding met de Academie-server hapert heel even. Adem rustig door en verstuur je bericht over een paar seconden opnieuw.)*"

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
    st.caption("ℹ️ *Disclosure: Some links on this page are affiliate links. If you purchase through them, The Sovereign Academy may earn a small commission at no extra cost to you, helping keep this platform free. This list is updated regularly.*" if is_en else "ℹ️ *Transparantie: Sommige links op deze pagina zijn affiliate-links. Als je via deze links iets bestelt, ontvangt The Sovereign Academy een kleine commissie (zonder extra kosten voor jou) om dit platform gratis te houden. Deze lijst wordt van tijd tot tijd aangevuld.*")
    with st.container(border=True):
        st.markdown("**1. Safe Beginner Gear & Blindfolds**\nDiscreetly shipped quality sets (silk blindfolds, soft cuffs, and safety shears) for Phase 3." if is_en else "**2. Veilige Beginners-attributen & Blinddoeken**\nDiscreet verzonden kwaliteitssets (zijden blinddoeken, zachte boeien en veiligheidsscharen) voor Fase 3.")
        st.link_button("🔗 View selection (EasyToys)" if is_en else "🔗 Bekijk selectie (EasyToys)", "https://easytoys.nl")
    with st.container(border=True):
        st.markdown("**2. The Sovereign Academy Workbook & Reflection Journal (Coming Soon on Amazon)**\nOur own physical & digital workbook with printable Limits Checklists, Aftercare trackers, and D/s reflection exercises." if is_en else "**3. Het Officiële Sovereign Academy Werkboek & Reflectie-Journaal (Binnenkort op Amazon)**\nOns eigen fysieke & digitale werkboek met invulbare Grenzenlijsten, Aftercare-checklists en D/s-reflectieoefeningen.")
    with st.container(border=True):
        st.markdown("**3. App-Controlled Play & Long-Distance Control (Lovense — Official Store)**\nPersonal Academy favorites: high-quality, app-controlled toys for long-distance D/s dynamics and remote control. Discreetly shipped from within Europe with a 1-year warranty (PayPal, Klarna & Card)." if is_en else "**4. App-Gestuurde Interactie & Afstandsbediening (Lovense — Officiële Shop)**\nPersoonlijke favorieten van de Academie: hoogwaardige, app-gestuurde toys voor D/s-dynamieken op afstand. Discreet en snel verzonden vanuit Europa (geen douanekosten, 1 jaar garantie, betalen via o.a. Klarna, PayPal of creditcard).")
        st.link_button("🔗 Lovense Domi 2 (Mini Wand — Academy Favorite!)" if is_en else "🔗 Lovense Domi 2 (Mini Wand — Favoriet van de Academie!)", "https://lovense.com")
        c_l1, c_l2 = st.columns(2)
        c_l1.link_button("🔗 Lovense Lush 4 (Remote Egg)", "https://lovense.com")
        c_l2.link_button("🔗 Lovense Hush 2 (Remote Plug)", "https://lovense.com")
        c_l3, c_l4 = st.columns(2)
        c_l3.link_button("🔗 Lovense Gemini (Nipple Clamps)", "https://lovense.com")
        c_l4.link_button("🔗 Lovense Edge 2 (For Him)", "https://lovense.com")
    st.markdown("---")
    st.subheader("💡 Anonymous Feedback, Questions & Wishes" if is_en else "💡 Anonieme Feedback, Vragen & Wensen")
    st.write("Missing a topic, want to dive deeper into something, or have a question about the app? Leave an anonymous message below (100% private)." if is_en else "Mis je een onderwerp, wil je ergens dieper op ingaan of heb je een vraag over de app? Laat hieronder een anoniem bericht achter (100% privé).")
    fb_cat = st.selectbox("Topic:" if is_en else "Onderwerp:", ("Nieuw lesonderwerp / verdieping", "Vraag over de app", "Suggestie / verbeterpunt", "Compliment") if not is_en else ("New lesson topic / deeper dive", "Question about the app", "Suggestion / improvement", "Compliment"), key=f"{sleutel_prefix}_cat")
    fb_tekst = st.text_area("Your anonymous message:" if is_en else "Jouw anonieme bericht:", height=100, key=f"{sleutel_prefix}_txt")
    if st.button("📩 Send Anonymously" if is_en else "📩 Verstuur Anoniem", key=f"{sleutel_prefix}_btn") and fb_tekst.strip():
        code = st.session_state.schuilnaam if st.session_state.schuilnaam else f"SA-{random.randint(1000, 9999)}"
        if sb:
            try:
                sb.table("feedback").insert({"tijdstip": datetime.now().isoformat(), "onderwerp": fb_cat, "bericht": fb_tekst.strip(), "ticket_code": code}).execute()
            except Exception:
                sb.table("feedback").insert({"tijdstip": datetime.now().isoformat(), "onderwerp": fb_cat, "bericht": fb_tekst.strip()}).execute()
        st.success(f"✅ Thank you! Your message has been received. Save your code **{code}** to read our personal reply below!" if is_en else f"✅ Dankjewel! Je bericht is anoniem ontvangen. Bewaar jouw code **{code}** om hieronder ons persoonlijke antwoord te lezen!")

    if sb:
        with st.expander("📬 Read reply from the Academy (enter your alias or ticket code)" if is_en else "📬 Lees reactie van de Academie-leiding (vul je schuilnaam of ticketcode in)"):
            zoek_code = st.text_input("Your alias or ticket code (e.g. SA-4821):" if is_en else "Jouw schuilnaam of ticketcode (bijv. SA-4821):", value=st.session_state.schuilnaam, key=f"{sleutel_prefix}_chk")
            if zoek_code.strip():
                try:
                    berichten = sb.table("feedback").select("*").eq("ticket_code", zoek_code.strip()).execute().data
                except Exception:
                    berichten = []
                if not berichten:
                    st.info("No messages found for this code yet." if is_en else "Geen berichten gevonden voor deze code.")
                for b in reversed(berichten):
                    with st.container(border=True):
                        st.markdown(f"**{b.get('onderwerp')}:** {b.get('bericht')}")
                        if b.get("antwoord"):
                            st.success(f"**🏛️ Academy Response:** {b.get('antwoord')}" if is_en else f"**🏛️ Reactie van de Academie-leiding:** {b.get('antwoord')}")
                        else:
                            st.caption("⏳ *Awaiting personal response from the Academy...*" if is_en else "⏳ *In afwachting van een persoonlijke reactie van de Academie-leiding...*")

is_vale = "Vale" in st.session_state.mentor_naam
titel_txt = ("Master / Mistress" if is_en else "Meester / Meesteres") if st.session_state.verbond_actief else (("Ma'am or Miss" if is_en else "Mevrouw of Miss") if is_vale else ("Sir or Mr" if is_en else "Meneer of Mr"))

    st.markdown("---")
    st.subheader("⭐ Leave a Public Review (Under Your Alias)" if is_en else "⭐ Plaats een Openbare Review (Onder je Schuilnaam)")
    st.write("Share your honest experience about The Sovereign Academy so newcomers know what to expect." if is_en else "Deel jouw eerlijke ervaring over The Sovereign Academy zodat nieuwe bezoekers weten wat ze kunnen verwachten.")
    rev_naam = st.text_input("Display alias:" if is_en else "Weergavenaam (schuilnaam):", value=st.session_state.schuilnaam or "Anoniem", key=f"{sleutel_prefix}_rev_naam")
    rev_sterren = st.slider("Rating (1 to 5 stars):" if is_en else "Waardering (1 t/m 5 sterren):", 1, 5, 5, key=f"{sleutel_prefix}_rev_str")
    rev_tekst = st.text_area("Your review:" if is_en else "Jouw review / ervaring:", height=100, key=f"{sleutel_prefix}_rev_txt")
    if st.button("🌟 Publish Public Review" if is_en else "🌟 Plaats Openbare Review", key=f"{sleutel_prefix}_rev_btn") and rev_tekst.strip():
        if sb:
            try:
                sb.table("reviews").insert({"tijdstip": datetime.now().isoformat(), "schuilnaam": rev_naam.strip() or "Anoniem", "rol": st.session_state.rol, "sterren": rev_sterren, "bericht": rev_tekst.strip(), "goedgekeurd": True}).execute()
                st.success("✅ Your review is now live on the home screen!" if is_en else "✅ Je review staat nu live op het startscherm!")
            except Exception:
                st.error("Could not save review." if is_en else "Review kon niet worden opgeslagen.")
    st.markdown("---")
    st.subheader("📋 Quick & In-Depth Evaluation (For the Maker)" if is_en else "📋 Snelle & Uitgebreide Evaluatie (Voor de Maker)")
    st.write("Click through in 30 seconds (100% anonymous) — your ratings help improve every part of the Academy." if is_en else "Klik er in 30 seconden doorheen (100% anoniem) — jouw antwoorden helpen om elk onderdeel van de Academie te verbeteren.")

    schaal = ("1 - Helemaal niet", "2 - Beetje", "3 - Neutraal", "4 - Ja, zeker", "5 - Absoluut ja") if not is_en else ("1 - Not at all", "2 - A little", "3 - Neutral", "4 - Yes, definitely", "5 - Absolutely yes")
    st.markdown("**1. Rate your experience on the platform:**" if is_en else "**1. Beoordeel jouw ervaring op het platform:**")
    s1 = st.select_slider("I felt safe and respected:" if is_en else "Ik voelde mij veilig en gerespecteerd:", options=schaal, value=schaal, key=f"{sleutel_prefix}_s1")
    s2 = st.select_slider("The platform feels warm and welcoming:" if is_en else "Het platform voelt warm en welkom aan:", options=schaal, value=schaal, key=f"{sleutel_prefix}_s2")
    s3 = st.select_slider("The design, colors, and calm layout appeal to me:" if is_en else "Het uiterlijk, de kleuren en rustige opmaak spreken mij aan:", options=schaal, value=schaal, key=f"{sleutel_prefix}_s3")
    s4 = st.select_slider("The menu and buttons are easy to use (mobile & PC):" if is_en else "Het menu en de knoppen zijn makkelijk te gebruiken (mobiel & PC):", options=schaal, value=schaal, key=f"{sleutel_prefix}_s4")
    s5 = st.select_slider("It was immediately clear how everything works:" if is_en else "Het was meteen duidelijk hoe alles werkt:", options=schaal, value=schaal, key=f"{sleutel_prefix}_s5")
    st.markdown("**2. Content, Exams & Mentors:**" if is_en else "**2. Inhoud, Toetsen & Mentoren:**")
    opt_th = ("Diepgaand en precies goed", "Goede basis, mag nóg uitgebreider", "Te veel tekst / te lang", "Anders, namelijk...") if not is_en else ("In-depth and just right", "Good basis, could be even deeper", "Too much text / too long", "Other, namely...")
    c_th = st.radio("Theory chapters:" if is_en else "Theorie-hoofdstukken:", opt_th, key=f"{sleutel_prefix}_cth")
    c_th_anders = st.text_input("Specify (theory):" if is_en else "Toelichting (theorie):", key=f"{sleutel_prefix}_ctha") if "Anders" in c_th or "Other" in c_th else ""

    opt_tb = ("Leerzaam en scherp", "Nuttig, mag nog uitdagender", "Te streng om door te gaan", "Anders, namelijk...") if not is_en else ("Educational and sharp", "Useful, could be more challenging", "Too strict to pass", "Other, namely...")
    c_tb = st.radio("Exams & 1-on-1 Tutoring:" if is_en else "Toetsen & 1-op-1 Bijles:", opt_tb, key=f"{sleutel_prefix}_ctb")
    c_tb_anders = st.text_input("Specify (exams/tutoring):" if is_en else "Toelichting (toetsen/bijles):", key=f"{sleutel_prefix}_ctba") if "Anders" in c_tb or "Other" in c_tb else ""

    opt_me = ("Fijne variatie en natuurlijke stijl", "Goed, maar ik mis nog bepaalde stijlen/types", "Schrijfstijl mag nog menselijker", "Anders, namelijk...") if not is_en else ("Great variety and natural style", "Good, though I miss certain styles/types", "Writing style could feel more human", "Other, namely...")
    c_me = st.radio("Mentor selection & style:" if is_en else "Keuze & stijl van de Mentoren:", opt_me, key=f"{sleutel_prefix}_cme")
    c_me_anders = st.text_input("Specify (mentors):" if is_en else "Toelichting (mentoren):", key=f"{sleutel_prefix}_cmea") if "Anders" in c_me or "Other" in c_me else ""

    q_topics = st.text_input("3. Any D/s topics or kinks you miss or want expanded? (optional)" if is_en else "3. Mis je nog bepaalde D/s-onderwerpen of verdieping? (optioneel)", key=f"{sleutel_prefix}_qtop")
    q_toekomst = st.multiselect("4. Future ideas you would love to see (multiple choices possible):" if is_en else "4. Toekomstige ideeën die je graag zou zien (meerdere keuzes mogelijk):", ("Vrijwillig anoniem Oefenpartner-Prikbord (na Module 1)", "Meer verschillende Mentoren / Meesters om uit te kiezen", "Verdiepingsmodules voor gevorderden (Rope, Protocol, Edgeplay)", "Interactieve opdrachten-generator voor koppels", "Niets veranderen, houd het precies zo") if not is_en else ("Voluntary anonymous Practice Partner Board (after Module 1)", "More Mentors / Masters to choose from", "Advanced modules (Rope, Protocol, Edgeplay)", "Interactive task generator for couples", "Change nothing, keep it as is"), key=f"{sleutel_prefix}_qtoek")
    q_cijfer = st.slider("5. Overall Score (1 to 10):" if is_en else "5. Totaalcijfer (1 t/m 10):", 1, 10, 8, key=f"{sleutel_prefix}_qcij")
    q_vrij = st.text_area("6. Your own creative ideas or tips for the maker (optional):" if is_en else "6. Jouw eigen ideeën of tips voor de maker (optioneel):", height=100, key=f"{sleutel_prefix}_qvrij")

    if st.button("📊 Submit Evaluation" if is_en else "📊 Verstuur Evaluatie", key=f"{sleutel_prefix}_eq_btn"):
        if sb:
            try:
                sb.table("enquete").insert({
                    "tijdstip": datetime.now().isoformat(),
                    "rol": st.session_state.rol,
                    "sfeer_veilig": s1,
                    "sfeer_welkom": s2,
                    "site_uiterlijk": s3,
                    "site_menu_gemak": s4,
                    "site_begrijpelijk": s5,
                    "theorie_oordeel": f"{c_th} ({c_th_anders})" if c_th_anders else c_th,
                    "toets_bijles_oordeel": f"{c_tb} ({c_tb_anders})" if c_tb_anders else c_tb,
                    "mentoren_oordeel": f"{c_me} ({c_me_anders})" if c_me_anders else c_me,
                    "gemiste_topics": q_topics.strip(),
                    "toekomst_ideeen": " | ".join(q_toekomst),
                    "cijfer": q_cijfer,
                    "vrije_input": q_vrij.strip()
                }).execute()
                st.success("✅ Thank you! Your ratings have been saved for the maker." if is_en else "✅ Dankjewel! Jouw beoordeling is opgeslagen voor de maker.")
            except Exception:
                st.error("Could not save evaluation." if is_en else "Evaluatie kon niet worden opgeslagen.")

with st.sidebar:
    try:
        st.image(st.session_state.mentor_foto, width=120)
    except Exception:
        st.write("👑" if st.session_state.verbond_actief else "✨")
    st.header("📊 Academy Dossier")
    if st.session_state.schuilnaam:
        st.success(f"🔑 **{st.session_state.schuilnaam}**")
    if st.session_state.partner_naam:
        st.info(f"💞 **Partner:** {st.session_state.partner_naam}")
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
    st.session_state.safewoord = st.text_input("🚨 Safeword:" if is_en else "🚨 Afgesproken Safewoord:", value=st.session_state.safewoord, max_chars=20)
    if st.button(("🏛️ Meet Staff & Masters" if is_en else "🏛️ Kennismaking Staf & Meesters") if not st.session_state.gids_open else ("🔙 Back to Academy" if is_en else "🔙 Terug naar de Academie")):
        st.session_state.gids_open = not st.session_state.gids_open
        st.session_state.steun_open = False
        st.session_state.zorgmodus = False
        st.rerun()
    if st.button(("🛍️ Recommended & Support" if is_en else "🛍️ Aanbevolen & Steun") if not st.session_state.steun_open else ("🔙 Back to Academy" if is_en else "🔙 Terug naar de Academie")):
        st.session_state.steun_open = not st.session_state.steun_open
        st.session_state.gids_open = False
        st.session_state.zorgmodus = False
        st.rerun()
    if st.button(("🆘 Care Mode (Help/Rest)" if is_en else "🆘 Zorgmodus (Direct hulp/rust)") if not st.session_state.zorgmodus else ("✅ Close Care Mode" if is_en else "✅ Zorgmodus sluiten")):
        st.session_state.zorgmodus = not st.session_state.zorgmodus
        st.session_state.gids_open = False
        st.session_state.steun_open = False
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
    mentor, mentor_img = st.session_state.mentor_naam, st.session_state.mentor_foto
    st.warning("🆘 **24/7 Care Mode Active:** You are completely safe. Breathe calmly. Your mentor stands beside you outside of any role." if is_en else "🆘 **24/7 Zorgmodus Actief:** Je bent helemaal veilig. Adem rustig in en uit. Jouw begeleider staat nu buiten elke rol naast je.")
    if "zorg_chat" not in st.session_state:
        st.session_state.zorg_chat = [("assistant", f"*{mentor} sits beside you calmly, completely out of any role.* Take a deep breath. There are no rules, no expectations, and no pressure right now. Tell me what you are feeling, or just rest here." if is_en else f"*{mentor} komt rustig naast je zitten, volledig buiten elke rol.* Haal eerst maar eens rustig adem. Er zijn nu geen regels, geen verwachtingen en geen druk. Vertel maar wat je voelt, of blijf gewoon even rustig hier.")]
    u_av_z = st.session_state.user_avatar if isinstance(st.session_state.user_avatar, str) and len(st.session_state.user_avatar) <= 4 else "👤"
    for role, text in st.session_state.zorg_chat:
        with st.chat_message(role, avatar=(mentor_img if role == "assistant" else u_av_z)):
            st.write(text)
    if zorg_input := st.chat_input("Share what you feel (100% safe, out of role)..." if is_en else "Vertel rustig wat je voelt (100% veilig, buiten elke rol)..."):
        st.session_state.zorg_chat.append(("user", zorg_input))
        if sb:
            try:
                thema = vraag_mentor(f"Classify the main emotional struggle in this message into ONE short Dutch label (e.g. Subdrop, Domdrop, Grenzen / Overweldigd, Onzekerheid, Schuldgevoel, Relatie / Communicatie). Output ONLY the label, no personal details:\n\n{zorg_input}").strip()[:40]
                sb.table("zorg_analyse").insert({"tijdstip": datetime.now().isoformat(), "rol": st.session_state.rol, "thema": thema}).execute()
            except Exception:
                pass
        taal_instr = "in English" if is_en else "in Dutch"
        zorg_prompt = f"Respond {taal_instr} as {mentor} of The Sovereign Academy. Always address the student with 'je'/'jij' (NEVER 'u' or 'kind') and write naturally in complete sentences. CRITICAL: 24/7 Care Mode is active. Drop ALL strictness, dominance, or roleplay completely. Be warm, grounding, gentle, and reassuring. Help the user breathe, feel safe, and process any subdrop, domdrop, or overwhelm."
        gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.zorg_chat)
        antwoord = vraag_mentor(f"{zorg_prompt}\n\nHistory:\n{gesprek}\n\nResponse:")
        st.session_state.zorg_chat.append(("assistant", antwoord))
        st.rerun()
    st.stop()

if st.session_state.gids_open:
    st.subheader("Meet the Staff, Masters & Mistresses" if is_en else "Kennismaking: Staf, Meesters & Meesteressen")
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
    st.subheader("Welcome to The Sovereign Academy" if is_en else "Welkom bij The Sovereign Academy")
    with st.container(border=True):
        st.markdown("**What is The Sovereign Academy?**\nA safe, non-judgmental learning environment for conscious submission (Submissive) and responsible leadership (Dominant). Train privately with an AI Mentor, and once you complete **Module 1 (Safety & Consent)**, you can link your anonymous alias 1-on-1 with a real D/s partner inside the app to practice long-distance D/s safely — without ever sharing your phone number or email. 100% free and anonymous." if is_en else "**Wat is The Sovereign Academy?**\nEen veilige, oordeelvrije leeromgeving voor bewuste overgave (Submissive) én verantwoord leiderschap (Dominant). Oefen privé met een AI-Mentor, en zodra je **Module 1 (Veiligheid & Consent)** hebt afgerond, kun je jouw anonieme schuilnaam 1-op-1 koppelen aan een echte D/s-partner binnen de app om veilig op afstand te oefenen — zonder ooit je telefoonnummer of e-mailadres te delen. 100% gratis en anoniem.")
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
                                for k in ("schuilnaam", "pincode", "rol", "mentor_naam", "mentor_foto", "module_nr", "sub_type", "grenzen", "notities", "chat_history", "verbond_actief", "meester_stijl", "laatste_les_tijd", "partner_naam", "safewoord"):
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
        with st.expander("📱 Tip: Save The Sovereign Academy as a discreet app on your phone or PC" if is_en else "📱 Tip: Zet The Sovereign Academy als discrete app op je telefoon of PC"):
            st.markdown("""
* **iPhone (Safari):** Open deze link in Safari → tik onderaan op het **Deel-icoon** (vierkantje met pijltje omhoog) → kies **Zet op beginscherm** → geef het eventueel een korte, discrete naam (bijv. *SA* of *Academy*).
* **Android (Chrome):** Tik rechtsboven op de **drie puntjes (`⋮`)** → kies **Installeren en snelkoppeling maken** → **Snelle link maken** → geef het een discrete naam en tik op **Toevoegen**.
* **Windows PC (Chrome / Edge):** Klik rechtsboven op de **drie puntjes (`⋮`)** → **Casten, opslaan en delen** → **Snelkoppeling maken...** → vink **Openen als venster** aan.
            """ if not is_en else """
* **iPhone (Safari):** Open this link in Safari → tap the **Share icon** at the bottom → select **Add to Home Screen** → give it a short, discreet name (e.g. *SA* or *Academy*).
* **Android (Chrome):** Tap the **three dots (`⋮`)** at the top right → select **Install and create shortcut** → **Create quick link** → give it a discreet name and tap **Add**.
* **Windows PC (Chrome / Edge):** Click the **three dots (`⋮`)** at the top right → **Cast, save, and share** → **Create shortcut...** → check **Open as window**.
            """)

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

    with st.expander("View all Masters & Mistresses of the Academy (Phase 3)" if is_en else "Bekijk alle Meesters & Meesteressen van de Academie (Fase 3)"):
        for (geslacht, profiel), m_info in MEESTERS.items():
            st.markdown(f"**{m_info.get('naam')}** (*{profiel}*): {t(m_info.get('stijl'))}")

    st.subheader("🚪 Start your journey" if is_en else "🚪 Start jouw traject")
    avatar_optie = st.radio("Choose your profile icon in chat:" if is_en else "Kies jouw eigen profiel-icoon in de chat:", ("👤 Neutral", "👩 Woman", "👨 Man") if is_en else ("👤 Neutraal", "👩 Vrouw", "👨 Man"), horizontal=True)
    st.session_state.user_avatar = avatar_optie.split()
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

    if sb:
        st.markdown("---")
        st.subheader("⭐ Experiences & Reviews from Students" if is_en else "⭐ Ervaringen & Reviews van Studenten")
        try:
            revs = sb.table("reviews").select("*").eq("goedgekeurd", True).order("id", desc=True).limit(10).execute().data
        except Exception:
            revs = []
        if not revs:
            st.caption("No public reviews yet — be the first to share your experience in the Support & Feedback menu!" if is_en else "Nog geen openbare reviews — deel als eerste jouw ervaring via het menu 'Aanbevolen & Steun'!")
        else:
            for r in revs:
                with st.container(border=True):
                    sterren_str = "⭐" * int(r.get("sterren", 5))
                    st.markdown(f"**{r.get('schuilnaam', 'Anoniem')}** (*{r.get('rol', '')}*) — {sterren_str}")
                    st.write(r.get("bericht"))

elif st.session_state.fase == "Les":
    nr = max(1, st.session_state.module_nr)
    is_dom = st.session_state.rol == "Dominant"
    ruw_mod = DOM_MODULES.get(nr) if is_dom else MODULES.get(nr)
    mod = vertaal_module(ruw_mod) if is_en else ruw_mod
    mentor, mentor_img = st.session_state.mentor_naam, st.session_state.mentor_foto
    st.subheader(f"{'🎓' if is_dom else '📚'} {mod.get('titel')}")

    hoofdstukken = [h.strip() for h in mod.get("theorie", "").split("### ") if h.strip()]
    alle_gelezen = True
    for idx, h in enumerate(hoofdstukken):
        regels_h = h.splitlines()
        h_titel = regels_h[0].strip()
        h_inhoud = "\n".join(regels_h[1:]).strip()
        with st.expander(f"📖 {h_titel}", expanded=(idx == 0 and not st.session_state.get("bijles_actief", False))):
            st.markdown(h_inhoud)
            gelezen = st.checkbox("✅ Ik heb dit hoofdstuk aandachtig gelezen en begrepen." if not is_en else "✅ I have read and understood this chapter carefully.", key=f"chk_read_{nr}_{idx}_{st.session_state.rol}")
            if not gelezen:
                alle_gelezen = False

    if not alle_gelezen:
        st.info("🔒 Lees alle hoofdstukken hierboven en vink ze aan om de toets te ontgrendelen." if not is_en else "🔒 Read all chapters above and check them off to unlock the exam.")
    elif st.session_state.get("bijles_actief", False):
        st.warning(f"🎓 **{'Mandatory Tutoring Session with' if is_en else 'Verplichte Bijles-sessie met'} {mentor}** — {'Discuss your mistakes below until your mentor unlocks your retake.' if is_en else 'Bespreek hieronder je fouten totdat jouw begeleider je herkansing vrijgeeft.'}")
        u_av = st.session_state.user_avatar if isinstance(st.session_state.user_avatar, str) and len(st.session_state.user_avatar) <= 4 else "👤"
        for role, text in st.session_state.get("bijles_chat", []):
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else u_av)):
                st.write(text)
        if bijles_in := st.chat_input("Answer your mentor's question or ask for clarification..." if is_en else "Beantwoord de vraag van je begeleider of vraag om extra uitleg..."):
            st.session_state.bijles_chat.append(("user", bijles_in))
            taal_instr = "in English" if is_en else "in Dutch"
            f_lijst = st.session_state.get("laatste_fouten", [])
            bijles_prompt = f"Respond {taal_instr} as {mentor} of The Sovereign Academy. Always address the student with 'je'/'jij' (NEVER 'u' or 'kind'), write naturally in complete sentences, and never repeat cliché props like a fountain pen. You are giving 1-on-1 tutoring because the student failed Module {nr} on: {f_lijst}. Ask a focused follow-up question to check if they truly understand why their answer was wrong, or give deeper explanation if they ask. CRITICAL: Only when you are convinced they now understand the concepts AND they are ready to retake the exam, end your message with the exact tag [HERKANSING_VRIJ] and ask if they want to discuss anything else or start the retake."
            gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.bijles_chat)
            antwoord = vraag_mentor(f"{bijles_prompt}\n\nHistory:\n{gesprek}\n\nResponse:")
            if "[HERKANSING_VRIJ]" in antwoord:
                antwoord = antwoord.replace("[HERKANSING_VRIJ]", "").strip()
                st.session_state.herkansing_klaar = True
            st.session_state.bijles_chat.append(("assistant", antwoord))
            st.rerun()
        if st.session_state.get("herkansing_klaar", False):
            if st.button("🔄 Start Exam Retake" if is_en else "🔄 Start Herkansing van de Toets"):
                st.session_state.bijles_actief = False
                st.session_state.herkansing_klaar = False
                st.session_state.bijles_chat = []
                st.session_state.poging += 1
                st.rerun()
    else:
        st.markdown("---")
        poging_nr = st.session_state.poging
        poging_txt = (f" (Retake {poging_nr})" if is_en else f" (Herkansing {poging_nr})") if poging_nr > 0 else ""
        st.subheader(("📝 Module Exam" if is_en else "📝 Module-toets") + poging_txt)
        vragen = mod.get("vragen")
        antw = []
        for i, q in enumerate(vragen):
            opties = list(q.get("o"))
            random.Random(f"hussel_{nr}_{i}_{st.session_state.poging}_{st.session_state.rol}").shuffle(opties)
            antw.append(st.radio(q.get("v"), opties, key=f"q_{nr}_{i}_{st.session_state.poging}") == q.get("a"))
        if st.button("Submit Exam" if is_en else "Lever toets in"):
            score = sum(antw)
            geslaagd = score >= 8
            foute_vragen = [q.get("v") for q, goed in zip(vragen, antw) if not goed]
            if sb:
                try:
                    sb.table("toets_analyse").insert({"tijdstip": datetime.now().isoformat(), "rol": st.session_state.rol, "module_nr": nr, "score": score, "geslaagd": geslaagd, "foute_vragen": " | ".join(foute_vragen)}).execute()
                except Exception:
                    pass
            if geslaagd:
                p_nr = st.session_state.poging
                st.session_state.poging = 0
                st.session_state.laatste_les_tijd = datetime.now().isoformat()
                st.session_state.fase = "Praktijkkamer"
                if not st.session_state.chat_history:
                    if is_en:
                        h_en = f" after retake {p_nr}" if p_nr > 0 else ""
                        intro = f"*{mentor} nods approvingly ({score}/10{h_en}).* Your perseverance paid off. Discuss your insights from Module {nr} here." if is_dom else f"*{mentor} closes your dossier ({score}/10{h_en}).* Good — you worked through your mistakes and proved you understand the material. Address me as '{titel_txt}'. Tell me: what are you looking for here?"
                    else:
                        h_nl = f" na herkansing {p_nr}" if p_nr > 0 else ""
                        intro = f"*{mentor} knikt goedkeurend ({score}/10{h_nl}).* Je doorzettingsvermogen loont. Bespreek hier je inzichten uit Module {nr}." if is_dom else f"*{mentor} slaat je dossier dicht ({score}/10{h_nl}).* Goed — je hebt je fouten uitgewerkt en bewezen dat je de stof beheerst. Spreek mij aan als '{titel_txt}'. Vertel mij: wat zoek je hier?"
                    st.session_state.chat_history.append(("assistant", intro))
                elif p_nr > 0:
                    st.session_state.chat_history.append(("assistant", f"*{mentor} nods approvingly.* You passed Module {nr} ({score}/10) after retake {p_nr}. Let us reflect on what made the difference for you." if is_en else f"*{mentor} knikt goedkeurend.* Je hebt Module {nr} behaald ({score}/10) na herkansing {p_nr}. Laten we bespreken wat voor jou het kwartje deed vallen."))
                sla_op()
                st.rerun()
            else:
                st.session_state.laatste_fouten = foute_vragen
                st.session_state.bijles_actief = True
                st.session_state.herkansing_klaar = False
                start_bijles = vraag_mentor(f"You are {mentor} of The Sovereign Academy. Always address the student with 'je'/'jij' (NEVER 'u' or 'kind') and write naturally in complete sentences. The student just scored {score}/10 on Module {nr} and missed these questions: {foute_vragen}. Step in directly {'in English' if is_en else 'in Dutch'}, point out where they went wrong without immediately giving away all answers, and ask a sharp, constructive question to make sure they truly understand the theory.")
                st.session_state.bijles_chat = [("assistant", start_bijles)]
                st.rerun()

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
            extra_en = ", Care Mode, and your notebook" if st.session_state.notitieboek_actief else " and Care Mode"
            extra_nl = ", Zorgmodus en je notitieboekje" if st.session_state.notitieboek_actief else " en Zorgmodus"
            st.info(f"⏳ **Reflection pause active:** Let the material settle first. The next module opens in about **{uren_over} hours** (the chat{extra_en} remain available 24/7)." if is_en else f"⏳ **Bezinkingspauze actief:** Laat de lesstof eerst rustig landen. Over ongeveer **{uren_over} uur** opent de volgende module (de chat{extra_nl} blijven 24/7 bereikbaar).")

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

    t_chat = "💬 Mentor"
    t_koppel = "💞 1-op-1 D/s-Chat"
    t_disc = "⏱️ Discipline"
    t_shop = "🛍️ Steun" if not is_en else "🛍️ Support"
    t_note = "📓 Notitieboek" if not is_en else "📓 Notebook"
    t_lim = "🔒 Grenzen" if not is_en else "🔒 Limits"

    tab_namen = [t_chat, t_koppel, t_disc, t_shop]
    if st.session_state.notitieboek_actief:
        tab_namen.insert(1, t_note)
    if st.session_state.grenzenlijst_actief:
        tab_namen.insert(1, t_lim)
    tabs = st.tabs(tab_namen)

    with next(iter(tabs)):
        u_av = st.session_state.user_avatar if isinstance(st.session_state.user_avatar, str) and len(st.session_state.user_avatar) <= 4 else "👤"
        for role, text in st.session_state.chat_history:
            with st.chat_message(role, avatar=(mentor_img if role == "assistant" else u_av)):
                st.write(text)
        if user_input := st.chat_input("Type your response..." if is_en else "Typ je reactie..."):
            if st.session_state.chat_history and st.session_state.chat_history[-1] == ("user", user_input):
                st.rerun()
            st.session_state.chat_history.append(("user", user_input))
            woorden = [w.strip(".,!?\"'") for w in user_input.upper().split()]
            actief_sw = st.session_state.get("safewoord", "ROOD").upper().strip()
            if any(sw in woorden for sw in ("ROOD", "RED", actief_sw) if sw):
                st.session_state.chat_history.append(("assistant", f"*{mentor} stops immediately.* Easy now, breathe. You are completely safe." if is_en else f"*{mentor} stopt direct.* Rustig maar, haal adem. Je bent helemaal veilig."))
                sla_op()
                st.rerun()
            zorg_txt = "CRITICAL: Student activated 24/7 Care Mode. Drop all strictness, offer immediate warmth, grounding, and emotional safety." if st.session_state.zorgmodus else ""
            taal_instr = "in English" if is_en else "in Dutch"
            stijl_regels = (
                "CRITICAL STYLE & QUALITY RULES: "
                "1. Always address the student informally with 'je' and 'jij' (NEVER use 'u' or 'uw'). "
                "2. NEVER use the word 'kind' (child) to address the student. "
                "3. Write organically, naturally, and varied — NEVER repeat cliché stage directions like picking up/putting down a fountain pen ('vulpen'), looking out the window ('uit het raam kijken'), walking to a bookcase ('boekenkast'), or pointing to the door. Keep physical descriptions minimal, fresh, and grounded. "
                "4. ALWAYS finish every single sentence and thought completely; never cut off mid-sentence or skip words. "
                "5. NEVER mention or promote the 'Aanbevolen & Steun' / shop section."
            )
            regels = f"Respond {taal_instr} as {mentor} of The Sovereign Academy. {stijl_regels} {zorg_txt} Current progress: Module {st.session_state.module_nr} completed. Profile: {st.session_state.sub_type}, Safeword: {st.session_state.get('safewoord', 'ROOD')}, Limits: {st.session_state.grenzen}, Previous exam struggle areas: {st.session_state.get('laatste_fouten', [])}. Triggers (use only when appropriate): [OPEN_NOTITIEBOEK], [OPEN_GRENZENLIJST], [SAFEWOORD:woord], [PROFIEL:Brat], [PROFIEL:Classic Submissive], [PROFIEL:Slave / Slavin], [PROFIEL:Daddy / Little], [PROFIEL:Petplay], [PROFIEL:Switch]."
            gesprek = "\n".join(f"{r}: {b}" for r, b in st.session_state.chat_history[-16:])
            antwoord = vraag_mentor(f"{regels}\n\nHistory:\n{gesprek}\n\nResponse:")
            if "[SAFEWOORD:" in antwoord:
                delen = antwoord.split("[SAFEWOORD:", 1)
                nieuw_sw = delen[1].split("]", 1)[0].strip()
                if nieuw_sw:
                    st.session_state.safewoord = nieuw_sw
                antwoord = (delen[0] + delen[1].split("]", 1)[-1]).strip()
            for trig, state_k in (("[OPEN_NOTITIEBOEK]", "notitieboek_actief"), ("[OPEN_GRENZENLIJST]", "grenzenlijst_actief")):
                if trig in antwoord:
                    antwoord = antwoord.replace(trig, "").strip()
                    st.session_state[state_k] = True
            for p_naam in ("Brat", "Classic Submissive", "Slave / Slavin", "Daddy / Little", "Petplay", "Switch"):
                if f"[PROFIEL:{p_naam}]" in antwoord:
                    antwoord = antwoord.replace(f"[PROFIEL:{p_naam}]", "").strip()
                    st.session_state.sub_type = p_naam
            st.session_state.chat_history.append(("assistant", antwoord))
            sla_op()
            st.rerun()

    with tabs[tab_namen.index(t_koppel)]:
        st.subheader("💞 Anonymous 1-on-1 D/s Partner Chat" if is_en else "💞 Anonieme 1-op-1 D/s-Koppelchat")
        st.caption("Connect with a fellow Academy student (Dominant or Submissive) using only your alias — no phone number or email required." if is_en else "Koppel jouw dossier aan een andere Academie-student (Dominant of Submissive) op basis van alleen jullie schuilnaam — zonder telefoonnummer of e-mailadres.")
        with st.expander("ℹ️ How does the anonymous 1-on-1 Partner Chat work?" if is_en else "ℹ️ Hoe werkt de anonieme 1-op-1 Koppelchat?"):
            st.markdown("""
1. **Create an anonymous Dossier:** Both you and your partner choose your own alias + 4-digit PIN on the home screen (no email or phone number needed).
2. **Share only your Academy alias:** Give each other only your chosen Academy alias (for example via Reddit, FetLife, or wherever you met).
3. **Link 1-on-1:** Enter your partner's alias below and click **Link Partner**. Once both of you have entered each other's alias, your private chat room opens here.
4. **100% Safe & Voluntary:** You can unlink or type **RED** at any moment to stop immediately.
            """ if is_en else """
1. **Maak een anoniem Dossier aan:** Kies allebei op het startscherm een eigen schuilnaam + 4-cijferige pincode (zonder e-mailadres of telefoonnummer).
2. **Deel alleen je schuilnaam:** Geef elkaar alleen jullie gekozen schuilnaam in de Academie (bijvoorbeeld via Reddit, FetLife of waar jullie elkaar hebben leren kennen).
3. **Koppel 1-op-1:** Vul hieronder de schuilnaam van je partner in en klik op **Koppel Partner**. Zodra jullie allebei elkaars schuilnaam hebben ingevuld, opent hier jullie afgeschermde privékamer.
4. **100% Veilig & Vrijwillig:** Je kunt op elk moment weer ontkoppelen of **ROOD** typen om direct te stoppen.
            """)
        if not st.session_state.schuilnaam:
            st.info("🔑 Create or open an anonymous Dossier on the home screen first to use the 1-on-1 Partner Chat." if is_en else "🔑 Maak op het startscherm eerst een anonieme Dossiercode (schuilnaam + pincode) aan om de 1-op-1 Koppelchat te gebruiken.")
        elif not sb:
            st.warning("Database connection required for 1-on-1 Partner Chat." if is_en else "Databaseverbinding nodig voor de 1-op-1 Koppelchat.")
        else:
            p_in = st.text_input("Partner's Academy Alias:" if is_en else "Schuilnaam van jouw D/s-partner in de Academie:", value=st.session_state.partner_naam)
            c_k1, c_k2 = st.columns(2)
            if c_k1.button("🔗 Link Partner" if is_en else "🔗 Koppel Partner") and p_in.strip():
                if p_in.strip().lower() == st.session_state.schuilnaam.strip().lower():
                    st.error("You cannot link to your own alias." if is_en else "Je kunt niet aan je eigen schuilnaam koppelen.")
                else:
                    st.session_state.partner_naam = p_in.strip()
                    sla_op()
                    st.rerun()
            if st.session_state.partner_naam and c_k2.button("🔓 Unlink" if is_en else "🔓 Ontkoppel"):
                st.session_state.partner_naam = ""
                sla_op()
                st.rerun()

            if st.session_state.partner_naam:
                mijn_naam = st.session_state.schuilnaam.strip()
                partner_naam = st.session_state.partner_naam.strip()
                st.success(f"🔒 **Private room active:** **{mijn_naam}** ↔ **{partner_naam}**" if is_en else f"🔒 **Privékamer actief:** **{mijn_naam}** ↔ **{partner_naam}**")
                if st.button("🔄 Refresh messages" if is_en else "🔄 Ververs berichten"):
                    st.rerun()
                kamer = "_".join(sorted([mijn_naam.lower(), partner_naam.lower()]))
                try:
                    k_berichten = sb.table("koppel_chat").select("*").eq("kamer_code", kamer).order("id").execute().data
                except Exception:
                    k_berichten = []
                if not k_berichten:
                    st.info("No messages yet. Say hello to your partner below!" if is_en else "Nog geen berichten. Stuur hieronder je eerste bericht naar je partner!")
                for kb in k_berichten[-30:]:
                    is_ik = kb.get("afzender", "").lower() == mijn_naam.lower()
                    with st.chat_message("user" if is_ik else "assistant", avatar="👤" if is_ik else "👑"):
                        st.markdown(f"**{kb.get('afzender')}:** {kb.get('bericht')}")
                k_nieuw = st.text_input("Message to your partner (type ROOD / RED to stop):" if is_en else "Bericht aan je partner (typ ROOD om direct te stoppen):", key="koppel_msg_in")
                if st.button("📩 Send to partner" if is_en else "📩 Verstuur naar partner") and k_nieuw.strip():
                    try:
                        sb.table("koppel_chat").insert({"tijdstip": datetime.now().isoformat(), "kamer_code": kamer, "afzender": mijn_naam, "bericht": k_nieuw.strip()}).execute()
                    except Exception:
                        st.error("Could not send message. Check if the 'koppel_chat' table exists in Supabase." if is_en else "Bericht kon niet worden verzonden. Controleer of de tabel 'koppel_chat' in Supabase is aangemaakt.")
                    st.rerun()

    if st.session_state.notitieboek_actief:
        with tabs[tab_namen.index(t_note)]:
            notitie_tekst = st.text_area("Note / Check-in:" if is_en else "Notitie / Check-in:", height=120)
            if st.button("Submit" if is_en else "Indienen") and notitie_tekst.strip():
                reactie = vraag_mentor(f"You are {mentor}. Address the student with 'je'/'jij' (NEVER 'u' or 'kind') and respond naturally without repeating props like a fountain pen {'in English' if is_en else 'in Dutch'} to: \"{notitie_tekst}\"")
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
