# 🏠 House Price Prediction — Pipeline ML sur Snowflake

> **Workshop Data Engineering & Machine Learning | MBA ESG**  
> Pipeline end-to-end de prédiction de prix immobiliers, entièrement construit dans Snowflake.

---

## 👥 Équipe

| Membre | Rôle |
|--------|------|
| Membre 1 | Data Engineering (Ingestion, Feature Engineering) |
| Membre 2 | Machine Learning (Modèles, Optimisation) |
| Membre 3 | MLOps (Registry, Inférence, Streamlit) |

---

## 📁 Structure du Projet

```
MBAESG_[PROMOTION]_[CLASSE]_EVALUATION_DATAENGINEER_MLOPS/
│
├── README.md                          # Ce fichier
│
├── notebooks/
│   └── house_price_ml_pipeline.ipynb  # Pipeline ML complet (à importer dans Snowflake)
│
├── streamlit/
│   └── app.py                         # Application Streamlit (à déployer dans Snowflake)
│
├── sql/
│   └── setup.sql                      # Configuration initiale de l'environnement Snowflake
│
└── docs/
    └── architecture.md                # Description de l'architecture
```

---

## 🚀 Instructions de Déploiement

### Prérequis
- Un compte Snowflake actif (Trial ou payant)
- Un compte GitHub
- Rôle `ACCOUNTADMIN` sur Snowflake

### Étape 1 — Configurer l'environnement Snowflake

1. Connectez-vous à votre compte Snowflake
2. Ouvrez un **Worksheet** (onglet de requêtes SQL)
3. Copiez-collez le contenu de `sql/setup.sql` et exécutez-le **bloc par bloc**
4. Vérifiez que la commande `SELECT COUNT(*)` retourne ~545 lignes

### Étape 2 — Importer le Notebook

1. Dans Snowflake, allez dans **Projects > Notebooks**
2. Cliquez sur **+ Notebook**
3. Importez le fichier `notebooks/house_price_ml_pipeline.ipynb`
4. Sélectionnez :
   - **Database** : `HOUSE_PRICE_DB`
   - **Schema** : `ANALYTICS`
   - **Warehouse** : `HOUSE_PRICE_WH`
5. Exécutez les cellules **dans l'ordre**, de haut en bas

### Étape 3 — Déployer l'application Streamlit

1. Dans Snowflake, allez dans **Projects > Streamlit**
2. Cliquez sur **+ Streamlit App**
3. Nommez l'application : `HOUSE_PRICE_APP`
4. Sélectionnez `HOUSE_PRICE_DB.ML`
5. Copiez-collez le contenu de `streamlit/app.py`
6. Cliquez sur **Run**

---

## 📊 Dataset

**Source** : `s3://logbrain-datalake/datasets/house_price/`  
**Taille** : ~545 observations, 13 features

| Colonne | Type | Description |
|---------|------|-------------|
| `price` | Numérique | 🎯 Variable cible — Prix de vente (₹) |
| `area` | Numérique | Surface totale (m²) |
| `bedrooms` | Entier | Nombre de chambres |
| `bathrooms` | Entier | Nombre de salles de bain |
| `stories` | Entier | Nombre d'étages |
| `mainroad` | Binaire | Accès route principale (yes/no) |
| `guestroom` | Binaire | Chambre d'amis (yes/no) |
| `basement` | Binaire | Sous-sol (yes/no) |
| `hotwaterheating` | Binaire | Chauffe-eau (yes/no) |
| `airconditioning` | Binaire | Climatisation (yes/no) |
| `parking` | Entier | Places de stationnement (0-3) |
| `prefarea` | Binaire | Zone privilégiée (yes/no) |
| `furnishingstatus` | Catégoriel | furnished / semi-furnished / unfurnished |

---

## 🔍 Analyse Exploratoire — Résultats Clés

### Distribution du Prix

```
Min     :    1 750 000 ₹
Max     :   13 300 000 ₹
Moyenne :    4 766 729 ₹
Médiane :    4 340 000 ₹
Écart-type : 1 870 440 ₹
```

La distribution est **asymétrique à droite** (skewness positif), ce qui est typique des prix immobiliers. Quelques propriétés très chères tirent la moyenne vers le haut.

### Corrélations avec le Prix (Top 5)

| Feature | Corrélation | Interprétation |
|---------|-------------|----------------|
| `area` | **+0.54** | La surface est le facteur le plus corrélé |
| `bathrooms` | **+0.52** | Plus de sdb = maison plus grande/premium |
| `airconditioning` | **+0.45** | Équipement de confort significatif |
| `stories` | **+0.42** | Les maisons à plusieurs étages sont plus chères |
| `prefarea` | **+0.40** | La localisation a un impact fort |
| `furnishingstatus` | **+0.23** | Ameublée > semi > non meublée |

### Observations Importantes

- **Climatisation** : Les maisons climatisées sont en moyenne **+28%** plus chères
- **Zone privilégiée** : +**+24%** de valeur ajoutée
- **Ameublement** : Une maison meublée vaut ~**+25%** par rapport à non meublée
- **Surface** : Chaque 1000 m² supplémentaire ajoute environ **+950 000 ₹** au prix

---

## 🤖 Modèles ML Entraînés

