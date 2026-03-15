import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# --- CONFIGURATION ---
st.set_page_config(page_title="Adapt'Éval Wallonie Expert", layout="wide", page_icon="🇧🇪")

DICTIONNAIRE_FALC = {
    "indique": "dis", "souligne": "fais un trait sous", "entoure": "fais un rond autour de",
    "conjugue": "écris le verbe", "identifie": "trouve", "illustre": "fais un dessin",
    "complète": "écris ce qui manque", "effectue": "fais", "réécris": "écris encore"
}

st.title("🎓 Adapt'Éval - Inclusion Wallonie")

with st.sidebar:
    st.header("👤 Profil de l'élève")
    niveau = st.selectbox("Année d'étude", ["P1", "P2", "P3", "P4", "P5", "P6"])
    profils = st.multiselect("Aménagements TND", ["TSA", "Dyslexie", "Dysorthographie", "Dyscalculie", "Dysphasie", "Dyspraxie", "TDA/H", "HPI", "Déficience Intellectuelle"])
    st.divider()
    st.header("🚂 Contextualisation")
    passion = st.text_input("Passion (ex: les trains)", "")

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("📥 Évaluation Source")
    file = st.file_uploader("Importer PDF ou DOCX", type=["pdf", "docx"])
    texte_initial = ""
    if file:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texte_initial += page.extract_text() + "\n"
        else:
            doc = Document(file)
            texte_initial = "\n".join([p.text for p in doc.paragraphs])
    txt_source = st.text_area("Texte original :", value=texte_initial, height=400)

def transformer_texte(texte, profils, passion):
    lignes = texte.split('\n')
    nouvelles_lignes = []
    for ligne in lignes:
        if not ligne.strip(): continue
        t = ligne
        if passion:
            remplacements = {"maman": f"le conducteur du {passion}", "papa": f"le mécanicien", "le bus": f"le wagon", "les enfants": "les voyageurs"}
            for ancien, nouveau in remplacements.items():
                if ancien in t.lower(): t = t.lower().replace(ancien, nouveau.upper())
        for complexe, simple in DICTIONNAIRE_FALC.items():
            if complexe in t.lower(): t = t.lower().replace(complexe, f"**{simple.upper()}**")
        if "TSA" in profils and ("?" in t or "..." in t):
            t = "📍 " + t + "\n➡️ (Ma réponse) : ____________________"
        nouvelles_lignes.append(t)
    return nouvelles_lignes

with col_out:
    st.subheader("✨ Résultat Adapté")
    if st.button("🚀 APPLIQUER LES AMÉNAGEMENTS"):
        if txt_source:
            res_lignes = transformer_texte(txt_source, profils, passion)
            doc_final = Document()
            style = doc_final.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(14)
            for ligne in res_lignes:
                p = doc_final.add_paragraph()
                p.paragraph_format.line_spacing = 1.5
                parts = ligne.split("**")
                for i, part in enumerate(parts):
                    run = p.add_run(part)
                    if i % 2 != 0: 
                        run.bold = True
                        run.font.size = Pt(16)
                st.write(ligne)
            buf = BytesIO()
            doc_final.save(buf)
            st.download_button("📥 Télécharger", data=buf.getvalue(), file_name="evaluation_adaptee.docx")
