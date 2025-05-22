from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
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
    age: int
    taille_foyer: float
    aide_sociale: int
    a_acces_credit: int
    a_retraite: int
    possede_voiture: float
    possede_logement: float
    possede_terrain: int
    annees_experience: float
    est_urbain: int
    est_marie: int
    weight: float = 1.0
    
    # Variables catégorielles
    sexe: str
    milieu: str
    etat_matrimonial: str
    region: str
    niveau_education: str
    categorie_socioprofessionnelle: str
    
    # Variables dérivées
    revenu_par_experience: float = 0.0
    niveau_socioeco: float = 0.0

# Définir le modèle de données de sortie
class PredictionOutput(BaseModel):
    revenu_predit: float
    message: str

# Endpoint pour la prédiction
@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'a pas pu être chargé")
    
    try:
        # Créer un DataFrame avec une ligne pour la prédiction
        data = {
            'age': input_data.age,
            'sexe': input_data.sexe,
            'milieu': input_data.milieu,
            'etat_matrimonial': input_data.etat_matrimonial,
            'region': input_data.region,
            'niveau_education': input_data.niveau_education,
            'categorie_socioprofessionnelle': input_data.categorie_socioprofessionnelle,
            'taille_foyer': input_data.taille_foyer,
            'aide_sociale': input_data.aide_sociale,
            'a_acces_credit': input_data.a_acces_credit,
            'a_retraite': input_data.a_retraite,
            'possede_voiture': input_data.possede_voiture,
            'possede_logement': input_data.possede_logement,
            'possede_terrain': input_data.possede_terrain,
            'annees_experience': input_data.annees_experience,
            'revenu_par_experience': input_data.revenu_par_experience,
            'niveau_socioeco': input_data.niveau_socioeco,
            'est_urbain': input_data.est_urbain,
            'est_marie': input_data.est_marie,
            'weight': input_data.weight
        }
        
        # Créer le DataFrame
        df = pd.DataFrame([data])
        
        # Afficher les colonnes pour le débogage
        print(f"Colonnes du DataFrame: {df.columns.tolist()}")
        
        # Faire la prédiction
        prediction = model.predict(df)[0]
        
        # Préparer le message de retour
        message = f"Le revenu annuel prédit est de {prediction:.2f} DH."
        
        return PredictionOutput(revenu_predit=float(prediction), message=message)
    
    except Exception as e:
        print(f"Erreur détaillée: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

# Endpoint pour vérifier que l'API fonctionne
@app.get("/")
def read_root():
    return {"message": "API de prédiction du revenu annuel d'un marocain"}

# Pour lancer l'API: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)