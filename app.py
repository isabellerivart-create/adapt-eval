import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from io import BytesIO
import PyPDF2
import re

st.set_page_config(page_title="Adapt'Éval Wallonie Pro", layout="wide", page_icon="🇧🇪")

# Dictionnaire de simplification FALC
DICT_FALC = {
    "indique": "DIS", "souligne": "FAIS UN TRAIT SOUS", "entoure": "FAIS UN ROND AUTOUR DE",
    "conjugue": "ÉCRIS LE VERBE", "identifie": "TROUVE", "illustre": "FAIS UN DESSIN",
    "complète": "ÉCRIS CE QUI MANQUE", "réécris": "ÉCRIS ENCORE", "reproduis": "REFAIS"
}

st.title("🎓 Adapt'Éval - Expert Inclusion & Dys")

with st.sidebar:
    st.header("👤 Profil de l'élève")
    profils = st.multiselect("Besoins spécifiques", ["Dyslexie", "Dysorthographie", "Dyspraxie", "TSA", "TDA/H"], default=["Dyslexie"])
    st.divider()
    st.header("🚂 Contextualisation")
    passion = st.text_input("Passion (ex: les trains)", "")
    st.header("📏 Réglages")
    interligne = st.slider("Espacement (Interligne)", 1.5, 3.0, 2.0)

col_in, col_out = st.columns(2)

with col_in:
    file = st.file_uploader("Importer l'évaluation (PDF ou DOCX)", type=["pdf", "docx"])
    texte_source = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            texte_source = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            doc = Document(file)
            texte_source = "\n".join([p.text for p in doc.paragraphs])
    txt_input = st.text_area("Texte brut détecté (à modifier si besoin) :", value=texte_source, height=400)

def nettoyer_et_adapter(ligne, passion):
    if not ligne.strip() or len(ligne.strip()) < 2: return None
    t = ligne.strip()
    
    # 1. Correction Majuscule début de phrase
    t = t[0].upper() + t[1:]
    
    # 2. Contextualisation Passion (Trains, etc.)
    if passion:
        subst = {"maman": f"le conducteur du {passion}", "papa": "le mécanicien", "le bus": "le wagon", "la voiture": "la locomotive"}
        for k, v in subst.items():
            if k in t.lower(): t = re.sub(k, v.upper(), t, flags=re.IGNORECASE)

    # 3. Simplification FALC (Consignes)
    for k, v in DICT_FALC.items():
        if k in t.lower():
            t = re.sub(k, f"**{v}**", t, flags=re.IGNORECASE)
    
    return t

with col_out:
    if st.button("🚀 GÉNÉRER LE DOCUMENT ADAPTÉ"):
        if txt_input:
            doc = Document()
            # Marges larges pour éviter la surcharge
            for section in doc.sections:
                section.top_margin = Cm(2)
                section.bottom_margin = Cm(2)
                section.left_margin = Cm(2.5)
                section.right_margin = Cm(2.5)

            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(14)

            lignes = txt_input.split('\n')
            for l in lignes:
                texte_pret = nettoyer_et_adapter(l, passion)
                if not texte_pret: continue
                
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = interligne
                p.paragraph_format.space_after = Pt(24) # GROS ESPACE ENTRE CHAQUE LIGNE
                
                # Gestion du gras/couleur pour les consignes
                parts = texte_pret.split("**")
                for i, part in enumerate(parts):
                    run = p.add_run(part)
                    if i % 2 != 0: # C'est une consigne FALC
                        run.bold = True
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(0, 102, 204) # Bleu pédagogique
                
                st.markdown(texte_pret.replace("**", "")) # Aperçu écran

            buf = BytesIO()
            doc.save(buf)
            st.success("Document ultra-aéré généré !")
            st.download_button("📥 Télécharger l'évaluation (.docx)", data=buf.getvalue(), file_name="EVAL_ADAPTEE_DYS.docx")
