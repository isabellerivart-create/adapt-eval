import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2
import re

st.set_page_config(page_title="Adapt'Éval Expert Wallonie", layout="wide")

# 1. MOTEUR DE REFORMULATION ET DÉCOUPAGE
DICTIONNAIRE_PEDAGO = {
    "indique": "DIS",
    "souligne": "FAIS UN TRAIT SOUS",
    "entoure": "FAIS UN ROND AUTOUR DE",
    "conjugue": "ÉCRIS LE VERBE",
    "identifie": "TROUVE",
    "complète": "ÉCRIS CE QUI MANQUE",
    "quels sont": "TROUVE LES",
    "ajoute": "METS"
}

# Notions à mettre en couleur
COULEURS_NOTIONS = {
    "passé": (200, 0, 0),    # Rouge
    "présent": (0, 128, 0),  # Vert
    "futur": (0, 0, 200),    # Bleu
    "infinitif": (128, 0, 128) # Violet
}

st.title("🎓 Adapt'Éval - Expert Inclusion")

with st.sidebar:
    st.header("⚙️ Réglages Pédagogiques")
    profils = st.multiselect("Besoins", ["Dyslexie", "Dysorthographie", "TSA", "Dyspraxie"], default=["Dyslexie"])
    passion = st.text_input("Passion (ex: les trains)", "")
    st.divider()
    st.info("L'outil va colorer les notions temporelles et reformuler les verbes de consigne.")

col_in, col_out = st.columns(2)

with col_in:
    file = st.file_uploader("Document source", type=["pdf", "docx"])
    texte_brut = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            texte_brut = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            doc = Document(file)
            texte_brut = "\n".join([p.text for p in doc.paragraphs])
    txt_input = st.text_area("Texte original :", value=texte_brut, height=400)

def appliquer_pedagogie(ligne, passion):
    t = ligne.strip()
    if not t: return None
    
    # Correction Majuscule
    t = t[0].upper() + t[1:] if len(t) > 1 else t
    
    # Reformulation FALC / Action
    for k, v in DICTIONNAIRE_PEDAGO.items():
        if k in t.lower():
            t = re.sub(k, f"**{v}**", t, flags=re.IGNORECASE)
    
    # Contextualisation
    if passion:
        remp = {"maman": f"le conducteur du {passion}", "le bus": "le wagon", "papa": "le mécanicien"}
        for k, v in remp.items():
            if k in t.lower(): t = re.sub(k, v.upper(), t, flags=re.IGNORECASE)
            
    return t

with col_out:
    if st.button("🚀 GÉNÉRER L'ADAPTATION PÉDAGOGIQUE"):
        if txt_input:
            doc = Document()
            for s in doc.sections: s.left_margin = Cm(2.5)
            
            lignes = txt_input.split('\n')
            for l in lignes:
                t_pret = appliquer_pedagogie(l, passion)
                if not t_pret: continue
                
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 2.0
                p.paragraph_format.space_after = Pt(20)

                # Colorisation intelligente
                # On découpe par les marqueurs de gras **
                parts = t_pret.split("**")
                for i, part in enumerate(parts):
                    run = p.add_run(part)
                    run.font.name = 'Arial'
                    run.font.size = Pt(14)
                    
                    if i % 2 != 0: # Consigne reformulée
                        run.bold = True
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(0, 51, 102) # Bleu foncé
                    
                    # Colorer les notions au sein du texte
                    for notion, color in COULEURS_NOTIONS.items():
                        if notion in part.lower():
                            run.font.color.rgb = RGBColor(*color)
                            run.bold = True
                
                # Ajouter une ligne de réponse si c'est une question
                if "?" in t_pret or "..." in t_pret:
                    resp = doc.add_paragraph("➞ Réponse : ...........................................................")
                    resp.paragraph_format.space_after = Pt(20)

            buf = BytesIO()
            doc.save(buf)
            st.success("Adaptation terminée avec succès !")
            st.download_button("📥 Télécharger le Word Adapté", data=buf.getvalue(), file_name="EVAL_DYS_WALLONIE.docx")
