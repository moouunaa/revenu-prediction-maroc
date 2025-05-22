import numpy as np
import pandas as pd
from datetime import datetime
import random

# Définir un seed pour la reproductibilité
np.random.seed(42)
random.seed(42)

# Nombre d'enregistrements
n_samples = 40000

# Définir les régions du Maroc
regions = [
    "Tanger-Tétouan-Al Hoceïma", "L'Oriental", "Fès-Meknès", "Rabat-Salé-Kénitra",
    "Béni Mellal-Khénifra", "Casablanca-Settat", "Marrakech-Safi", "Drâa-Tafilalet",
    "Souss-Massa", "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"
]

# Probabilités pour chaque région (basées sur la population approximative)
region_probs = [
    0.11, 0.08, 0.13, 0.13, 0.07, 0.20, 0.13, 0.05, 0.07, 0.01, 0.01, 0.01
]

# Générer les données de base
data = {
    # Caractéristiques démographiques
    'age': np.random.randint(18, 80, n_samples),
    'sexe': np.random.choice(['Homme', 'Femme'], n_samples, p=[0.52, 0.48]),
    'milieu': np.random.choice(['Urbain', 'Rural'], n_samples, p=[0.63, 0.37]),
    'etat_matrimonial': np.random.choice(
        ['Célibataire', 'Marié', 'Divorcé', 'Veuf'], 
        n_samples, 
        p=[0.35, 0.55, 0.07, 0.03]
    ),
    'region': np.random.choice(regions, n_samples, p=region_probs),
    
    # Caractéristiques socio-économiques
    'niveau_education': np.random.choice(
        ['Sans niveau', 'Fondamental', 'Secondaire', 'Supérieur'], 
        n_samples, 
        p=[0.25, 0.35, 0.25, 0.15]
    ),
    'categorie_socioprofessionnelle': np.random.choice(
        ['Groupe 1', 'Groupe 2', 'Groupe 3', 'Groupe 4', 'Groupe 5', 'Groupe 6'], 
        n_samples, 
        p=[0.05, 0.15, 0.20, 0.20, 0.25, 0.15]
    ),
    
    # Caractéristiques additionnelles choisies
    'taille_foyer': np.random.randint(1, 10, n_samples),
    'aide_sociale': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    'a_acces_credit': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
    'a_retraite': np.zeros(n_samples, dtype=int),  # Sera mis à jour en fonction de l'âge
    
    # Possessions
    'possede_voiture': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    'possede_logement': np.random.choice([0, 1], n_samples, p=[0.4, 0.6]),
    'possede_terrain': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
}

# Créer le DataFrame
df = pd.DataFrame(data)

# Ajouter la catégorie d'âge
def categoriser_age(age):
    if age < 30:
        return 'Jeune'
    elif age < 50:
        return 'Adulte'
    elif age < 65:
        return 'Sénior'
    else:
        return 'Âgé'

df['categorie_age'] = df['age'].apply(categoriser_age)

# Calculer les années d'expérience en fonction de l'âge et du niveau d'éducation
def calculer_experience(row):
    age = row['age']
    education = row['niveau_education']
    
    if education == 'Sans niveau':
        debut_travail = 15
    elif education == 'Fondamental':
        debut_travail = 16
    elif education == 'Secondaire':
        debut_travail = 19
    else:  # Supérieur
        debut_travail = 23
    
    experience = max(0, age - debut_travail)
    # Ajouter une variabilité (certaines personnes peuvent avoir des périodes sans emploi)
    experience = max(0, experience - np.random.randint(0, 5))
    return experience

df['annees_experience'] = df.apply(calculer_experience, axis=1)

# Mettre à jour la retraite en fonction de l'âge
df.loc[df['age'] >= 60, 'a_retraite'] = 1

# Ajuster l'accès au crédit en fonction du revenu et de la stabilité financière
def ajuster_acces_credit(row):
    if row['categorie_socioprofessionnelle'] in ['Groupe 1', 'Groupe 2']:
        return np.random.choice([0, 1], p=[0.2, 0.8])
    elif row['categorie_socioprofessionnelle'] in ['Groupe 3', 'Groupe 4']:
        return np.random.choice([0, 1], p=[0.5, 0.5])
    else:
        return np.random.choice([0, 1], p=[0.8, 0.2])

df['a_acces_credit'] = df.apply(ajuster_acces_credit, axis=1)