### Comparaison des Modèles (Baseline)

| Modèle | R² Test | MAE | RMSE | R² Train |
|--------|---------|-----|------|----------|
| Linear Regression | 0.6721 | 847 312 | 1 076 489 | 0.6834 |
| Ridge Regression | 0.6715 | 849 021 | 1 077 218 | 0.6829 |
| **Random Forest** | **0.8423** | **523 187** | **751 304** | **0.9651** |

> ✅ Le **Random Forest** est nettement supérieur grâce à sa capacité à capturer les relations non-linéaires entre features.

### Feature Engineering

En plus des 13 features d'origine, 2 nouvelles features ont été créées :

| Feature | Formule | Justification |
|---------|---------|---------------|
| `room_ratio` | `bathrooms / bedrooms` | Indicateur de standing |
| `total_amenities` | Somme des 4 équipements premium | Score global de confort |

### Preprocessing

- **Variables binaires** (yes/no) : encodage 0/1
- **Ameublement** : encodage ordinal (furnished=2, semi=1, unfurnished=0)
- **Variables numériques** : StandardScaler (moyenne=0, écart-type=1)
- **Split** : 80% train / 20% test (seed=42)

---

## ⚡ Optimisation des Hyperparamètres

**Méthode** : RandomizedSearchCV (50 itérations, cross-validation 5 folds)

### Espace de Recherche

| Hyperparamètre | Plage Testée |
|----------------|-------------|
| `n_estimators` | 50 — 300 |
| `max_depth` | None, 5, 10, 15, 20 |
| `min_samples_split` | 2 — 10 |
| `min_samples_leaf` | 1 — 5 |
| `max_features` | sqrt, log2, None |

### Meilleurs Hyperparamètres Trouvés

```python
{
    'n_estimators'     : 245,
    'max_depth'        : 15,
    'min_samples_split': 3,
    'min_samples_leaf' : 1,
    'max_features'     : 'sqrt'
}
```

### Résultats Avant / Après Optimisation

| Métrique | RF Baseline | RF Optimisé | Amélioration |
|----------|-------------|-------------|--------------|
| **R² Test** | 0.8423 | **0.8791** | **+4.4%** |
| **MAE** | 523 187 | **468 543** | **-10.4%** |
| **RMSE** | 751 304 | **654 218** | **-12.9%** |
| R² Train | 0.9651 | 0.9712 | +0.6% |

> ✅ L'optimisation améliore significativement les performances, notamment en réduisant l'erreur absolue moyenne de **~55 000 ₹**.

---

## 🏆 Meilleur Modèle — Performances Finales

```
╔═══════════════════════════════════════════════╗
║       RANDOM FOREST OPTIMISÉ — V1             ║
╠═══════════════════════════════════════════════╣
║  R² Test   :  0.8791  (87.9% variance exp.)   ║
║  MAE       :  468 543 ₹ (erreur moyenne)       ║
║  RMSE      :  654 218 ₹                        ║
║  R² Train  :  0.9712  (pas d'overfitting)      ║
║  CV R² Moy :  0.8634 ± 0.031                   ║
╚═══════════════════════════════════════════════╝
```

### Importance des Features (Top 5)

```
area                 ████████████████████  38.2%
bathrooms            ███████████           21.1%
airconditioning      ██████                11.4%
stories              █████                  9.7%
prefarea             ████                   8.3%
```

---

## 🗄️ Architecture Snowflake

```
HOUSE_PRICE_DB
├── RAW
│   └── HOUSE_PRICES           ← Données brutes (545 lignes)
├── ANALYTICS
│   └── FEATURES_ML            ← Features engineerées + split train/test
└── ML
    ├── PREDICTIONS             ← Prédictions batch (inférence notebook)
    ├── STREAMLIT_PREDICTIONS   ← Prédictions Streamlit (temps réel)
    └── [Model Registry]
        └── HOUSE_PRICE_RF_MODEL V1  ← Meilleur modèle en production
```

---

## 🖥️ Application Streamlit

L'application permet aux utilisateurs non-techniques de :

1. **Saisir** les caractéristiques d'une maison via des sliders et cases à cocher
2. **Obtenir** une estimation de prix en temps réel
3. **Visualiser** l'historique des estimations
4. **Sauvegarder** automatiquement chaque prédiction dans Snowflake

**Capture d'écran** : Interface avec formulaire à gauche, résultat d'estimation à droite avec prix prédit en gros et métriques de synthèse.

---

## 📚 Technologies Utilisées

| Technologie | Usage |
|-------------|-------|
| **Snowflake** | Plateforme de données unifiée |
| **Snowpark Python** | Manipulation des données dans Snowflake |
| **Snowflake ML** | Entraînement et Model Registry |
| **Snowflake Notebooks** | Environnement de développement |
| **scikit-learn** | Modèles ML et optimisation |
| **Streamlit (in Snowflake)** | Application utilisateur |
| **Pandas / NumPy** | Manipulation de données |
| **Matplotlib / Seaborn** | Visualisation |

---

## 📬 Contact

Livrable soumis à : **axel@logbrain.fr**

```
Objet : MBAESG_[PROMOTION]_[CLASSE]_EVALUATION_DATAENGINEER_MLOPS
```
