import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from io import BytesIO
import PyPDF2
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="Adapt'Éval Inclusion Pro", layout="wide")

# Dictionnaire de reformulation (FALC / Dys)
REFORMULATION = {
    "indique": "DIS",
    "souligne": "FAIS UN TRAIT SOUS",
    "entoure": "FAIS UN ROND AUTOUR DE",
    "conjugue": "ÉCRIS LE VERBE",
    "identifie": "TROUVE",
    "complète": "ÉCRIS CE QUI MANQUE",
    "ajoute un connecteur": "CHOISIS UN MOT POUR LE TEMPS",
    "quel est l'infinitif": "DONNE LE NOM DU VERBE"
}

st.title("🎓 Adapt'Éval - Adaptation Pédagogique")

with st.sidebar:
    st.header("👤 Besoins de l'élève")
    profils = st.multiselect("Profils", ["Dyslexie", "Dysorthographie", "TSA", "Dyspraxie"], default=["Dyslexie", "Dysorthographie"])
    st.divider()
    st.header("🎨 Couleurs des mots-clés")
    c_verbes = st.color_picker("Couleur des consignes", "#003366")
    c_temps = st.color_picker("Couleur des indicateurs de temps", "#CC0000")
    st.divider()
    passion = st.text_input("Passion (ex: les trains)", "")

col_in, col_out = st.columns(2)

with col_in:
    file = st.file_uploader("Fichier source", type=["pdf", "docx"])
    texte_source = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            texte_source = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            doc = Document(file)
            texte_source = "\n".join([p.text for p in doc.paragraphs])
    txt_input = st.text_area("Texte original :", value=texte_source, height=400)

def adapter_pedagogique(ligne, passion):
    t = ligne.strip()
    if not t: return None
    
    # 1. Reformulation des consignes complexes
    for k, v in REFORMULATION.items():
        if k in t.lower():
            t = re.sub(k, f"**{v}**", t, flags=re.IGNORECASE)
            
    # 2. Contextualisation (Passion)
    if passion:
        remplacements = {"maman": f"le conducteur du {passion}", "papa": "le mécanicien", "le bus": "le wagon"}
        for k, v in remplacements.items():
            if k in t.lower(): t = re.sub(k, v.upper(), t, flags=re.IGNORECASE)
            
    # 3. Mise en majuscule forcée
    t = t[0].upper() + t[1:] if len(t) > 1 else t
    return t

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

with col_out:
    if st.button("🚀 APPLIQUER L'ADAPTATION PÉDAGOGIQUE"):
        if txt_input:
            doc = Document()
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(14)
            
            lignes = txt_input.split('\n')
            for l in lignes:
                t_pret = adapter_pedagogique(l, passion)
                if not t_pret: continue
                
                # Création du paragraphe
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 2.0 # DOUBLE INTERLIGNE
                p.paragraph_format.space_after = Pt(24)
                
                # Colorisation et mise en gras
                parts = t_pret.split("**")
                for i, part in enumerate(parts):
                    run = p.add_run(part)
                    if i % 2 != 0: # C'est un mot-clé reformulé
                        run.bold = True
                        run.font.size = Pt(16)
                        rgb = hex_to_rgb(c_verbes)
                        run.font.color.rgb = RGBColor(rgb[0], rgb[1], rgb[2])
                    
                    # Mise en couleur automatique des temps (Passé, Présent, Futur)
                    for temps in ["Passé", "Présent", "Futur"]:
                        if temps.lower() in part.lower():
                            rgb_t = hex_to_rgb(c_temps)
                            run.font.color.rgb = RGBColor(rgb_t[0], rgb_t[1], rgb_t[2])

            buf = BytesIO()
            doc.save(buf)
            st.success("Adaptation pédagogique terminée.")
            st.download_button("📥 Télécharger le Word",