# Générer le revenu en fonction des caractéristiques
def generer_revenu(row):
    # Base income with stronger feature dependence
    base_revenu = 4000 + (row['annees_experience'] * 800)  # Experience matters more
    
    # Education multipliers (wider gaps)
    education_multiplier = {
        'Sans niveau': 0.4,
        'Fondamental': 0.7,
        'Secondaire': 1.5,
        'Supérieur': 3.0  # University graduates earn significantly more
    }[row['niveau_education']]
    
    # Socio-professional group multipliers (starker differences)
    socio_multiplier = {
        'Groupe 1': 4.0,  # High-income professionals
        'Groupe 2': 2.0,
        'Groupe 3': 1.2,
        'Groupe 4': 0.8,
        'Groupe 5': 0.6,
        'Groupe 6': 0.4   # Unemployed/Manual laborers
    }[row['categorie_socioprofessionnelle']]
    
    # Interaction: Urban + Higher education = bonus
    urban_edu_bonus = 1.5 if (row['milieu'] == 'Urbain' and row['niveau_education'] == 'Supérieur') else 1.0
    
    # Combine factors with less noise
    revenu = base_revenu * education_multiplier * socio_multiplier * urban_edu_bonus
    revenu *= np.random.normal(1, 0.1)  # Reduced noise
    
    return max(1000, int(round(revenu)))







df['revenu_annuel'] = df.apply(generer_revenu, axis=1)

# Ajouter des colonnes redondantes
df['age_en_mois'] = df['age'] * 12
df['est_urbain'] = df['milieu'].apply(lambda x: 1 if x == 'Urbain' else 0)
df['est_marie'] = df['etat_matrimonial'].apply(lambda x: 1 if x == 'Marié' else 0)

# Ajouter des colonnes non pertinentes
df['id_utilisateur'] = np.arange(1, n_samples + 1)
df['date_enregistrement'] = [datetime.now().strftime('%Y-%m-%d') for _ in range(n_samples)]
df['code_postal'] = np.random.randint(10000, 99999, n_samples)

# Ajouter des valeurs manquantes
for col in ['niveau_education', 'annees_experience', 'taille_foyer', 'possede_voiture', 'possede_logement']:
    mask = np.random.choice([True, False], n_samples, p=[0.05, 0.95])
    df.loc[mask, col] = np.nan

# Ajouter des valeurs aberrantes
# Âge aberrant
aberrant_indices = np.random.choice(n_samples, int(n_samples * 0.01), replace=False)
df.loc[aberrant_indices, 'age'] = np.random.randint(100, 120, len(aberrant_indices))

# Revenu aberrant
aberrant_indices = np.random.choice(n_samples, int(n_samples * 0.01), replace=False)
df.loc[aberrant_indices, 'revenu_annuel'] = np.random.randint(300000, 1000000, len(aberrant_indices))

# Calculer les statistiques actuelles
urbain_mean = df[df['milieu'] == 'Urbain']['revenu_annuel'].mean()
rural_mean = df[df['milieu'] == 'Rural']['revenu_annuel'].mean()
overall_mean = df['revenu_annuel'].mean()

# Calculer les facteurs d'ajustement pour atteindre les cibles
target_overall = 21949
target_urbain = 26988
target_rural = 12862

adjustment_urbain = target_urbain / urbain_mean
adjustment_rural = target_rural / rural_mean

# Appliquer les ajustements (avec conversion explicite en int)
df.loc[df['milieu'] == 'Urbain', 'revenu_annuel'] = (df.loc[df['milieu'] == 'Urbain', 'revenu_annuel'] * adjustment_urbain).astype(int)
df.loc[df['milieu'] == 'Rural', 'revenu_annuel'] = (df.loc[df['milieu'] == 'Rural', 'revenu_annuel'] * adjustment_rural).astype(int)

# Vérifier les statistiques après ajustement
urbain_mean_adj = df[df['milieu'] == 'Urbain']['revenu_annuel'].mean()
rural_mean_adj = df[df['milieu'] == 'Rural']['revenu_annuel'].mean()
overall_mean_adj = df['revenu_annuel'].mean()

# Fonction pour ajuster la distribution pour atteindre les pourcentages cibles sous la moyenne
def ajuster_distribution_skew(df_subset, target_pct_below_mean, mean_value, iterations=5):
    """
    Ajuste la distribution pour atteindre le pourcentage cible sous la moyenne
    en modifiant progressivement la forme de la distribution.
    """
    current_pct = (df_subset['revenu_annuel'] < mean_value).mean() * 100
    
    # Si déjà proche de la cible, ne rien faire
    if abs(current_pct - target_pct_below_mean) < 1.0:
        return df_subset
    
    # Déterminer si nous devons augmenter ou diminuer le pourcentage sous la moyenne
    need_increase = current_pct < target_pct_below_mean
    
    for _ in range(iterations):
        # Calculer le pourcentage actuel sous la moyenne
        current_pct = (df_subset['revenu_annuel'] < mean_value).mean() * 100
        
        if abs(current_pct - target_pct_below_mean) < 1.0:
            break  # Assez proche de la cible
        
        if need_increase:
            # Nous devons augmenter le pourcentage sous la moyenne
            # Identifier les revenus juste au-dessus de la moyenne
            just_above = df_subset[(df_subset['revenu_annuel'] >= mean_value) & 
                                  (df_subset['revenu_annuel'] < mean_value * 1.2)]
            
            if len(just_above) > 0:
                # Calculer combien d'observations doivent être déplacées
                n_to_move = int(len(df_subset) * (target_pct_below_mean - current_pct) / 100)
                n_to_move = min(n_to_move, len(just_above))
                
                if n_to_move > 0:
                    # Sélectionner les observations à déplacer
                    to_move = just_above.sample(n=n_to_move)
                    
                    # Réduire ces revenus pour qu'ils soient sous la moyenne
                    factor = 0.85  # Réduction de 15%
                    df_subset.loc[to_move.index, 'revenu_annuel'] = (df_subset.loc[to_move.index, 'revenu_annuel'] * factor).astype(int)
        else:
            # Nous devons diminuer le pourcentage sous la moyenne
            # Identifier les revenus juste en-dessous de la moyenne
            just_below = df_subset[(df_subset['revenu_annuel'] < mean_value) & 
                                  (df_subset['revenu_annuel'] > mean_value * 0.8)]
            
            if len(just_below) > 0:
                # Calculer combien d'observations doivent être déplacées
                n_to_move = int(len(df_subset) * (current_pct - target_pct_below_mean) / 100)
                n_to_move = min(n_to_move, len(just_below))
                
                if n_to_move > 0:
                    # Sélectionner les observations à déplacer
                    to_move = just_below.sample(n=n_to_move)
                    
                    # Augmenter ces revenus pour qu'ils soient au-dessus de la moyenne
                    factor = 1.2  # Augmentation de 20%
                    df_subset.loc[to_move.index, 'revenu_annuel'] = (df_subset.loc[to_move.index, 'revenu_annuel'] * factor).astype(int)
    
    return df_subset

