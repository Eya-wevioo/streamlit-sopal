import streamlit as st 
import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Configuration de la page ---
st.set_page_config(page_title="Détails des matériaux", layout="wide")

# --- Image de fond depuis GitHub ---
background_url = "https://raw.githubusercontent.com/Eya-wevioo/streamlit-sopal/main/backphoto.png"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{background_url}');
        background-size: contain;  /* ou essaye aussi: 100% auto */
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
""", unsafe_allow_html=True)
# --- Titre principal ---
st.title("📋 Détails des matériaux")

# --- Stopwords ---
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
        st.subheader(":blue[☁️ Description]")

        ligne = df[df['Nom du produit'] == produit_selectionne].iloc[0]
        texte = ligne['Description_nettoyee']
        matiere = ligne['Matériau']
        mots = set(texte.split()) & mots_positifs
        texte_filtre = " ".join(mots)

        if not mots:
            st.info("Aucun mot positif identifié dans la description.")
        else:
            wc = WordCloud(
    		width=200,
    		height=100,
   	 	max_font_size=20,  # mot petit
    		background_color=None,
    		mode="RGBA",
    		max_words=30,
    		color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
    		collocations=False,
    		prefer_horizontal=1.0
	    ).generate(texte_filtre)

st.markdown("""
    <div style="border-radius: 20px; border: 2px solid navy; padding: 10px; background-color: rgba(255,255,255,0.05); display: inline-block;">
""", unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(2.5, 1.2))  # cadre petit
ax.imshow(wc, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

st.markdown("</div>", unsafe_allow_html=True)
