import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from io import BytesIO
import PyPDF2
import re

st.set_page_config(page_title="Adapt'Éval Expert", layout="wide", page_icon="🇧🇪")

# Dictionnaire de reformulation pédagogique
REFORMULATION = {
    "indique": "DIS",
    "souligne": "FAIS UN TRAIT SOUS",
    "entoure": "FAIS UN ROND AUTOUR DE",
    "conjugue": "ÉCRIS LE VERBE",
    "identifie": "TROUVE",
    "complète": "ÉCRIS CE QUI MANQUE",
    "choisis": "PRENDS",
    "réécris": "ÉCRIS ENCORE",
    "quels sont": "TROUVE LES"
}

st.title("🎓 Adapt'Éval - Orthopédagogie & TND")

with st.sidebar:
    st.header("⚙️ Paramètres d'adaptation")
    profils = st.multiselect("Besoins", ["Dyslexie", "Dysorthographie", "TSA", "Dyspraxie"], default=["Dyslexie", "Dysorthographie"])
    
    st.divider()
    st.header("🎨 Couleurs Pédagogiques")
    c_consigne = st.color_picker("Couleur Verbes d'action", "#003366")
    c_notion = st.color_picker("Couleur Notions (Passé/Futur...)", "#CC0000")
    
    st.divider()
    passion = st.text_input("Passion (ex: les trains)", "")

col_in, col_out = st.columns(2)

with col_in:
    file = st.file_uploader("Fichier source (PDF/DOCX)", type=["pdf", "docx"])
    texte_brut = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            texte_brut = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            doc = Document(file)
            texte_brut = "\n".join([p.text for p in doc.paragraphs])
    txt_input = st.text_area("Texte détecté :", value=texte_brut, height=400)

def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def adapter_ligne(ligne, passion):
    t = ligne.strip()
    if not t: return None
    
    # 1. Majuscule forcée et nettoyage
    t = t[0].upper() + t[1:] if len(t) > 1 else t
    t = re.sub(r'\s+', ' ', t) # Supprime les espaces doubles

    # 2. Reformulation des consignes (FALC)
    for k, v in REFORMULATION.items():
        if k in t.lower():
            t = re.sub(k, f"**{v}**", t, flags=re.IGNORECASE)

    # 3. Passion / Contextualisation
    if passion:
        d_p = {"maman": f"le conducteur du {passion}", "papa": "le mécanicien", "le bus": "le wagon", "la voiture": "la locomotive", "les enfants": "les passagers"}
        for k, v in d_p.items():
            if k in t.lower(): t = re.sub(k, v.upper(), t, flags=re.IGNORECASE)
            
    return t

with col_out:
    if st.button("🚀 APPLIQUER L'ADAPTATION EXPERTE"):
        if txt_input:
            doc = Document()
            # Marges pour la Dyspraxie
            for s in doc.sections:
                s.left_margin = Cm(3)
                s.right_margin = Cm(2)

            lignes = txt_input.split('\n')
            for l in lignes:
                t_adapte = adapter_ligne(l, passion)
                if not t_adapte: continue
                
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 2.0
                p.paragraph_format.space_after = Pt(24)

                # Application des couleurs et du gras
                parts = t_adapte.split("**")
                for i, part in enumerate(parts):
                    run = p.add_run(part)
                    run.font.name = 'Arial'
                    run.font.size = Pt(14)
                    
                    if i % 2 != 0: # C'est une consigne reformulée
                        run.bold = True
                        run.font.size = Pt(16)
                        rgb = hex_to_rgb(c_consigne)
                        run.font.color.rgb = RGBColor(*rgb)
                    
                    # Mise en couleur des notions de temps
                    for notion in ["Passé", "Présent", "Futur
