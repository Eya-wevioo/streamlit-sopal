import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import spacy
import re

# Charger modèle NLP français
nlp = spacy.load("fr_core_news_sm")

# Fonction de nettoyage avancée
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

# Masque circulaire pour nuage
def create_circle_mask(diameter=400):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > (center) ** 2
    mask = 255 * mask.astype(int)
    return mask

# Mots valorisants
mots_positifs = set([
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
])

# Fonction de couleur par matériau
def make_color_func(mat):
    color_map = {
        'alu': 'blue',
        'acier': 'grey',
        'laiton': 'goldenrod'
    }
    color = color_map.get(mat, 'black')
    def color_func(word, **kwargs):
        return color
    return color_func

# Charger les données
@st.cache_data
def charger_donnees():
    df = pd.read_excel("produits_structures.xlsx")
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)
    return df

# Application Streamlit
st.title("🌥️ Nuages de mots interactifs - Produits industriels avec NLP avancé")
df = charger_donnees()
produit = st.selectbox("Choisissez un produit :", df["Nom du produit"])
ligne = df[df["Nom du produit"] == produit].iloc[0]

texte = ligne['Description_nettoyee']
materiau = ligne.get("Matériau", "")

# Extraire et filtrer les mots
mots = [mot for mot in texte.lower().split() if mot in mots_positifs]
texte_filtre = " ".join(mots)

if texte_filtre.strip():
    wc = WordCloud(
        width=500,
        height=500,
        background_color='white',
        mask=create_circle_mask(500),
        color_func=make_color_func(materiau),
        contour_width=2,
        contour_color='black',
        collocations=False,
        max_font_size=60,
        relative_scaling=0.5
    ).generate(texte_filtre)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("Aucune description valorisante trouvée pour ce produit.")
