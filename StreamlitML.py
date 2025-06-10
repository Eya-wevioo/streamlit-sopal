import streamlit as st
import pandas as pd
import spacy
from spacy.cli import download
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

# --- IMPORTANT : set_page_config doit être appelé en premier ---
st.set_page_config(page_title="Nuage de mots produits industriels", layout="centered")

# === Titre de la page ===
st.title("🌥️ Nuage de mots interactif - Produits industriels")

# === Chargement du modèle SpaCy avec cache et téléchargement automatique ===
@st.cache_resource
def load_spacy_model():
    model_name = "fr_core_news_sm"
    try:
        nlp = spacy.load(model_name)
    except OSError:
        download(model_name)
        nlp = spacy.load(model_name)
    return nlp

nlp = load_spacy_model()

# === Chargement des données ===
@st.cache_data
def load_data():
    df = pd.read_excel("produits_structures.xlsx")
    return df

df = load_data()

# Nettoyage de la colonne "Nom du produit"
if 'Nom du produit' in df.columns:
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
else:
    st.error("Colonne 'Nom du produit' manquante dans le fichier Excel.")

# Nettoyage de la description
if 'Description' not in df.columns:
    st.error("Colonne 'Description' manquante dans le fichier Excel.")
else:
    def nettoyer_texte(text):
        doc = nlp(text.lower())
        tokens = []
        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            if token.is_alpha or token.like_num or any(char.isdigit() for char in token.text):
                tokens.append(token.lemma_)
        return " ".join(tokens)
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)

# Détection du matériau à partir du nom
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

# Masque circulaire réduit pour WordCloud
def create_circle_mask(diameter=300):
    x, y = np.ogrid[:diameter, :diameter]
    center = diameter / 2
    mask = (x - center) ** 2 + (y - center) ** 2 > (center) ** 2
    mask = 255 * mask.astype(int)
    return mask

# Palette des couleurs
def make_color_func(mat):
    color_map = {
        'alu': 'blue',
        'acier': 'grey',
        'laiton': 'goldenrod',
        'autre': 'black'
    }
    return lambda word, **kwargs: color_map.get(mat, 'black')

# Affichage du nuage de mots
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
        width=300, height=300,
        background_color='white',
        mask=create_circle_mask(300),
        color_func=make_color_func(matiere),
        contour_width=1,
        contour_color='black',
        collocations=False,
        max_font_size=30,
        min_font_size=10,
        margin=1,
        max_words=50
    ).generate(texte_filtre)

    st.markdown(f"#### {nom}")  # Titre plus petit (niveau 4)
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(fig)

# Sélection d’un produit
produit_selectionne = st.selectbox("Sélectionnez un produit :", df['Nom du produit'].unique())

produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
texte = produit['Description_nettoyee']
matiere = produit['Matériau']
nom = produit['Nom du produit']

# Affichage du nuage de mots
afficher_nuage(texte, matiere, nom)
