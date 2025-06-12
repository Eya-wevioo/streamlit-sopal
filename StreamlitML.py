import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy

# ----------------------- CONFIGURATION DU STYLE -----------------------

# URL GitHub brute de ton image
background_url = "https://raw.githubusercontent.com/Eya-wevioo/streamlit-sopal/main/backphoto.png"

# Ajout de l’image en fond d’écran (Cloud-compatible)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
    }}
    .rounded-box {{
        background-color: rgba(255, 255, 255, 0); /* Fond transparent */
        border: 3px solid #003366; /* Contour bleu foncé */
        border-radius: 20px;
        padding: 20px;
        margin-top: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------- CHARGEMENT DES DONNÉES -----------------------

df = pd.read_excel("produits_structures.xlsx")

# Nettoyage NLP
def nettoyer_description(texte):
    texte = str(texte)
    texte = texte.replace("PRIX UNITAIRE", "")
    nlp = spacy.blank("fr")
    doc = nlp(texte)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

df["Description_nettoyee"] = df["Description"].apply(nettoyer_description)

# ----------------------- INTERFACE UTILISATEUR -----------------------

st.markdown("## 🧾 Détails des matériaux")
col1, col2 = st.columns([2, 1])

# Colonne de gauche : Description
with col1:
    st.markdown("### 💡 Description")
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)

    if "selected_product" not in st.session_state:
        st.session_state["selected_product"] = None

    if st.session_state["selected_product"]:
        desc = df[df["Nom du produit"] == st.session_state["selected_product"]]["Description_nettoyee"].values[0]

        # Créer un nuage de mots transparent
        wc = WordCloud(width=600, height=300, background_color=None, mode="RGBA", colormap='Greys',
                       max_font_size=40, min_font_size=20).generate(desc)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.markdown("⬅️ Sélectionnez un produit pour voir sa description")

    st.markdown('</div>', unsafe_allow_html=True)

# Colonne de droite : Filtres
with col2:
    st.markdown("### 🔍 Filtrer par matériau")
    materiaux = df["Nom du produit"].str.extract(r'([a-zA-Z]+)')[0].str.lower().dropna().unique()
    materiau_selectionne = st.selectbox("Sélectionnez un matériau :", options=sorted(materiaux))

    produits_filtres = df[df["Nom du produit"].str.lower().str.contains(materiau_selectionne)]

    st.markdown(f"📦 **{len(produits_filtres)} produit(s) disponible(s)** :")
    st.markdown("Cliquez sur un produit :")

    selected = st.radio("Produits :", produits_filtres["Nom du produit"].tolist(), label_visibility="collapsed")

    if selected:
        st.session_state["selected_product"] = selected
