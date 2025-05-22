import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(
    page_title="Prédiction du Revenu Annuel",
    page_icon="💰",
    layout="wide"
)

# Titre de l'application
st.title("Prédiction du Revenu Annuel d'un Marocain")
st.markdown("Cette application permet de prédire le revenu annuel d'un marocain en fonction de ses caractéristiques socio-démographiques.")

# URL de l'API
API_URL = "http://localhost:8000/predict"

# Fonction pour faire une prédiction via l'API
def predict_income(data):
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur lors de la prédiction: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        return None

# Interface utilisateur pour saisir les données
st.header("Saisissez les informations")

# Création de colonnes pour organiser les inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Informations personnelles")
    age = st.slider("Âge", 18, 80, 30)
    
    
    sexe = st.radio("Sexe", ["Homme", "Femme"])
    
    milieu = st.radio("Milieu", ["Urbain", "Rural"])
    est_urbain = 1 if milieu == "Urbain" else 0
    
    etat_matrimonial = st.selectbox("État matrimonial", 
                                   ["Célibataire", "Marié", "Divorcé", "Veuf"])
    est_marie = 1 if etat_matrimonial == "Marié" else 0
    
    taille_foyer = st.slider("Taille du foyer", 1, 10, 3)
    

with col2:
    st.subheader("Éducation et profession")
    niveau_education = st.selectbox("Niveau d'éducation", 
                                   ["Sans niveau", "Fondamental", "Secondaire", "Supérieur"])
    
    annees_experience = st.slider("Années d'expérience", 0, 50, 5)
    
    categorie_socioprofessionnelle = st.selectbox("Catégorie socioprofessionnelle", 
                                                 ["Groupe 1 : Cadres supérieurs et professions libérales",
                                                  "Groupe 2 : Cadres moyens et employés",
                                                  "Groupe 3 : Inactifs (retraités, rentiers)",
                                                  "Groupe 4 : Travailleurs agricoles",
                                                  "Groupe 5 : Ouvriers qualifiés et artisans",
                                                  "Groupe 6 : Manœuvres et chômeurs"])
    
    a_retraite = st.checkbox("Bénéficie d'une retraite")
    aide_sociale = st.checkbox("Bénéficie d'une aide sociale")
    a_acces_credit = st.checkbox("A accès au crédit")

with col3:
    st.subheader("Patrimoine et région")
    possede_voiture = st.checkbox("Possède une voiture")
    possede_logement = st.checkbox("Possède un logement")
    possede_terrain = st.checkbox("Possède un terrain")
    
    # Calcul automatique du niveau socio-économique
    niveau_socioeco = float(possede_voiture) + float(possede_logement) + float(possede_terrain)
    st.info(f"Niveau socio-économique: {niveau_socioeco}/3")
    
    regions = [
        "Tanger-Tétouan-Al Hoceïma", "L'Oriental", "Fès-Meknès", "Rabat-Salé-Kénitra",
        "Béni Mellal-Khénifra", "Casablanca-Settat", "Marrakech-Safi", "Drâa-Tafilalet",
        "Souss-Massa", "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"
    ]
    region = st.selectbox("Région", regions)

# Bouton pour lancer la prédiction
if st.button("Prédire le revenu annuel"):
    # Préparation des données pour l'API
    input_data = {
        "age": age,
        "sexe": sexe,
        "milieu": milieu,
        "etat_matrimonial": etat_matrimonial,
        "region": region,
        "niveau_education": niveau_education,
        "categorie_socioprofessionnelle": categorie_socioprofessionnelle,
        "taille_foyer": float(taille_foyer),
        "aide_sociale": int(aide_sociale),
        "a_acces_credit": int(a_acces_credit),
        "a_retraite": int(a_retraite),
        "possede_voiture": float(possede_voiture),
        "possede_logement": float(possede_logement),
        "possede_terrain": int(possede_terrain),
        "annees_experience": float(annees_experience),
        "est_urbain": est_urbain,
        "est_marie": est_marie,
        "weight": 1.0,
        "niveau_socioeco": float(niveau_socioeco)
    }

    # Appel à l'API pour la prédiction
    with st.spinner("Calcul en cours..."):
        result = predict_income(input_data)
    
    if result:
        # Affichage du résultat
        st.success(f"Revenu annuel prédit: {result['revenu_predit']:.2f} DH")
        
        # Visualisation du résultat
        st.subheader("Comparaison avec les moyennes nationales")
        
        # Données de référence (selon l'énoncé)
        revenu_moyen_national = 21949
        revenu_moyen_urbain = 26988
        revenu_moyen_rural = 12862
        
        # Création d'un dataframe pour la visualisation
        comparison_data = pd.DataFrame({
            'Catégorie': ['Prédiction', 'Moyenne nationale', 
                         f'Moyenne {milieu.lower()}'],
            'Revenu annuel (DH)': [result['revenu_predit'], revenu_moyen_national, 
                                  revenu_moyen_urbain if milieu == "Urbain" else revenu_moyen_rural]
        })
        
        # Création du graphique
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = sns.barplot(x='Catégorie', y='Revenu annuel (DH)', data=comparison_data, ax=ax)
        
        # Ajout des valeurs sur les barres
        for bar in bars.patches:
            bars.annotate(f"{bar.get_height():.0f} DH",
                         (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                         ha='center', va='bottom', fontsize=10)
        
        ax.set_title('Comparaison du revenu prédit avec les moyennes nationales')
        ax.set_ylabel('Revenu annuel (DH)')
        ax.set_xlabel('')
        
        # Affichage du graphique dans Streamlit
        st.pyplot(fig)
        
        # Interprétation du résultat
        if result['revenu_predit'] > revenu_moyen_national:
            st.info(f"Le revenu prédit est supérieur à la moyenne nationale de {result['revenu_predit'] - revenu_moyen_national:.2f} DH.")
        else:
            st.info(f"Le revenu prédit est inférieur à la moyenne nationale de {revenu_moyen_national - result['revenu_predit']:.2f} DH.")
        
        # Calcul du revenu par personne
        revenu_par_personne = result['revenu_predit'] / taille_foyer
        st.info(f"Revenu par personne dans le foyer: {revenu_par_personne:.2f} DH")
        
        # Affichage de la position par rapport au seuil de pauvreté
        seuil_pauvrete = 5000  # Exemple de seuil de pauvreté (à ajuster selon les données réelles)
        if revenu_par_personne < seuil_pauvrete:
            st.warning(f"Le revenu par personne est inférieur au seuil de pauvreté estimé à {seuil_pauvrete} DH.")
        else:
            st.success(f"Le revenu par personne est supérieur au seuil de pauvreté estimé à {seuil_pauvrete} DH.")

# Informations supplémentaires
st.header("Informations sur le modèle")
st.markdown("""
Ce modèle a été entraîné sur un dataset simulé de 40 000 Marocains avec des caractéristiques socio-démographiques variées.
Les principales variables qui influencent le revenu sont:
- L'âge et la catégorie d'âge
- Le sexe
- Le milieu (urbain/rural)
- Le niveau d'éducation
- Les années d'expérience
- La catégorie socioprofessionnelle
- La région
- Les possessions (voiture, logement, terrain)
- L'accès au crédit et aux aides sociales
""")

# Pied de page
st.markdown("---")
st.markdown("Mini-projet Intelligence Artificielle - 2ème année Cycle d'ingénieurs GI")