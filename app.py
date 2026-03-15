import streamlit as st
from docx import Document
from io import BytesIO
import PyPDF2 # Pour lire les PDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Adapt'Éval Wallonie Pro", layout="wide", page_icon="🇧🇪")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .main-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; }
    .stButton>button { background-color: #E11D48; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION POUR LIRE LES FICHIERS ---
def extraire_texte(upload):
    if upload.type == "application/pdf":
        reader = PyPDF2.PdfReader(upload)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif upload.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(upload)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Format non supporté pour l'extraction automatique. Copiez-collez le texte."

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇧🇪 Configuration")
    niveau = st.selectbox("Année", ["P1", "P2", "P3", "P4", "P5", "P6"])
    
    st.subheader("👤 Profils TND complets")
    # Liste exhaustive des TND
    choix_tnd = st.multiselect("Besoins spécifiques :", 
        ["TSA", "Dyslexie", "Dysorthographie", "Dyscalculie", "Dysphasie", "Dyspraxie", "TDA/H", "HPI"])

# --- CORPS ---
col_in, col_out = st.columns(2)

with col_in:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📥 Charger l'évaluation")
    
    # ZONE DE FICHIER
    uploaded_file = st.file_uploader("Ajoutez un PDF ou DOCX", type=["pdf", "docx"])
    
    contenu_initial = ""
    if uploaded_file:
        contenu_initial = extraire_texte(uploaded_file)
        st.success("Texte extrait avec succès !")

    txt_source = st.text_area("Texte à adapter (ou contenu extrait) :", value=contenu_initial, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIQUE D'ADAPTATION ---
def adapter_total(text, profils):
    res = text
    # Adaptation Dyspraxie : Aération maximale
    if "Dyspraxie" in profils:
        res = res.replace("\n", "\n\n")
    # Adaptation Dysphasie : Simplification syntaxique (mots complexes en gras)
    if "Dysphasie" in profils:
        res = "📢 *Consigne lue par l'adulte si nécessaire.*\n" + res
    # Adaptation TDA/H : Segmentation
    if "TDA/H" in profils:
        res = res.replace(".", ".\n✅ ---")
        
    return res

# --- SORTIE ---
with col_out:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✨ Version Adaptée")
    if st.button("LANCER L'ADAPTATION"):
        if txt_source:
            resultat = adapter_total(txt_source, choix_tnd)
            st.text_area("Résultat :", value=resultat, height=400)
            
            # Export Word
            new_doc = Document()
            new_doc.add_paragraph(resultat)
            b = BytesIO()
            new_doc.save(b)
            st.download_button("📥 Télécharger .docx", data=b.getvalue(), file_name="export.docx")
    st.markdown('</div>', unsafe_allow_html=True)
