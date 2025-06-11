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

# Télécharger les stopwords une fois
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# Fonction de nettoyage de texte
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

# Détection du matériau
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

# Couleurs personnalisées pour nuage de mots
color_map = {
    'alu': 'blue',
    'acier': 'grey',
    'laiton': 'goldenrod',
    'autre': 'black'
}

# Mots positifs à garder
mots_positifs = {
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
}

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_excel("produits_structures.xlsx")

df = load_data()

# Nettoyage
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

# Disposition en deux colonnes
col1, col2 = st.columns([2, 1])

# ----- 🧱 Colonne Gauche : Description et nuage -----
with col1:
    st.subheader("🔍 Sélection du produit")

    produit_selectionne = st.selectbox("Choisissez un produit :", df['Nom du produit'].unique())
    produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
    texte = produit['Description_nettoyee']
    matiere = produit['Matériau']
    mots = set(texte.split()) & mots_positifs
    texte_filtre = " ".join(mots)

    st.markdown("**📝 Description nettoyée :**")
    st.write(texte if texte else "_Aucune description disponible_")

    st.markdown("**☁️ Nuage de mots qualitatifs :**")
    if not mots:
        st.info("Aucun mot positif identifié dans la description.")
    else:
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

# ----- 🧱 Colonne Droite : Filtrage par matériau -----
with col2:
    st.subheader("🧪 Filtrer les produits par matériau")

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
    categorie_choisie = st.selectbox("Sélectionnez un matériau :", ["acier", "alu", "laiton", "autre"])

    produits_filtres = df[df['Catégorie'] == categorie_choisie]['Nom du produit'].unique()

    if len(produits_filtres) > 0:
        for p in produits_filtres:
            st.write(f"- {p}")
    else:
        st.info(f"Aucun produit trouvé pour la catégorie '{categorie_choisie}'.")
