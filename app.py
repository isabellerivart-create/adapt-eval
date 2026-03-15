import streamlit as st
from docx import Document
from io import BytesIO
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

st.set_page_config(page_title="Adapt'Éval Wallonie", layout="wide", page_icon="🇧🇪")

# --- INTERFACE ---
st.title("🎓 Adapt'Éval - Primaire Wallonie")

with st.sidebar:
    st.header("⚙️ Configuration")
    niveau = st.selectbox("Année", ["P1", "P2", "P3", "P4", "P5", "P6"])
    profils = st.multiselect("Besoins spécifiques", ["TSA", "Dyslexie", "Dysorthographie", "Dyscalculie", "Dysphasie", "Dyspraxie", "TDA/H", "HPI"])

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("📥 Charger l'évaluation")
    file = st.file_uploader("Importer PDF ou DOCX", type=["pdf", "docx"])
    
    texte_extrait = ""
    if file:
        try:
            if file.type == "application/pdf":
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    texte_extrait += page.extract_text()
            else:
                doc = Document(file)
                texte_extrait = "\n".join([p.text for p in doc.paragraphs])
            st.success("Fichier lu avec succès !")
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
            
    txt_source = st.text_area("Texte à adapter :", value=texte_extrait, height=300)

with col_out:
    st.subheader("✨ Aperçu de l'adaptation")
    if st.button("LANCER L'ADAPTATION"):
        if txt_source:
            # Petite logique d'adaptation visuelle simple
            res = f"ÉVALUATION ADAPTÉE - {niveau}\n" + "="*20 + "\n\n"
            res += txt_source.replace("?", " ?\n" + "."*30 + "\n")
            st.text_area("Résultat :", value=res, height=300)
            
            # Bouton de téléchargement
            doc_final = Document()
            doc_final.add_paragraph(res)
            buf = BytesIO()
            doc_final.save(buf)
            st.download_button("📥 Télécharger .docx", data=buf.getvalue(), file_name="evaluation.docx")

st.info("Astuce : Si l'importation échoue, faites un simple copier-coller du texte dans la zone de gauche.")