# Définir les pourcentages cibles
target_pct_below_mean = 71.8
target_pct_below_mean_urbain = 65.9
target_pct_below_mean_rural = 85.4

# Appliquer les ajustements de distribution
df_urbain = df[df['milieu'] == 'Urbain'].copy()
df_rural = df[df['milieu'] == 'Rural'].copy()

df_urbain = ajuster_distribution_skew(df_urbain, target_pct_below_mean_urbain, urbain_mean_adj, iterations=10)
df_rural = ajuster_distribution_skew(df_rural, target_pct_below_mean_rural, rural_mean_adj, iterations=10)

# Recombiner les dataframes
df = pd.concat([df_urbain, df_rural])

# Vérifier les statistiques finales
urbain_mean_final = df[df['milieu'] == 'Urbain']['revenu_annuel'].mean()
rural_mean_final = df[df['milieu'] == 'Rural']['revenu_annuel'].mean()
overall_mean_final = df['revenu_annuel'].mean()

# Ajuster à nouveau pour atteindre exactement les moyennes cibles
adjustment_urbain_final = target_urbain / urbain_mean_final
adjustment_rural_final = target_rural / rural_mean_final

df.loc[df['milieu'] == 'Urbain', 'revenu_annuel'] = (df.loc[df['milieu'] == 'Urbain', 'revenu_annuel'] * adjustment_urbain_final).astype(int)
df.loc[df['milieu'] == 'Rural', 'revenu_annuel'] = (df.loc[df['milieu'] == 'Rural', 'revenu_annuel'] * adjustment_rural_final).astype(int)

# Recalculer les statistiques finales
urbain_mean_final = df[df['milieu'] == 'Urbain']['revenu_annuel'].mean()
rural_mean_final = df[df['milieu'] == 'Rural']['revenu_annuel'].mean()
overall_mean_final = df['revenu_annuel'].mean()

pct_below_mean_final = (df['revenu_annuel'] < overall_mean_final).mean() * 100
pct_below_mean_urbain_final = (df[df['milieu'] == 'Urbain']['revenu_annuel'] < urbain_mean_final).mean() * 100
pct_below_mean_rural_final = (df[df['milieu'] == 'Rural']['revenu_annuel'] < rural_mean_final).mean() * 100

print(f"Revenu moyen global: {overall_mean_final:.2f} DH/an (Cible: {target_overall} DH/an)")
print(f"Revenu moyen urbain: {urbain_mean_final:.2f} DH/an (Cible: {target_urbain} DH/an)")
print(f"Revenu moyen rural: {rural_mean_final:.2f} DH/an (Cible: {target_rural} DH/an)")
print(f"Pourcentage global sous la moyenne: {pct_below_mean_final:.1f}% (Cible: {target_pct_below_mean}%)")
print(f"Pourcentage urbain sous la moyenne: {pct_below_mean_urbain_final:.1f}% (Cible: {target_pct_below_mean_urbain}%)")
print(f"Pourcentage rural sous la moyenne: {pct_below_mean_rural_final:.1f}% (Cible: {target_pct_below_mean_rural}%)")

# Sauvegarder le dataset
df.to_csv('dataset_revenu_marocains.csv', index=False, encoding='utf-8')
print(f"Dataset généré et sauvegardé avec {n_samples} enregistrements.")

# Afficher un aperçu du dataset
print("\nAperçu du dataset:")
print(df.head())

# Afficher les statistiques descriptives
print("\nStatistiques descriptives du revenu annuel:")
print(df['revenu_annuel'].describe())