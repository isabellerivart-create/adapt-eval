import streamlit as st
from docx import Document
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Adapt'Éval Expert", layout="wide", page_icon="🎓")

# --- DESIGN ERGONOMIQUE ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F4F8; }
    .main-card { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .stButton>button { 
        background-color: #6C63FF; color: white; border-radius: 8px; 
        font-weight: bold; border: none; height: 3em; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #5750D6; transform: translateY(-2px); }
    .rgpd-banner { padding: 10px; background-color: #FFE5E5; border: 1px solid #FFB2B2; border-radius: 8px; color: #D8000C; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

PICTOS = {"Lire": "📖", "Écrire": "✍️", "Calculer": "🧮", "Cocher": "☑️", "Relie": "↔️"}

# --- ENTÊTE ---
st.title("🎓 Adapt'Éval")
st.markdown('<div class="rgpd-banner">⚠️ RAPPEL RGPD : Ne saisissez JAMAIS le nom ou le prénom d\'un élève.</div>', unsafe_allow_html=True)

# --- NOTICE PÉDAGOGIQUE ---
with st.expander("📚 Guide des adaptations"):
    st.write("Sources : Tom Pousse, ATZEO, GACS, De Boeck.")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Configuration")
    niveau = st.selectbox("Année de l'élève", ["P1/CP", "P2/CE1", "P3/CE2", "P4/CM1", "P5/CM2", "P6/6ème"])
    matiere = st.selectbox("Matière", ["Français", "Mathématiques", "Éveil"])
    duree = st.slider("Durée prévue (min)", 5, 90, 45)
    st.divider()
    st.header("👤 Profil de l'élève")
    profils = st.multiselect("Profil(s) TND", ["TSA", "Dyslexie", "Dyscalculie", "TDAH", "Déficience Intellectuelle"])
    besoins_vocaux = st.text_area("Notes libres (ex: Police 16)")

# --- CORPS DE L'APPLICATION ---
col_in, col_out = st.columns([1, 1])

with col_in:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📥 Évaluation Originale")
    # ON DEFINIT LES VARIABLES ICI AVANT L'ADAPTATION
    competence = st.text_input("Compétence visée", value="Non précisée")
    objectif = st.text_input("Objectif spécifique", value="Non précisé")
    
    txt_source = st.text_area("Texte de l'évaluation :", height=300)
    
    st.write("Ajouter un pictogramme :")
    p_cols = st.columns(5)
    # On initialise le texte si vide pour éviter les erreurs
    if 'temp_txt' not in st.session_state: st.session_state.temp_txt = ""
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FONCTION D'ADAPTATION ---
def adapter(text, profils, matiere, duree, comp, obj):
    final = f"**COMPÉTENCE : {comp}**\n**OBJECTIF : {obj}**\n\n---\n"
    if duree > 45: final += "⚠️ *Note : Temps majoré ou contenu allégé.*\n\n"
    
    if "Dyscalculie" in profils and matiere != "Français":
        final += "| km | hm | dam | m | dm | cm | mm |\n|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n| | | | | | | |\n\n"
    
    temp_text = text
    if "Dyslexie" in profils:
        for v in ["Calcule", "Lis", "Entoure", "Relie", "Coche"]:
            temp_text = temp_text.replace(v, f"**{v.upper()}**")
    if "TSA" in profils:
        temp_text = "📍 DEBUT\n" + temp_text.replace("?", " ? (Réponse courte)\n───") + "\n🔚 FIN"
    return final + temp_text

# --- SORTIE ---
with col_out:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✨ Version Adaptée")
    
    if st.button("🚀 GÉNÉRER L'ADAPTATION"):
        if txt_source:
            # On passe les variables à la fonction
            res = adapter(txt_source, profils, matiere, duree, competence, objectif)
            if besoins_vocaux: res = f"🔔 NOTES : {besoins_vocaux}\n\n" + res
            
            final_edit = st.text_area("Éditeur final :", value=res, height=400)
            
            doc = Document()
            doc.add_paragraph(final_edit)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button("📥 Télécharger en .DOCX", data=buffer, file_name="eval_adaptee.docx")
        else:
            st.warning("Veuillez saisir un texte.")
    st.markdown('</div>', unsafe_allow_html=True)
