# HealthTic — Projet pour CV

---

## Description courte (à mettre dans le CV)

> **HealthTic** — Plateforme IoT de santé connectée avec Intelligence Artificielle  
> Conception et développement d'une plateforme complète de télémédecine intégrant un dispositif IoT (ESP32), un modèle de Machine Learning pour la classification d'états respiratoires, une API REST, et une interface web temps réel.

---

## Ligne CV — Version concise

```
HealthTic | Plateforme IoT e-santé avec IA médicale
- Développement d'un modèle de classification médicale (Random Forest, scikit-learn) pour détecter 4 états de santé respiratoire à partir de 5 paramètres physiologiques captés par un dispositif IoT (ESP32)
- Conception d'un pipeline complet : génération de données synthétiques médicalement validées, entraînement, normalisation, déploiement du modèle en production via API REST
- Architecture full-stack : backend Python (API REST, PostgreSQL), frontend React/TypeScript (TailwindCSS), communication IoT via clé d'authentification
- Fonctionnalités : tableau de bord temps réel, prédictions IA avec score de confiance, alertes automatiques, messagerie patient-médecin, recommandations personnalisées
Technologies : Python, scikit-learn, NumPy, Pandas, REST API, React, TypeScript, TailwindCSS, PostgreSQL, ESP32
```

---

## Version détaillée pour entretien / lettre de motivation

### Le problème résolu

HealthTic répond au besoin de **suivi médical à distance** des patients à risque respiratoire. Le système permet à un patient équipé d'un capteur IoT de transmettre automatiquement ses paramètres vitaux à un serveur, qui les analyse en temps réel grâce à un modèle d'IA et alerte le médecin si nécessaire.

### Architecture technique

```
Capteur IoT (ESP32)
    │
    │  Envoi HTTP (5 paramètres vitaux + clé d'authentification)
    ▼
API REST (Backend Python)
    │
    ├── Validation et stockage des données brutes
    ├── Analyse IA en temps réel (Random Forest)
    ├── Génération automatique d'alertes médicales
    └── Calcul de scores et recommandations
    │
    ▼
Interface Web (React + TypeScript)
    │
    ├── Tableau de bord patient (graphiques, tendances 7 jours)
    ├── Page Prédiction IA (score santé, risque, confiance)
    ├── Système d'alertes (info / warning / danger)
    └── Messagerie patient ↔ médecin
```

---

## PARTIE IA — Le coeur du projet (à valoriser)

### 1. Génération de données d'entraînement

J'ai conçu un **générateur de données synthétiques médicalement réalistes** basé sur la littérature médicale :

- **4 profils cliniques** définis avec des plages physiologiques validées :
  - **Sain** (50% du dataset) : SpO2 96-100%, FC 60-85 bpm, T° 36.4-37.2°C
  - **Infection légère** (25%) : SpO2 94-97%, FC 85-105 bpm, T° 37.3-38.5°C
  - **Infection modérée** (15%) : SpO2 89-94%, FC 95-120 bpm, T° 37.8-39.5°C
  - **Hypoxie sévère** (10%) : SpO2 75-89%, FC 105-140 bpm, T° 37.5-40°C

- **Simulation réaliste** :
  - Distribution normale tronquée pour chaque paramètre
  - Bruit de capteur simulé (±5%) pour reproduire les erreurs de mesure
  - **Corrélations physiologiques** intégrées (ex: la fièvre augmente la fréquence cardiaque de ~10 bpm par degré au-dessus de 37°C)
  - Ajout de 5% d'outliers pour la robustesse du modèle

- **Dataset final** : 2000 échantillons, 5 features, 4 classes

### 2. Modèle de Machine Learning

- **Algorithme** : Random Forest Classifier
- **Hyperparamètres** : 100 arbres, profondeur max 10, min 5 samples pour split, min 2 samples par feuille
- **Prétraitement** : StandardScaler (normalisation moyenne=0, écart-type=1)
- **Validation** : train/test split 80/20 avec stratification + rapport de classification complet
- **Analyse** : importance des features pour interpréter les décisions du modèle

### 3. Entrées et sorties du modèle

**5 paramètres d'entrée (features)** captés par le dispositif IoT :

| Feature | Description | Capteur |
|---------|-------------|---------|
| `cov_ppb` | Composés Organiques Volatils | Capteur COV |
| `eco2_ppm` | CO2 équivalent | Capteur eCO2 |
| `heart_rate` | Fréquence cardiaque | Capteur optique (PPG) |
| `spo2` | Saturation en oxygène | Oxymètre de pouls |
| `temperature` | Température corporelle | Capteur de température |

**Sortie** : classification en 4 états + probabilités + score de confiance

```
Entrée :  [400, 420, 75, 98, 36.8]
Sortie :  { status: "Sain", confidence: 92.5%, 
            probabilités: {Sain: 92.5%, Inf. légère: 5.2%, Inf. modérée: 1.8%, Hypoxie: 0.5%} }
```

