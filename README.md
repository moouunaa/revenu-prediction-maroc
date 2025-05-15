# Prédiction du Revenu Annuel d'un Marocain

Ce projet implémente un modèle de machine learning pour prédire le revenu annuel d'un Marocain en fonction de ses caractéristiques socio-démographiques.

## Structure du projet

- `generate_dataset.py`: Script pour générer le dataset simulé
- `dataset_revenu_marocains.csv`: Dataset généré
- `mini_projet_AI_Noms.ipynb`: Notebook contenant l'analyse et la modélisation
- `modele_selection.joblib`: Modèle sauvegardé
- `api.py`: API FastAPI pour exposer le modèle
- `app.py`: Application web Streamlit pour interagir avec le modèle

## Installation

1. Clonez ce dépôt
2. Installez les dépendances:

```bash
pip install -r requirements.txt