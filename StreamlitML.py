import streamlit as st
import pandas as pd
import spacy
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np

# === Initialisation NLP ===
st.set_page_config(page_title="Nuage de mots produits industriels", layout="centered")
st.title("🌥️ Nuage de mots interactif - Produits industriels")

@st.cache_resource

def load_spacy_model():
    return spacy.load("fr_core_news_sm")

nlp = load_spacy_model()

# === Chargement des données ===
def load_data():
    df = pd.read_excel("produits_structures.xlsx")
    return df

# === Nettoyage ===
def nettoyer_texte(text):
    doc = nlp(text.lower())
    tokens = []
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        if token.is_alpha or token.like_num or any(char.isdigit() for char in token.text):
            tokens.append(token.lemma_)
    return " ".join(tokens)

# === Masque circulaire ===
def create_circle_mask(diameter=400):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > (center) ** 2
    mask = 255 * mask.astype(int)
    return mask

# === Palette des couleurs ===
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

# === Affichage ===
def afficher_nuage(texte, matiere, nom):
    mots_positifs = set([
        "haute", "résistance", "excellente", "robustesse", "performance",
        "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
        "fiabilité", "robuste", "résistant", "élevée"
    ])
    mots = [mot for mot in texte.lower().split() if mot in mots_positifs]
    if not mots:
        st.info("Aucun mot positif identifié pour ce produit.")
        return
    texte_filtre = " ".join(mots)
    wc = WordCloud(
        width=400, height=400,
        background_color='white',
        mask=create_circle_mask(400),
        color_func=make_color_func(matiere),
        contour_width=2,
        contour_color='black',
        collocations=False,
        max_font_size=50,
        relative_scaling=0.5
    ).generate(texte_filtre)
    st.subheader(nom)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# === Main ===
df = load_data()

# Nettoyage
if 'Nom du produit' in df.columns:
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
else:
    st.error("Colonne 'Nom du produit' manquante dans le fichier Excel.")

if 'Description' not in df.columns:
    st.error("Colonne 'Description' manquante dans le fichier Excel.")
else:
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)

# Matériaux (supposition basée sur le nom du produit)
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

# Sélection produit
produit_selectionne = st.selectbox("Sélectionnez un produit :", df['Nom du produit'].unique())

produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
texte = produit['Description_nettoyee']
matiere = produit['Matériau']
nom = produit['Nom du produit']

afficher_nuage(texte, matiere, nom)
