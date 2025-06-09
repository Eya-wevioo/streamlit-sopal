import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import spacy

# Charger le modèle français de spaCy (attention à l'avoir installé et dans requirements.txt)
@st.cache_resource
def load_spacy_model():
    return spacy.load("fr_core_news_sm")

nlp = load_spacy_model()

# Nettoyage de texte avec spaCy
def nettoyer_texte(text):
    if not isinstance(text, str):
        return ""
    doc = nlp(text.lower())
    tokens = []
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        if token.is_alpha or token.like_num or any(char.isdigit() for char in token.text):
            tokens.append(token.lemma_)
    return " ".join(tokens)

# Détection automatique du matériau dans le nom du produit
def detecter_materiau(nom):
    nom = nom.lower()
    if "alu" in nom or "aluminium" in nom:
        return "alu"
    elif "acier" in nom or "c45" in nom:
        return "acier"
    elif "laiton" in nom:
        return "laiton"
    else:
        return "inconnu"

# Masque circulaire pour WordCloud
def create_circle_mask(diameter=400):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > (center) ** 2
    mask = 255 * mask.astype(int)
    return mask

# Fonction couleur selon matériau
def make_color_func(mat):
    color_map = {
        'alu': 'blue',
        'acier': 'grey',
        'laiton': 'goldenrod',
        'inconnu': 'black'
    }
    color = color_map.get(mat, 'black')
    def color_func(word, **kwargs):
        return color
    return color_func

mots_positifs = set([
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
])

st.title("🌥️ Nuage de mots interactif - Produits industriels")

uploaded_file = st.file_uploader("📁 Téléversez le fichier Excel des produits", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Nettoyer le nom du produit
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)

    # Nettoyer les descriptions
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)

    # Vérifier présence colonne 'Matériau' sinon la créer automatiquement
    if "Matériau" not in df.columns:
        df['Matériau'] = df['Nom du produit'].apply(detecter_materiau)
        st.info("ℹ️ Colonne 'Matériau' absente, détection automatique appliquée.")
    else:
        df['Matériau'] = df['Matériau'].fillna("inconnu").str.lower()

    # Sélection produit
    produit = st.selectbox("🔍 Choisissez un produit :", df["Nom du produit"])

    # Extraire description et matériau
    row = df[df["Nom du produit"] == produit].iloc[0]
    desc = row["Description_nettoyee"]
    materiau = row["Matériau"]

    # Filtrer sur mots positifs
    mots = [mot for mot in desc.split() if mot in mots_positifs]
    texte_filtre = " ".join(mots)

    if texte_filtre.strip():
        wc = WordCloud(
            width=400, height=400,
            background_color='white',
            mask=create_circle_mask(400),
            color_func=make_color_func(materiau),
            contour_width=3,
            contour_color='black',
            collocations=False,
            max_font_size=60,
            relative_scaling=0.5
        ).generate(texte_filtre)

        fig, ax = plt.subplots(figsize=(6,6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f"Nuage de mots produit : {produit} ({materiau})", fontsize=14)
        st.pyplot(fig)
    else:
        st.warning("⚠️ Pas de mots positifs trouvés pour ce produit.")
else:
    st.info("📄 Veuillez téléverser un fichier Excel contenant les données produits.")
