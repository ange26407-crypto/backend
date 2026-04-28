# Logique Métier - Système HealthTic IoT

Ce document explique comment le système traite les données envoyées par le dispositif IoT (capteur) et comment ces données sont utilisées par l'interface utilisateur (frontend).

---

## 1. Vue d'ensemble du système

Le système HealthTic est une plateforme de santé connectée qui :
1. **Reçoit** des mesures physiologiques depuis un capteur IoT (ex: ESP32)
2. **Analyse** ces données avec un modèle d'intelligence artificielle
3. **Stocke** les résultats dans une base de données
4. **Expose** ces données au frontend pour affichage et suivi

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  Capteur    │────▶│    Backend      │────▶│  Frontend   │
│  IoT/ESP32  │     │  (Serveur API)  │     │  (Web App)  │
└─────────────┘     └─────────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Modèle IA  │
                    │  Médical    │
                    └─────────────┘
```

---

## 2. Les données captées par le dispositif IoT

Le capteur IoT mesure **5 paramètres vitaux** :

| Paramètre | Description | Unité | Exemple |
|-----------|-------------|-------|---------|
| **cov_ppb** | Composés Organiques Volatils | ppb (parties par milliard) | 400 |
| **eco2_ppm** | CO2 équivalent | ppm (parties par million) | 420 |
| **heart_rate** | Fréquence cardiaque | bpm (battements/min) | 75 |
| **spo2** | Saturation en oxygène du sang | % | 98 |
| **temperature** | Température corporelle | °C | 36.8 |

---

## 3. Flux de réception des données IoT

### 3.1 Authentification du capteur

Chaque capteur possède une **clé unique** (`device_key`) qui l'identifie :
- Cette clé est générée lors de l'enregistrement du capteur par l'utilisateur
- Le capteur envoie cette clé avec chaque transmission de données
- Le serveur vérifie que la clé existe et que le capteur est actif

### 3.2 Format des données envoyées par le capteur

Le capteur envoie un paquet de données au format suivant :

```json
{
    "device_key": "abc123...",
    "cov_ppb": 400,
    "eco2_ppm": 420,
    "heart_rate": 75,
    "spo2": 98,
    "temperature": 36.8
}
```

### 3.3 Processus de traitement (étape par étape)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RÉCEPTION DES DONNÉES                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. VALIDATION                                                   │
│    - Vérifier que la device_key est présente                   │
│    - Vérifier que le capteur existe et est actif               │
│    - Vérifier que tous les champs requis sont présents         │
│    - Convertir les valeurs en nombres décimaux                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. STOCKAGE DES DONNÉES BRUTES                                 │
│    - Créer un enregistrement SensorData avec :                 │
│      • Lien vers le capteur                                    │
│      • Les 5 valeurs mesurées                                  │
│      • Date/heure de réception                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. ANALYSE PAR L'INTELLIGENCE ARTIFICIELLE                     │
│    - Envoyer les 5 paramètres au modèle IA                     │
│    - Le modèle prédit l'état de santé (4 catégories)           │
│    - Récupérer le niveau de confiance de la prédiction         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. ENRICHISSEMENT DES DONNÉES                                  │
│    - Ajouter le résultat IA aux données du capteur             │
│    - Marquer les données comme "traitées"                      │
│    - Mettre à jour la date de dernière activité du capteur     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. CRÉATION DES DONNÉES DE SANTÉ UTILISATEUR                   │
│    - Créer un enregistrement HealthData pour l'utilisateur     │
│    - Convertir certaines valeurs (ex: eco2 → fréq. respiratoire)│
│    - Attribuer un statut global (normal/attention/critique)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. L'Intelligence Artificielle médicale

### 4.1 Rôle du modèle IA

Le modèle IA analyse les 5 paramètres vitaux et prédit l'état de santé parmi **4 catégories** :

| Code | État | Description |
|------|------|-------------|
| 0 | **Sain** | Tous les paramètres sont normaux |
| 1 | **Infection légère** | Signes d'une infection mineure |
| 2 | **Infection modérée** | Infection nécessitant une surveillance |
| 3 | **Hypoxie sévère** | Manque critique d'oxygène - urgence |

### 4.2 Fonctionnement du modèle

1. **Normalisation** : Les valeurs brutes sont normalisées (mises à l'échelle)
2. **Prédiction** : Le modèle calcule la probabilité pour chaque catégorie
3. **Résultat** : La catégorie avec la plus haute probabilité est retenue

### 4.3 Sortie du modèle IA

```json
{
    "status": 0,
    "status_name": "Sain",
    "confidence": 92.5,
    "probabilities": {
        "Sain": 92.5,
        "Infection légère": 5.2,
        "Infection modérée": 1.8,
        "Hypoxie sévère": 0.5
    }
}
```

---

## 5. Stockage des données

### 5.1 Données brutes du capteur (SensorData)

Chaque mesure du capteur est stockée avec :
- **Lien vers le capteur** (quel appareil a envoyé les données)
- **Les 5 valeurs mesurées** (cov, eco2, heart_rate, spo2, temperature)
- **Résultat IA** (statut, nom du statut, confiance, probabilités)
- **Métadonnées** (date de création, indicateur de traitement)

### 5.2 Données de santé utilisateur (HealthData)

Version simplifiée pour l'affichage frontend :
- **Fréquence cardiaque** (bpm)
- **Niveau d'oxygène** (SpO2 %)
- **Température** (°C)
- **Fréquence respiratoire** (estimée depuis eco2)
- **Qualité de l'air** (convertie depuis cov)
- **Statut global** : normal / attention / critique

### 5.3 Règle de conversion du statut IA vers statut santé

| Statut IA | Statut Santé |
|-----------|--------------|
| 0 (Sain) | normal |
| 1 ou 2 (Infection légère/modérée) | attention |
| 3 (Hypoxie sévère) | critical |

---

## 6. Utilisation des données par le Frontend

### 6.1 Tableau de bord (Dashboard)

Le frontend récupère les données via l'endpoint `/health/dashboard/` qui fournit :

**Statistiques actuelles :**
- Fréquence respiratoire avec statut (Normale/Attention)
- Fréquence cardiaque avec statut
- SpO2 avec statut (Excellente/Normale/Attention)
- Qualité de l'air avec statut (Bonne/Modérée/Mauvaise)
- Température avec statut

**Tendances sur 7 jours :**
- Score de santé quotidien (0-100)
- Calculé à partir des moyennes de SpO2 et fréquence cardiaque

**Historique récent :**
- 4 dernières mesures avec date, statut et couleur

### 6.2 Prédictions IA

Le frontend récupère les prédictions via `/health/prediction/` :

**Score de santé (0-10) :**
- Basé sur SpO2, fréquence cardiaque et température moyennes

**Risque relatif (0-100%) :**
- Calculé selon des seuils :
  - SpO2 < 95% → +20%
  - Fréquence cardiaque hors 60-100 bpm → +15%
  - Température hors 36-37.5°C → +15%
  - Qualité air > 50 AQI → +10%
  - Fréquence respiratoire hors 12-20/min → +10%

**Niveau de risque :**
- < 20% → Faible (vert)
- 20-50% → Modéré (orange)
- > 50% → Élevé (rouge)

**Recommandations personnalisées :**
- Générées automatiquement selon les facteurs de risque détectés
- Exemples : exercices respiratoires, relaxation, éviter la pollution

### 6.3 Données des capteurs

Le frontend peut récupérer :
- **Liste des capteurs** de l'utilisateur (`/devices/my-devices/`)
- **20 dernières mesures** avec résultats IA (`/devices/sensor-data/`)
- **Dernier résultat IA** (`/devices/latest-ai/`)

---

## 7. Système d'alertes

### 7.1 Déclenchement automatique

Des alertes sont générées automatiquement selon des seuils critiques :

| Paramètre | Seuil Warning | Seuil Danger |
|-----------|---------------|--------------|
| SpO2 | < 95% | < 90% |
| Fréquence cardiaque | > 100 bpm | > 120 bpm |
| Température | > 37.5°C | > 38.5°C |

### 7.2 Niveaux d'alerte

- **Info** : Information générale
- **Warning** : Attention requise
- **Danger** : Situation critique

---

## 8. Relation Utilisateurs et Capteurs

### 8.1 Types d'utilisateurs

- **Patient** : Possède des capteurs, reçoit des mesures
- **Docteur** : Peut suivre plusieurs patients

### 8.2 Gestion des capteurs

Chaque utilisateur peut :
1. **Créer** un nouveau capteur (génère une clé unique)
2. **Lister** ses capteurs
3. **Activer/Désactiver** un capteur
4. **Régénérer** la clé d'un capteur (sécurité)
5. **Supprimer** un capteur

---

## 9. Résumé du flux complet

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   CAPTEUR IoT                                                            │
│   ───────────                                                            │
│   Mesure: cov, eco2, heart_rate, spo2, temperature                      │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      BACKEND                                     │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │   │
│   │  │ Validation  │───▶│ Stockage    │───▶│ Analyse IA          │  │   │
│   │  │ device_key  │    │ SensorData  │    │ (4 catégories)      │  │   │
│   │  └─────────────┘    └─────────────┘    └─────────────────────┘  │   │
│   │                                                │                 │   │
│   │                                                ▼                 │   │
│   │                           ┌─────────────────────────────────┐   │   │
│   │                           │ Création HealthData             │   │   │
│   │                           │ (données simplifiées + statut)  │   │   │
│   │                           └─────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      FRONTEND                                    │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │   │
│   │  │ Dashboard   │    │ Prédictions │    │ Historique          │  │   │
│   │  │ (stats)     │    │ (risques)   │    │ (graphiques)        │  │   │
│   │  └─────────────┘    └─────────────┘    └─────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Points clés à retenir

1. **Le capteur s'authentifie** avec sa clé unique (`device_key`)
2. **5 paramètres** sont mesurés à chaque transmission
3. **L'IA analyse** et classe l'état de santé en 4 catégories
4. **Deux types de stockage** : données brutes (SensorData) et données simplifiées (HealthData)
5. **Le frontend** consomme les données via des points d'accès dédiés
6. **Les alertes** sont générées automatiquement selon des seuils médicaux
7. **Les recommandations** sont personnalisées selon les facteurs de risque détectés
