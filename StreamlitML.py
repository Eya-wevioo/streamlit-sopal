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

# --- Fonction de nettoyage (utilisée en interne uniquement) ---
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

# Détecter le matériau à partir du nom
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

# Couleurs du nuage
color_map = {
    'alu': 'blue',
    'acier': 'grey',
    'laiton': 'goldenrod',
    'autre': 'black'
}

# Mots positifs retenus pour les nuages
mots_positifs = {
    "haute", "résistance", "excellente", "robustesse", "performance",
    "fiable", "durable", "optimale", "facile", "idéale", "qualité", 
    "fiabilité", "robuste", "résistant", "élevée"
}

# Charger les données
@st.cache_data
def load_data():
    return pd.read_excel("produits_structures.xlsx")

df = load_data()

# Nettoyage interne (non affiché)
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

# Layout : deux colonnes
col1, col2 = st.columns([2, 1])

# ----- 🧱 Colonne gauche : Sélection de produit -----
with col1:
    st.subheader("🔍 Sélection du produit")

    produit_selectionne = st.selectbox("Choisissez un produit :", df['Nom du produit'].unique())
    produit = df[df['Nom du produit'] == produit_selectionne].iloc[0]
    texte_nettoye = produit['Description_nettoyee']
    matiere = produit['Matériau']

    mots = set(texte_nettoye.split()) & mots_positifs
    texte_filtre = " ".join(mots)

    st.markdown("**🧾 Description produit :**")

    if not texte_filtre.strip():
        st.info("Aucun mot pertinent trouvé dans la description.")
    else:
        wc = WordCloud(
            width=350,
            height=350,
            background_color='white',
            max_words=50,
            color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
            collocations=False,
            prefer_horizontal=1,
            relative_scaling=0.5,
            min_font_size=10,
            max_font_size=22
        ).generate(texte_filtre)

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

# ----- 🧱 Colonne droite : Filtrage par matériau -----
with col2:
    st.subheader("🏗️ Filtrer par matériau")

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
    nb_produits = len(produits_filtres)

    st.markdown(f"**📦 Produits disponibles : {nb_produits}**")

    if nb_produits > 0:
        for p in produits_filtres:
            st.write(f"- {p}")
    else:
        st.info(f"Aucun produit trouvé pour la catégorie '{categorie_choisie}'.")
