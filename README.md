# Prédiction du Revenu Annuel des Marocains

Ce projet implémente un modèle de machine learning pour prédire le revenu annuel d’un marocain en fonction de ses caractéristiques socio-démographiques.

## Sommaire

- [Structure du projet](#structure-du-projet)
- [Technologies utilisées](#technologies-utilisées)
- [Méthodologie](#méthodologie)
- [Résultats](#résultats)
- [Installation et exécution](#installation-et-exécution)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Auteurs](#auteurs)

---

## Structure du projet

- `generate_dataset.py` : Script pour générer le jeu de données simulé  
- `dataset_revenu_marocains.csv` : Jeu de données généré  
- `mini_projet_AI_Aazibou_Ait_Brahim_Skeli.ipynb` : Notebook contenant l’analyse exploratoire et la modélisation  
- `modele_selection.joblib` : Modèle sauvegardé après entraînement  
- `api.py` : API REST développée avec FastAPI pour exposer le modèle  
- `app.py` : Application web développée avec Streamlit pour interagir avec le modèle  

---

## Technologies utilisées

- **Langage** : Python 3.x  
- **Manipulation des données** : Pandas, NumPy  
- **Visualisation** : Matplotlib, Seaborn, Sweetviz  
- **Machine Learning** : Scikit-learn  
- **Déploiement** : FastAPI, Streamlit  

---

## Méthodologie

Le projet suit les étapes classiques d’un processus de Data Science :

1. **Compréhension des données**
   - Analyse exploratoire
   - Statistiques descriptives
   - Visualisation des distributions et corrélations

2. **Préparation des données**
   - Traitement des valeurs manquantes
   - Détection et gestion des valeurs aberrantes (Isolation Forest)
   - Suppression des attributs non pertinents
   - Création de nouvelles caractéristiques

3. **Modélisation**
   - Entraînement de 5 algorithmes de régression :
     - Régression Linéaire
     - Arbre de Décision
     - Forêt Aléatoire
     - Gradient Boosting
     - Réseau de Neurones (MLP)
   - Optimisation des hyperparamètres avec GridSearchCV et RandomizedSearchCV
   - Validation croisée à 5 plis

4. **Évaluation**
   - Métriques utilisées : MAE, RMSE, R²
   - Analyse des résidus
   - Visualisation des prédictions vs valeurs réelles

5. **Déploiement**
   - API REST avec FastAPI
   - Interface utilisateur avec Streamlit

---

## Résultats

Le modèle de **Forêt Aléatoire** a obtenu les meilleures performances avec :

- **MAE** : 3425.15  
- **RMSE** : 16050.43  
- **R²** : 0.8692  

---

## Installation et exécution

### Prérequis

- Python 3.8 ou plus récent
- `pip` installé

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement du notebook (facultatif)

```bash
jupyter notebook mini_projet_AI_Aazibou_Ait_Brahim_Skeli.ipynb
```

### Lancement de l’API

```bash
uvicorn api:app --reload
```

### Lancement de l’application Streamlit

```bash
streamlit run app.py
```

---

## Utilisation de l’API

L’API expose un endpoint `/predict` qui accepte une requête POST contenant les caractéristiques d’un individu et retourne la prédiction de son revenu annuel.

### Exemple de requête JSON

```json
{
  "age": 35,
  "sexe": "Homme",
  "milieu": "Urbain",
  "etat_matrimonial": "Marié",
  "region": "Casablanca-Settat",
  "niveau_education": "Supérieur",
  "categorie_socioprofessionnelle": "Groupe 2",
  "taille_foyer": 4,
  "aide_sociale": 0,
  "a_acces_credit": 1,
  "a_retraite": 0,
  "possede_voiture": 1,
  "possede_logement": 1,
  "possede_terrain": 0,
  "annees_experience": 10,
  "niveau_socioeco": 2,
  "est_urbain": 1,
  "est_marie": 1
}
```

---

## Auteurs

- **AAZIBOU Douae**  
- **AIT BRAHIM Lina**  
- **SKELI Mouna**

---

## Licence

## Licence

Ce projet a été réalisé dans le cadre du module d’**Intelligence Artificielle** à l’**École Nationale des Sciences Appliquées de Tétouan** (ENSATé), sous la supervision de **M. Y. El Younoussi**.  
Il est destiné exclusivement à un usage pédagogique et académique.

