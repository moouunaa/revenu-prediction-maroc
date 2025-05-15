import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from batch_prediction import batch_prediction_page

# Configuration de la page
st.set_page_config(
    page_title="Prédiction du Revenu Annuel",
    page_icon="💰",
    layout="wide"
)

# Fonction pour la page principale
def main_page():
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
                return response.json()["revenu_predit"]
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
        
        # Catégorie d'âge (calculée automatiquement)
        if age < 30:
            categorie_age = "Jeune"
            categorie_age_encoded = 0
        elif age < 50:
            categorie_age = "Adulte"
            categorie_age_encoded = 1
        elif age < 65:
            categorie_age = "Sénior"
            categorie_age_encoded = 2
        else:
            categorie_age = "Âgé"
            categorie_age_encoded = 3
        
        st.info(f"Catégorie d'âge: {categorie_age}")
        
        sexe = st.radio("Sexe", ["Homme", "Femme"])
        sexe_Homme = sexe == "Homme"
        
        milieu = st.radio("Milieu", ["Urbain", "Rural"])
        milieu_Urbain = milieu == "Urbain"
        
        taille_foyer = st.slider("Taille du foyer", 1, 10, 3)
        
        etat_matrimonial = st.selectbox("État matrimonial", 
                                       ["Célibataire", "Marié", "Divorcé", "Veuf"])
        # One-hot encoding pour l'état matrimonial
        etat_matrimonial_Célibataire = etat_matrimonial == "Célibataire"
        etat_matrimonial_Marié = etat_matrimonial == "Marié"
        etat_matrimonial_Divorcé = etat_matrimonial == "Divorcé"
        etat_matrimonial_Veuf = etat_matrimonial == "Veuf"

    with col2:
        st.subheader("Éducation et profession")
        niveau_education = st.selectbox("Niveau d'éducation", 
                                       ["Sans niveau", "Fondamental", "Secondaire", "Supérieur"])
        
        # Encodage du niveau d'éducation
        education_mapping = {"Sans niveau": 0, "Fondamental": 1, "Secondaire": 2, "Supérieur": 3}
        niveau_education_encoded = education_mapping[niveau_education]
        
        annees_experience = st.slider("Années d'expérience", 0, 50, 5)
        
        categorie_sociopro = st.selectbox("Catégorie socioprofessionnelle", 
                                         ["Groupe 1: Cadres supérieurs et professions libérales",
                                          "Groupe 2: Cadres moyens et employés",
                                          "Groupe 3: Inactifs (retraités, rentiers)",
                                          "Groupe 4: Exploitants agricoles et ouvriers agricoles",
                                          "Groupe 5: Artisans et ouvriers qualifiés",
                                          "Groupe 6: Manœuvres et petits métiers"])
        
        # Encodage de la catégorie socioprofessionnelle
        categorie_socioprofessionnelle_encoded = int(categorie_sociopro[7]) - 1
        
        a_retraite = st.checkbox("Bénéficie d'une retraite")
        aide_sociale = st.checkbox("Bénéficie d'une aide sociale")
        a_acces_credit = st.checkbox("A accès au crédit")

    with col3:
        st.subheader("Patrimoine et région")
        possede_voiture = st.checkbox("Possède une voiture")
        possede_logement = st.checkbox("Possède un logement")
        possede_terrain = st.checkbox("Possède un terrain")
        
        region = st.selectbox("Région", 
                             ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Fès-Meknès", 
                              "Marrakech-Safi", "Tanger-Tétouan-Al Hoceïma", "L'Oriental",
                              "Souss-Massa", "Drâa-Tafilalet", "Béni Mellal-Khénifra",
                              "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"])
        
        # One-hot encoding pour la région
        regions = ["Casablanca-Settat", "Dakhla-Oued Ed-Dahab", "Drâa-Tafilalet", 
                   "Fès-Meknès", "Guelmim-Oued Noun", "L'Oriental", 
                   "Laâyoune-Sakia El Hamra", "Marrakech-Safi", 
                   "Rabat-Salé-Kénitra", "Souss-Massa", "Tanger-Tétouan-Al Hoceïma"]
        
        region_encoded = {f"region_{r.replace('-', '_').replace(' ', '_').replace('\'', '_')}": (region == r) for r in regions}

    # Bouton pour lancer la prédiction
    if st.button("Prédire le revenu annuel"):
        # Préparation des données pour l'API
        input_data = {
            # Variables numériques
            "age": float(age),
            "taille_foyer": float(taille_foyer),
            "aide_sociale": float(aide_sociale),
            "a_acces_credit": float(a_acces_credit),
            "a_retraite": float(a_retraite),
            "possede_voiture": float(possede_voiture),
            "possede_logement": float(possede_logement),
            "possede_terrain": float(possede_terrain),
            "annees_experience": float(annees_experience),
            
            # Variables catégorielles encodées
            "niveau_education_encoded": niveau_education_encoded,
            "categorie_socioprofessionnelle_encoded": categorie_socioprofessionnelle_encoded,
            "categorie_age_encoded": categorie_age_encoded,
            
            # Variables binaires
            "sexe_Homme": sexe_Homme,
            "milieu_Urbain": milieu_Urbain,
            
            # État matrimonial (one-hot encoding)
            "etat_matrimonial_Divorcé": etat_matrimonial_Divorcé,
            "etat_matrimonial_Marié": etat_matrimonial_Marié,
            "etat_matrimonial_Veuf": etat_matrimonial_Veuf,
            
            # Région (one-hot encoding)
            "region_Casablanca_Settat": region == "Casablanca-Settat",
            "region_Dakhla_Oued_Ed_Dahab": region == "Dakhla-Oued Ed-Dahab",
            "region_Drâa_Tafilalet": region == "Drâa-Tafilalet",
            "region_Fès_Meknès": region == "Fès-Meknès",
            "region_Guelmim_Oued_Noun": region == "Guelmim-Oued Noun",
            "region_L_Oriental": region == "L'Oriental",
            "region_Laâyoune_Sakia_El_Hamra": region == "Laâyoune-Sakia El Hamra",
            "region_Marrakech_Safi": region == "Marrakech-Safi",
            "region_Rabat_Salé_Kénitra": region == "Rabat-Salé-Kénitra",
            "region_Souss_Massa": region == "Souss-Massa",
            "region_Tanger_Tétouan_Al_Hoceïma": region == "Tanger-Tétouan-Al Hoceïma"
        }
        
        # Appel à l'API pour la prédiction
        with st.spinner("Calcul en cours..."):
            predicted_income = predict_income(input_data)
        
        if predicted_income is not None:
            # Affichage du résultat
            st.success(f"Revenu annuel prédit: {predicted_income:.2f} DH")
            
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
                'Revenu annuel (DH)': [predicted_income, revenu_moyen_national, 
                                      revenu_moyen_urbain if milieu == "Urbain" else revenu_moyen_rural]
            })
            
            # Création du graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='Catégorie', y='Revenu annuel (DH)', data=comparison_data, ax=ax)
            ax.set_title('Comparaison du revenu prédit avec les moyennes nationales')
            ax.set_ylabel('Revenu annuel (DH)')
            ax.set_xlabel('')
            
            # Affichage du graphique dans Streamlit
            st.pyplot(fig)
            
            # Interprétation du résultat
            if predicted_income > revenu_moyen_national:
                st.info(f"Le revenu prédit est supérieur à la moyenne nationale de {predicted_income - revenu_moyen_national:.2f} DH.")
            else:
                st.info(f"Le revenu prédit est inférieur à la moyenne nationale de {revenu_moyen_national - predicted_income:.2f} DH.")
            
            # Calcul du revenu par personne
            revenu_par_personne = predicted_income / taille_foyer
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

# Navigation entre les pages
def navigation():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Aller à", ["Prédiction individuelle", "Prédiction par lot"])
    
    if page == "Prédiction individuelle":
        main_page()
    else:
        batch_prediction_page()

# Pied de page
def footer():
    st.markdown("---")
    st.markdown("Mini-projet Intelligence Artificielle - 2ème année Cycle d'ingénieurs GI")

# Exécution de l'application
if __name__ == "__main__":
    navigation()
    footer()