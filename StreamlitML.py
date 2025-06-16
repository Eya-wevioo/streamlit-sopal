with col1:
    if produit_selectionne:
        st.markdown("""<span class='colored-text' style='color: rgb(0, 104, 201); font-size: 20px;'>☁️ Description</span>""", unsafe_allow_html=True)

        ligne = df[df['Nom du produit'] == produit_selectionne].iloc[0]
        texte = ligne['Description_nettoyee']
        matiere = ligne['Matériau']
        mots = set(texte.split()) & mots_positifs
        texte_filtre = " ".join(mots)

        if not mots:
            st.info("Aucun mot positif identifié dans la description.")
        else:
            # Création du WordCloud avec des paramètres plus petits
            wc = WordCloud(
                width=200,  # Réduit la taille
                height=100,
                max_font_size=14,  # Police plus petite
                min_font_size=6,
                background_color=None,
                mode="RGBA",
                max_words=30,  # Moins de mots
                color_func=lambda *args, **kwargs: color_map.get(matiere, 'black'),
                collocations=False,
                prefer_horizontal=0.9
            ).generate(texte_filtre)

            # Création de la figure
            fig, ax = plt.subplots(figsize=(2, 1))  # Taille réduite
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout(pad=0)

            # Conversion en image
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
            buffer.seek(0)
            plt.close(fig)

            # Affichage dans le cadre bleu
            st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center; 
                border-radius: 15px; border: 2px solid #004080; padding: 10px; 
                background-color: rgba(255, 255, 255, 0.05); width: 250px; 
                height: 150px; margin-top: 10px; overflow: hidden;">
            """, unsafe_allow_html=True)
            
            st.image(buffer, use_container_width=True)  # Correction ici
            
            st.markdown("</div>", unsafe_allow_html=True)