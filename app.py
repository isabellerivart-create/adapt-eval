import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Adapt'Éval Wallonie Expert", layout="wide", page_icon="🇧🇪")

# --- DICTIONNAIRE DE SIMPLIFICATION FALC ---
DICTIONNAIRE_FALC = {
    "indique": "dis",
    "souligne": "fais un trait sous",
    "entoure": "fais un rond autour de",
    "conjugue": "écris le verbe",
    "identifie": "trouve",
    "illustre": "fais un dessin",
    "complète": "écris ce qui manque",
    "effectue": "fais",
    "réécris": "écris encore",
    "reproduis": "refais la même chose"
}

# --- TITRE ET STYLE ---
st.title("🎓 Adapt'Éval - Inclusion Wallonie")
st.markdown("---")

# --- BARRE LATÉRALE (CONFIGURATION) ---
with st.sidebar:
    st.header("👤 Profil de l'élève")
    niveau = st.selectbox("Année d'étude", ["P1", "P2", "P3", "P4", "P5", "P6"])
    
    profils = st.multiselect("Aménagements TND", 
        ["TSA", "Dyslexie", "Dysorthographie", "Dyscalculie", "Dysphasie", "Dyspraxie", "TDA/H", "HPI", "Déficience Intellectuelle"])
    
    st.divider()
    st.header("🚂 Contextualisation")
    passion = st.text_input("Passion de l'élève (ex: les trains, les dinosaures)", "")
    st.info("L'outil remplacera les sujets génériques par des éléments liés à cette passion.")

# --- CORPS DE L'APPLICATION ---
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("📥 Évaluation Source")
    file = st.file_uploader("Importer le document (PDF ou DOCX)", type=["pdf", "docx"])
    
    texte_initial = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texte_initial += page.extract_text() + "\n"
        else:
            doc = Document(file)
            texte_initial = "\n".join([p.text for p in doc.paragraphs])
            
    txt_source = st.text_area("Vérifiez le texte ici :", value=texte_initial, height=400)

# --- MOTEUR D'ADAPTATION ---
def transformer_texte(texte, profils, passion):
    lignes = texte.split('\n')
    nouvelles_lignes = []
    
    for ligne in lignes:
        if not ligne.strip(): continue
        t = ligne
        
        # 1. CONTEXTUALISATION (Passion)
        if passion:
            # On remplace les noms communs par le thème de la passion
            dictionnaire_passion = {
                "maman": f"le conducteur du {passion}",
                "papa": f"le mécanicien du {passion}",
                "le bus": f"le wagon de {passion}",
                "la voiture": f"la locomotive",
                "les enfants": f"les voyageurs du {passion}",
                "la maison": f"la gare de {passion}",
                "le vélo": f"le petit train"
            }
            for ancien, nouveau in dictionnaire_passion.items():
                if ancien in
