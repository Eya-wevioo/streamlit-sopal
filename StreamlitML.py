import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuration Streamlit
st.set_page_config(page_title="Produits industriels", layout="centered")
st.title("🌥️ Description des matériaux disponibles")

# Télécharger stopwords français (une fois)
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# Nettoyage texte (minuscules, ponctuation, stopwords)
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

# Détecter matériau pour la couleur
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

# Palette couleurs par matériau
color_map = {
    'alu': 'blue',
    'acier': 'grey',
    'laiton': 'goldenrod',
    'autre': 'black'
}

# Liste de mots positifs à garder dans le nuage
mots_positifs = {
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
}

# Chargement données
@st.cache_data
def load_data():
    return pd.read_excel("produits_structures.xlsx")

df = load_data()

# Nettoyage noms produits (suppression " - PRIX UNITAIRE")
if 'Nom du produit' in df.columns:
    df['Nom du produit'] = df['Nom du produit'].str.replace(' - PRIX UNITAIRE', '', regex=False)
else:
    st.error("Colonne 'Nom du produit' manquante.")

# Nettoyage descriptions
if 'Description' in df.columns:
    df['Description_nettoyee'] = df['Description'].fillna("").apply(nettoyer_texte)
else:
    st.error("Colonne 'Description' manquante.")

# Détection matériau (ajoute colonne 'Matériau' si absente)
if 'Matériau' not in df.columns:
    df['Matériau'] = df['Nom du produit'].apply(detecter_matiere)

# Sélection produit
produit_selectionne = st.selectbox("Sélectionnez un produit :", df['Nom du produit'].unique())

produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
texte = produit['Description_nettoyee']
matiere = produit['Matériau']
nom = produit['Nom du produit']

# Filtrer les mots positifs uniques
mots = set(texte.split()) & mots_positifs

if not mots:
    st.info("Aucun mot positif identifié dans la description.")
else:
    texte_filtre = " ".join(mots)
    
    wc = WordCloud(
        width=400, height=400,
        background_color='white',
        max_words=50,
        color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
        collocations=False
    ).generate(texte_filtre)
    
    st.markdown("---")  # Séparateur visuel

# Disposition en deux colonnes : 2/3 gauche pour nuage, 1/3 droite pour filtre
col1, col2 = st.columns([2, 1])

# Colonne gauche : Nuage de mots
with col1:
    st.header("📋 Description des matériaux disponibles")
    
    # Sélection produit
    produit_selectionne = st.selectbox("Sélectionnez un produit :", df['Nom du produit'].unique())

    produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
    texte = produit['Description_nettoyee']
    matiere = produit['Matériau']
    nom = produit['Nom du produit']

    mots = set(texte.split()) & mots_positifs

    if not mots:
        st.info("Aucun mot positif identifié dans la description.")
    else:
        texte_filtre = " ".join(mots)
        wc = WordCloud(
            width=400, height=400,
            background_color='white',
            max_words=50,
            color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
            collocations=False
        ).generate(texte_filtre)
        
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

# Colonne droite : Classification simple par matériau
with col2:
    st.header("📦 Liste des produits par matériau")

    def classifier_materiau(nom):
        nom = nom.lower()
        if "acier" in nom:
            return "acier"
        elif "alu" in nom:
            return "alu"
        elif "laiton" in nom:
            return "laiton"
        else:
            return "autre"

    df['Catégorie'] = df['Nom du produit'].apply(classifier_materiau)

    categorie_choisie = st.selectbox("Choisissez un matériau :", ["acier", "alu", "laiton", "autre"], key="filtre_materiau")

    produits_filtres = df[df['Catégorie'] == categorie_choisie]['Nom du produit'].unique()

    st.markdown("**🛒 Produits correspondants :**")
    if len(produits_filtres) > 0:
        for p in produits_filtres:
            st.write(f"- {p}")
    else:
        st.info(f"Aucun produit trouvé pour la catégorie '{categorie_choisie}'.")
