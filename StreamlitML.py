import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# Fonction simple pour nettoyer le texte
def nettoyer_texte(texte):
    if not isinstance(texte, str):
        return ""
    # Mettre en minuscule
    texte = texte.lower()
    # Supprimer les caractères spéciaux et chiffres
    texte = re.sub(r'[^a-z\s]', ' ', texte)
    # Supprimer les espaces multiples
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte

# Charger les données
<<<<<<< HEAD
df = pd.read_excel(r"C:\Users\Eya jerbi\Desktop\PFESOPALDOSSIER\produits_structures.xlsx")

=======
df = pd.read_excel("produits_structures.xlsx")
>>>>>>> 0e23b93 (Ajout des fichiers pour déploiement Streamlit)
# Nettoyer la colonne Description pour créer une nouvelle colonne
df["Description_nettoyee"] = df["Description"].apply(nettoyer_texte)

st.title("🌥️ Nuages de mots interactifs - Produits industriels")

# Sélectionner un produit
produit = st.selectbox("Choisissez un produit :", df["Nom du produit"])

# Récupérer la description nettoyée du produit sélectionné
desc = df.loc[df["Nom du produit"] == produit, "Description_nettoyee"].values[0]

# Générer et afficher le nuage de mots si la description n'est pas vide
if desc.strip():
    wc = WordCloud(width=600, height=300, background_color="white").generate(desc)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("Aucune description disponible pour ce produit.")
