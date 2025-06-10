import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import string

# === Première commande obligatoire ===
st.set_page_config(page_title="Nuage de mots produits industriels", layout="centered")

# === Télécharger les stopwords si besoin ===
nltk.download('stopwords')

# === Initialisation ===
st.title("🌥️ Nuage de mots interactif - Produits industriels")

# === Chargement des données ===
def load_data():
    df = pd.read_excel("produits_structures.xlsx")
    return df

# === Nettoyage de texte (simple sans SpaCy) ===
def nettoyer_texte(text):
    mots = text.lower().split()
    mots_nettoyes = [
        mot.strip(string.punctuation)
        for mot in mots
        if mot not in stopwords.words('french') and mot.isalpha()
    ]
    return " ".join(mots_nettoyes)

# === Masque circulaire ===
def create_circle_mask(diameter=200):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > (center) ** 2
    mask = 255 * mask.astype(int)
    return mask

# === Couleur selon matériau ===
def make_color_func(matiere):
    color_map = {
        'alu': 'blue',
        'acier': 'grey',
        'laiton': 'goldenrod'
    }
    return lambda word, **kwargs: color_map.get(matiere, 'black')

# === Affichage du nuage ===
def afficher_nuage(texte, matiere, nom):
    mots_positifs = {
        "haute", "résistance", "excellente", "robustesse", "performance",
        "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
        "fiabilité", "robuste", "résistant", "élevée"
    }
    mots = [mot for mot in texte.split() if mot in mots_positifs]
    if not mots:
        st.info("Aucun mot positif identifié pour ce produit.")
        return

    texte_filtre = " ".join(mots)

    wc = WordCloud(
        width=200, height=200,
        background_color='white',
        mask=create_circle_mask(200),
        color_func=make_color_func(matiere),
        contour_width=1,
        contour_color='black',
        collocations=False,
        max_font_size=20,
        relative_scaling=0.5
    ).generate(texte_filtre)

    st.subheader(nom)
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# === Chargement des données ===
df = load_data()

# Nettoyage nom produit
if 'Nom du produit' in df.columns:
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
else:
    st.error("Colonne 'Nom du produit' manquante.")

# Nettoyage description
if 'Description' not in df.columns:
    st.error("Colonne 'Description' manquante.")
else:
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)

# Détecter matière
def detecter_matiere(nom):
    nom = nom.lower()
    if 'alu' in nom:
        return 'alu'
    elif 'acier' in nom:
        return 'acier'
    elif 'laiton' in nom:
        return 'laiton'
    else:
        return 'autre'

if 'Matériau' not in df.columns:
    df['Matériau'] = df['Nom du produit'].apply(detecter_matiere)

# Sélection
produit_selectionne = st.selectbox("Sélectionnez un produit :", df['Nom du produit'].unique())

produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
texte = produit['Description_nettoyee']
matiere = produit['Matériau']
nom = produit['Nom du produit']

# Affichage
afficher_nuage(texte, matiere, nom)
