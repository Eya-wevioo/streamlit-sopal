import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(page_title="Détails des matériaux", layout="wide")

# Titre principal
st.title("📋 Détails des matériaux")

# Télécharger les stopwords une seule fois
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# --- Fonctions ---

def nettoyer_texte(text):
    if not isinstance(text, str):
        return ""
    mots = text.lower().split()
    mots_nettoyes = [
        mot.strip(string.punctuation)
        for mot in mots
        if mot.isalpha() and mot not in stop_words
    ]
    return " ".join(mots_nettoyes)

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

color_map = {
    'alu': 'blue',
    'acier': 'grey',
    'laiton': 'goldenrod',
    'autre': 'black'
}

mots_positifs = {
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
}

@st.cache_data
def load_data():
    return pd.read_excel("produits_structures.xlsx")

# --- Données ---
df = load_data()

if 'Nom du produit' in df.columns:
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
else:
    st.error("Colonne 'Nom du produit' manquante.")

if 'Description' in df.columns:
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)
else:
    st.error("Colonne 'Description' manquante.")

if 'Matériau' not in df.columns:
    df['Matériau'] = df['Nom du produit'].apply(detecter_matiere)

# Catégorie produit
df['Catégorie'] = df['Nom du produit'].apply(detecter_matiere)

# --- Interface principale ---
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🔎 Filtrer par matériau")

    materiau_choisi = st.selectbox("Sélectionnez un matériau :", ["acier", "alu", "laiton", "autre"])
    produits_filtrés = df[df['Catégorie'] == materiau_choisi]['Nom du produit'].unique()

    st.markdown(f"**🛒 {len(produits_filtrés)} produit(s) disponible(s) :**")
    produit_selectionne = st.radio("Cliquez sur un produit :", produits_filtrés, index=0 if produits_filtrés.size > 0 else None)

with col1:
    if produit_selectionne:
        st.subheader("☁️ Description")

        ligne = df[df['Nom du produit'] == produit_selectionne].iloc[0]
        texte = ligne['Description_nettoyee']
        matiere = ligne['Matériau']
        mots = set(texte.split()) & mots_positifs
        texte_filtre = " ".join(mots)

        if not mots:
            st.info("Aucun mot positif identifié dans la description.")
        else:
            wc = WordCloud(
                width=100,
                height=100,
                background_color='white',
                max_words=50,
                color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
                collocations=False,
                prefer_horizontal=1.0,
                font_path=None
            ).generate(texte_filtre)

            fig, ax = plt.subplots(figsize=(3, 3))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
