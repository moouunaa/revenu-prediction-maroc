from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from typing import List, Optional
import pandas as pd

# Charger le modèle sauvegardé
try:
    model = joblib.load("modele_selection.joblib")
    print("Modèle chargé avec succès!")
except Exception as e:
    print(f"Erreur lors du chargement du modèle: {e}")
    model = None

# Créer l'application FastAPI
app = FastAPI(title="API de Prédiction du Revenu Annuel",
              description="API pour prédire le revenu annuel d'un marocain")

# Définir le modèle de données d'entrée
class PredictionInput(BaseModel):
    # Variables numériques
    age: float
    taille_foyer: float
    aide_sociale: float  # Probablement 0 ou 1
    a_acces_credit: float  # Probablement 0 ou 1
    a_retraite: float  # Probablement 0 ou 1
    possede_voiture: float  # Probablement 0 ou 1
    possede_logement: float  # Probablement 0 ou 1
    possede_terrain: float  # Probablement 0 ou 1
    annees_experience: float
    
    # Variables catégorielles encodées
    niveau_education_encoded: int
    categorie_socioprofessionnelle_encoded: int
    categorie_age_encoded: int
    
    # Variables binaires
    sexe_Homme: bool
    milieu_Urbain: bool
    
    # État matrimonial (one-hot encoding)
    etat_matrimonial_Divorcé: bool
    etat_matrimonial_Marié: bool
    etat_matrimonial_Veuf: bool
    
    # Région (one-hot encoding)
    region_Casablanca_Settat: bool
    region_Dakhla_Oued_Ed_Dahab: bool
    region_Drâa_Tafilalet: bool
    region_Fès_Meknès: bool
    region_Guelmim_Oued_Noun: bool
    region_L_Oriental: bool
    region_Laâyoune_Sakia_El_Hamra: bool
    region_Marrakech_Safi: bool
    region_Rabat_Salé_Kénitra: bool
    region_Souss_Massa: bool
    region_Tanger_Tétouan_Al_Hoceïma: bool

# Définir le modèle de données de sortie
class PredictionOutput(BaseModel):
    revenu_predit: float

# Endpoint pour la prédiction
@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'a pas pu être chargé")
    
    # Calculer les caractéristiques dérivées
    ratio_possessions = (input_data.possede_voiture + input_data.possede_logement + input_data.possede_terrain) / 3
    ratio_experience_age = input_data.annees_experience / input_data.age if input_data.age > 0 else 0
    
    # Nous ne pouvons pas calculer revenu_par_personne car nous ne connaissons pas encore le revenu
    # Nous utiliserons indice_stabilite comme une valeur fixe pour cet exemple
    indice_stabilite = 0.5  # Valeur par défaut, à ajuster selon votre logique métier
    
    # Créer le vecteur de caractéristiques dans le même ordre que votre DataFrame
    features = [
        input_data.age,
        input_data.taille_foyer,
        input_data.aide_sociale,
        input_data.a_acces_credit,
        input_data.a_retraite,
        input_data.possede_voiture,
        input_data.possede_logement,
        input_data.possede_terrain,
        input_data.annees_experience,
        # revenu_annuel est la variable cible, donc pas incluse ici
        ratio_possessions,
        indice_stabilite,
        ratio_experience_age,
        0,  # revenu_par_personne (sera ignoré par le modèle ou remplacé par une valeur par défaut)
        input_data.niveau_education_encoded,
        input_data.categorie_socioprofessionnelle_encoded,
        input_data.categorie_age_encoded,
        input_data.sexe_Homme,
        input_data.milieu_Urbain,
        input_data.etat_matrimonial_Divorcé,
        input_data.etat_matrimonial_Marié,
        input_data.etat_matrimonial_Veuf,
        input_data.region_Casablanca_Settat,
        input_data.region_Dakhla_Oued_Ed_Dahab,
        input_data.region_Drâa_Tafilalet,
        input_data.region_Fès_Meknès,
        input_data.region_Guelmim_Oued_Noun,
        input_data.region_L_Oriental,
        input_data.region_Laâyoune_Sakia_El_Hamra,
        input_data.region_Marrakech_Safi,
        input_data.region_Rabat_Salé_Kénitra,
        input_data.region_Souss_Massa,
        input_data.region_Tanger_Tétouan_Al_Hoceïma
    ]
    
    # Faire la prédiction
    try:
        # Convertir les booléens en entiers (0 ou 1)
        features_numeric = [float(f) if isinstance(f, bool) else f for f in features]
        
        # Créer un DataFrame avec les features
        feature_names = [
            'age', 'taille_foyer', 'aide_sociale', 'a_acces_credit', 'a_retraite',
            'possede_voiture', 'possede_logement', 'possede_terrain', 'annees_experience',
            'ratio_possessions', 'indice_stabilite', 'ratio_experience_age', 'revenu_par_personne',
            'niveau_education_encoded', 'categorie_socioprofessionnelle_encoded', 'categorie_age_encoded',
            'sexe_Homme', 'milieu_Urbain', 'etat_matrimonial_Divorcé', 'etat_matrimonial_Marié',
            'etat_matrimonial_Veuf', 'region_Casablanca-Settat', 'region_Dakhla-Oued Ed-Dahab',
            'region_Drâa-Tafilalet', 'region_Fès-Meknès', 'region_Guelmim-Oued Noun',
            "region_L'Oriental", 'region_Laâyoune-Sakia El Hamra', 'region_Marrakech-Safi',
            'region_Rabat-Salé-Kénitra', 'region_Souss-Massa', 'region_Tanger-Tétouan-Al Hoceïma'
        ]
        df = pd.DataFrame([features_numeric], columns=feature_names)
        
        # Faire la prédiction avec le DataFrame
        prediction = model.predict(df)[0]
        
        return PredictionOutput(revenu_predit=float(prediction))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

# Endpoint pour vérifier que l'API fonctionne
@app.get("/")
def read_root():
    return {"message": "API de prédiction du revenu annuel d'un marocain"}

# Pour lancer l'API: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)