### 4. Déploiement du modèle en production

- **Pattern Singleton** : une seule instance du modèle chargée en mémoire pour optimiser les performances
- **Chargement paresseux** (lazy loading) : le modèle se charge automatiquement à la première requête
- **Sérialisation** : modèle et scaler sauvegardés via joblib (.pkl)
- **Gestion d'erreurs** : fallback gracieux si le modèle n'est pas disponible
- **Intégration API** : prédiction en temps réel à chaque réception de données IoT

### 5. Logique de scoring et prédiction côté serveur

Au-delà du modèle ML, j'ai implémenté une **couche de scoring métier** :

- **Score de santé (0-10)** : moyenne pondérée de scores individuels (SpO2, FC, température)
- **Risque relatif (0-100%)** : accumulation de facteurs de risque avec seuils médicaux
- **Confiance IA dynamique** : augmente avec le nombre de données collectées (min 50%, +5% par mesure, max 95%)
- **Recommandations personnalisées** : générées automatiquement selon les facteurs de risque détectés

---

## Compétences techniques démontrées

### Intelligence Artificielle / Machine Learning
- Génération de données synthétiques réalistes (data augmentation)
- Modélisation de corrélations physiologiques
- Entraînement et évaluation de modèle de classification supervisée
- Normalisation et prétraitement des données (StandardScaler)
- Déploiement d'un modèle ML en production (API temps réel)
- Interprétabilité du modèle (feature importance, probabilités par classe)

### Backend / API
- Conception d'API REST sécurisée
- Authentification par token (utilisateurs) et par clé (dispositifs IoT)
- Architecture modulaire (users, devices, health, alerts, chat, measurements)
- Base de données relationnelle (PostgreSQL)
- Système d'alertes automatiques basé sur des seuils médicaux

### Frontend
- Interface React avec TypeScript
- Design responsive (TailwindCSS)
- Visualisation de données de santé (graphiques, tendances)
- Gestion d'état (Zustand)
- Pages : Dashboard, Prédiction IA, Alertes, Messagerie, Profil

### IoT / Embarqué
- Communication HTTP entre ESP32 et serveur
- Authentification par clé unique du dispositif
- Protocole de transmission des 5 paramètres vitaux

### Architecture
- Architecture 3-tiers : IoT → Backend → Frontend
- Pattern Singleton pour le service IA
- Séparation données brutes (SensorData) / données métier (HealthData)
- Système de rôles (patient / médecin) avec assignation

---

## Stack technique complète

| Couche | Technologies |
|--------|-------------|
| **IA / ML** | Python, scikit-learn, NumPy, Pandas, joblib |
| **Backend** | Python, REST API, PostgreSQL |
| **Frontend** | React 19, TypeScript, TailwindCSS, Zustand, Axios, Lucide |
| **IoT** | ESP32, HTTP, capteurs physiologiques |
| **Déploiement** | Render (backend), Vercel (frontend) |

---

## Mots-clés pour ATS (systèmes de tri de CV)

Machine Learning, Random Forest, Classification supervisée, IoT, e-santé, Télémédecine, API REST, Python, scikit-learn, React, TypeScript, PostgreSQL, TailwindCSS, ESP32, Données physiologiques, Prédiction médicale, Full-stack, Temps réel

---

## Exemple de bullet points CV

Choisis 3-4 de ces lignes selon le poste visé :

### Si tu postules en IA / Data Science :
- Conception et entraînement d'un modèle Random Forest pour la classification de 4 états de santé respiratoire à partir de 5 paramètres physiologiques IoT (scikit-learn, Pandas, NumPy)
- Création d'un générateur de données synthétiques médicales avec corrélations physiologiques réalistes et simulation de bruit capteur
- Déploiement d'un modèle ML en production via API REST avec prédiction temps réel, score de confiance et probabilités par classe
- Implémentation d'un système de scoring de risque multi-facteurs avec recommandations personnalisées automatiques

### Si tu postules en Développement Full-Stack :
- Développement full-stack d'une plateforme e-santé : API REST Python + frontend React/TypeScript + intégration IoT ESP32
- Conception d'une architecture 3-tiers avec double authentification (token utilisateur + clé dispositif IoT)
- Implémentation d'un tableau de bord temps réel avec tendances sur 7 jours, alertes automatiques et messagerie patient-médecin
- Intégration d'un modèle de Machine Learning en production pour l'analyse prédictive des données de santé

### Si tu postules en IoT / Systèmes embarqués :
- Intégration d'un dispositif ESP32 avec capteurs physiologiques (SpO2, FC, température, COV, eCO2) et transmission HTTP vers un serveur d'analyse IA
- Conception du protocole de communication IoT sécurisé par clé d'authentification unique par dispositif
- Pipeline complet capteur → serveur → IA → interface utilisateur avec alertes en temps réel
