import streamlit as st
import pandas as pd
import requests
import io
import base64

def batch_prediction_page():
    st.title("Prédiction par lot")
    st.markdown("Téléchargez un fichier CSV contenant plusieurs individus pour prédire leur revenu annuel en une seule fois.")
    
    # Téléchargement du modèle de fichier CSV
    st.subheader("Modèle de fichier CSV")
    
    # Créer un exemple de fichier CSV
    example_data = {
        "age": [30, 45, 60],
        "taille_foyer": [3, 4, 2],
        "aide_sociale": [0, 1, 0],
        "a_acces_credit": [1, 0, 1],
        "a_retraite": [0, 0, 1],
        "possede_voiture": [1, 0, 1],
        "possede_logement": [0, 1, 1],
        "possede_terrain": [0, 0, 1],
        "annees_experience": [5, 20, 35],
        "niveau_education_encoded": [2, 1, 3],
        "categorie_socioprofessionnelle_encoded": [1, 3, 0],
        "categorie_age_encoded": [0, 1, 2],
        "sexe_Homme": [1, 0, 1],
        "milieu_Urbain": [1, 0, 1],
        "etat_matrimonial_Divorcé": [0, 1, 0],
        "etat_matrimonial_Marié": [1, 0, 0],
        "etat_matrimonial_Veuf": [0, 0, 1],
        "region_Casablanca_Settat": [1, 0, 0],
        "region_Dakhla_Oued_Ed_Dahab": [0, 0, 0],
        "region_Drâa_Tafilalet": [0, 0, 0],
        "region_Fès_Meknès": [0, 0, 0],
        "region_Guelmim_Oued_Noun": [0, 0, 0],
        "region_L_Oriental": [0, 0, 0],
        "region_Laâyoune_Sakia_El_Hamra": [0, 0, 0],
        "region_Marrakech_Safi": [0, 0, 0],
        "region_Rabat_Salé_Kénitra": [0, 1, 0],
        "region_Souss_Massa": [0, 0, 0],
        "region_Tanger_Tétouan_Al_Hoceïma": [0, 0, 1]
    }
    
    example_df = pd.DataFrame(example_data)
    
    # Convertir le DataFrame en CSV
    csv = example_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="modele_prediction_lot.csv">Télécharger le modèle de fichier CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Téléchargement du fichier CSV par l'utilisateur
    st.subheader("Téléchargez votre fichier CSV")
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            # Lire le fichier CSV
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu des données:")
            st.write(df.head())
            
            # Vérifier que toutes les colonnes nécessaires sont présentes
            required_columns = set(example_data.keys())
            if not required_columns.issubset(set(df.columns)):
                missing_columns = required_columns - set(df.columns)
                st.error(f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}")
                return
            
            # Bouton pour lancer la prédiction par lot
            if st.button("Lancer la prédiction par lot"):
                with st.spinner("Prédiction en cours..."):
                    # Préparer les résultats
                    results = []
                    
                    # Pour chaque ligne du DataFrame
                    for _, row in df.iterrows():
                        # Préparer les données pour l'API
                        input_data = {col: float(row[col]) if col in ["age", "taille_foyer", "aide_sociale", "a_acces_credit", 
                                                                     "a_retraite", "possede_voiture", "possede_logement", 
                                                                     "possede_terrain", "annees_experience"] 
                                     else int(row[col]) if col in ["niveau_education_encoded", "categorie_socioprofessionnelle_encoded", 
                                                                  "categorie_age_encoded"]
                                     else bool(row[col]) for col in row.index}
                        
                        # Appeler l'API
                        try:
                            response = requests.post("http://localhost:8000/predict", json=input_data)
                            if response.status_code == 200:
                                revenu_predit = response.json()["revenu_predit"]
                                results.append({"revenu_predit": revenu_predit})
                            else:
                                results.append({"revenu_predit": "Erreur"})
                        except Exception as e:
                            results.append({"revenu_predit": f"Erreur: {str(e)}"})
                    
                    # Ajouter les résultats au DataFrame
                    results_df = pd.DataFrame(results)
                    df_with_results = pd.concat([df, results_df], axis=1)
                    
                    # Afficher les résultats
                    st.subheader("Résultats de la prédiction")
                    st.write(df_with_results)
                    
                    # Téléchargement des résultats
                    csv_results = df_with_results.to_csv(index=False)
                    b64_results = base64.b64encode(csv_results.encode()).decode()
                    href_results = f'<a href="data:file/csv;base64,{b64_results}" download="resultats_prediction.csv">Télécharger les résultats</a>'
                    st.markdown(href_results, unsafe_allow_html=True)
                    
                    # Statistiques sur les résultats
                    st.subheader("Statistiques sur les résultats")
                    
                    # Vérifier si toutes les prédictions sont numériques
                    numeric_results = df_with_results[df_with_results["revenu_predit"] != "Erreur"]
                    if not numeric_results.empty:
                        numeric_results["revenu_predit"] = pd.to_numeric(numeric_results["revenu_predit"])
                        
                        # Statistiques descriptives
                        st.write("Statistiques descriptives:")
                        st.write(numeric_results["revenu_predit"].describe())
                        
                        # Histogramme des revenus prédits
                        st.write("Distribution des revenus prédits:")
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.histplot(numeric_results["revenu_predit"], kde=True, ax=ax)
                        ax.set_title("Distribution des revenus prédits")
                        ax.set_xlabel("Revenu annuel prédit (DH)")
                        ax.set_ylabel("Fréquence")
                        st.pyplot(fig)
                        
                        # Comparaison avec les moyennes nationales
                        st.write("Comparaison avec les moyennes nationales:")
                        revenu_moyen_national = 21949
                        revenu_moyen_urbain = 26988
                        revenu_moyen_rural = 12862
                        
                        # Calculer les moyennes par milieu
                        urbain_results = numeric_results[numeric_results["milieu_Urbain"] == 1]
                        rural_results = numeric_results[numeric_results["milieu_Urbain"] == 0]
                        
                        urbain_mean = urbain_results["revenu_predit"].mean() if not urbain_results.empty else 0
                        rural_mean = rural_results["revenu_predit"].mean() if not rural_results.empty else 0
                        
                        comparison_data = pd.DataFrame({
                            'Catégorie': ['Prédiction (moyenne)', 'Prédiction (urbain)', 'Prédiction (rural)',
                                         'Moyenne nationale', 'Moyenne urbaine', 'Moyenne rurale'],
                            'Revenu annuel (DH)': [numeric_results["revenu_predit"].mean(), urbain_mean, rural_mean,
                                                  revenu_moyen_national, revenu_moyen_urbain, revenu_moyen_rural]
                        })
                        
                        fig, ax = plt.subplots(figsize=(12, 6))
                        sns.barplot(x='Catégorie', y='Revenu annuel (DH)', data=comparison_data, ax=ax)
                        ax.set_title('Comparaison des revenus prédits avec les moyennes nationales')
                        ax.set_ylabel('Revenu annuel (DH)')
                        ax.set_xlabel('')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
        
        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier: {str(e)}")

# Ajouter cette fonction à votre application principale
if __name__ == "__main__":
    batch_prediction_page()