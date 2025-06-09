import streamlit as st
import pandas as pd
import spacy
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

# Charge le modèle français déjà installé via requirements.txt
nlp = spacy.load("fr_core_news_sm")

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

def create_circle_mask(diameter=400):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > center ** 2
    mask = 255 * mask.astype(int)
    return mask

def make_color_func(mat):
    color_map = {
        'alu': 'blue',
        'acier': 'grey',
        'laiton': 'goldenrod'
    }
    color = color_map.get(mat.lower(), 'black')
    def color_func(word, **kwargs):
        return color
    return color_func

mots_positifs = set([
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
])

st.title("🌥️ Nuages de mots interactifs - Produits industriels")

uploaded_file = st.file_uploader("📁 Téléversez votre fichier Excel des produits", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Supprimer " - PRIX UNITAIRE" dans 'Nom du produit'
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)

    # Nettoyage des descriptions
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)

    if 'Matériau' not in df.columns:
        st.error("❌ Colonne 'Matériau' manquante dans le fichier Excel.")
        st.stop()

    produit_choisi = st.selectbox("Choisissez un produit :", df["Nom du produit"])

    row = df[df['Nom du produit'] == produit_choisi].iloc[0]
    desc = row['Description_nettoyee']
    materiau = row['Matériau']

    mots = [mot for mot in desc.split() if mot in mots_positifs]

    if mots:
        texte_filtre = " ".join(mots)
        mask = create_circle_mask(400)
        wc = WordCloud(
            width=400,
            height=400,
            background_color='white',
            mask=mask,
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
        st.pyplot(fig)
    else:
        st.warning("⚠️ Aucun mot positif trouvé pour ce produit.")
else:
    st.info("📄 Veuillez téléverser un fichier Excel pour démarrer.")
