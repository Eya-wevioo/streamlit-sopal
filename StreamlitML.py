import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import re
import spacy

# Initialisation de spaCy
nlp = spacy.load("fr_core_news_sm")

# Fonction de nettoyage de texte
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
        'laiton': 'goldenrod'
    }
    color = color_map.get(mat, 'black')
    def color_func(word, **kwargs):
        return color
    return color_func

# Liste de mots positifs
mots_positifs = set([
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
])

# 🎯 Interface Streamlit
st.title("🌥️ Nuage de mots interactif - Produits industriels")

# 📥 Chargement des données Excel
try:
    df = pd.read_excel("produits_structures.xlsx")
except FileNotFoundError:
    st.error("❌ Fichier 'produits_structures.xlsx' introuvable. Veuillez l'ajouter.")
    st.stop()

# Nettoyage des champs
df["Nom du produit"] = df["Nom du produit"].str.replace(' - PRIX UNITAIRE', '', regex=False)
df["Description_nettoyee"] = df["Description"].fillna("").apply(nettoyer_texte)

# Vérification présence colonne 'Matériau'
if "Matériau" not in df.columns:
    st.error("❌ Colonne 'Matériau' manquante dans le fichier Excel.")
    st.stop()

# Choix interactif
produit = st.selectbox("🔍 Choisissez un produit :", df["Nom du produit"])

# Extraction
row = df[df["Nom du produit"] == produit].iloc[0]
desc = row["Description_nettoyee"]
materiau = row["Matériau"]

# Filtrage positif
mots = [mot for mot in desc.split() if mot in mots_positifs]
texte_filtre = " ".join(mots)

# Affichage du nuage
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

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("⚠️ Pas de mots positifs trouvés pour ce produit.")
