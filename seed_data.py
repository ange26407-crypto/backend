"""
Script de seeding pour générer des données de test.
Exécuter avec: python manage.py shell < seed_data.py
Ou: python manage.py runscript seed_data (si django-extensions installé)
"""

import os
import sys
import django
import random
import secrets
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esante_backend.settings')
django.setup()

from django.utils import timezone
from users.models import User
from devices.models import Device, SensorData
from health.models import HealthData
from alerts.models import Alert
from chat.models import Message
from rest_framework.authtoken.models import Token

print("=" * 60)
print("SEEDING DE LA BASE DE DONNÉES HEALTHTIC")
print("=" * 60)

# ============================================================
# 1. CRÉATION DES MÉDECINS
# ============================================================
print("\n[1/6] Création des médecins...")

medecins_data = [
    {"username": "dr_martin", "email": "dr.martin@healthtic.com", "password": "medecin123", "first_name": "Jean", "last_name": "Martin"},
    {"username": "dr_dubois", "email": "dr.dubois@healthtic.com", "password": "medecin123", "first_name": "Marie", "last_name": "Dubois"},
    {"username": "dr_laurent", "email": "dr.laurent@healthtic.com", "password": "medecin123", "first_name": "Pierre", "last_name": "Laurent"},
    {"username": "dr_rousseau", "email": "dr.rousseau@healthtic.com", "password": "medecin123", "first_name": "Sophie", "last_name": "Rousseau"},
    {"username": "dr_bernard", "email": "dr.bernard@healthtic.com", "password": "medecin123", "first_name": "Luc", "last_name": "Bernard"},
]

medecins = []
for data in medecins_data:
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "username": data["username"],
            "role": "doctor",
            "first_name": data["first_name"],
            "last_name": data["last_name"]
        }
    )
    if created:
        user.set_password(data["password"])
        user.save()
        Token.objects.get_or_create(user=user)
        print(f"  ✓ Médecin créé: {user.username} ({user.email})")
    else:
        print(f"  - Médecin existant: {user.username}")
    medecins.append(user)

# ============================================================
# 2. CRÉATION DES PATIENTS (assignés aux médecins)
# ============================================================
print("\n[2/6] Création des patients...")

patients_data = [
    {"username": "patient_alice", "email": "alice@example.com", "password": "patient123", "first_name": "Alice", "last_name": "Dupont"},
    {"username": "patient_bob", "email": "bob@example.com", "password": "patient123", "first_name": "Bob", "last_name": "Leroy"},
    {"username": "patient_claire", "email": "claire@example.com", "password": "patient123", "first_name": "Claire", "last_name": "Bernard"},
    {"username": "patient_david", "email": "david@example.com", "password": "patient123", "first_name": "David", "last_name": "Moreau"},
    {"username": "patient_emma", "email": "emma@example.com", "password": "patient123", "first_name": "Emma", "last_name": "Petit"},
    {"username": "patient_felix", "email": "felix@example.com", "password": "patient123", "first_name": "Felix", "last_name": "Garnier"},
    {"username": "patient_gabrielle", "email": "gabrielle@example.com", "password": "patient123", "first_name": "Gabrielle", "last_name": "Roux"},
    {"username": "patient_hugo", "email": "hugo@example.com", "password": "patient123", "first_name": "Hugo", "last_name": "Simon"},
    {"username": "patient_isabelle", "email": "isabelle@example.com", "password": "patient123", "first_name": "Isabelle", "last_name": "Michel"},
    {"username": "patient_julien", "email": "julien@example.com", "password": "patient123", "first_name": "Julien", "last_name": "Lefebvre"},
    {"username": "patient_karine", "email": "karine@example.com", "password": "patient123", "first_name": "Karine", "last_name": "Mercier"},
    {"username": "patient_louis", "email": "louis@example.com", "password": "patient123", "first_name": "Louis", "last_name": "Blanc"},
    {"username": "patient_marine", "email": "marine@example.com", "password": "patient123", "first_name": "Marine", "last_name": "Guerin"},
    {"username": "patient_nathan", "email": "nathan@example.com", "password": "patient123", "first_name": "Nathan", "last_name": "Boyer"},
    {"username": "patient_olivia", "email": "olivia@example.com", "password": "patient123", "first_name": "Olivia", "last_name": "Faure"},
]

patients = []
for i, data in enumerate(patients_data):
    # Assigner chaque patient à un médecin (alternance)
    medecin_assigne = medecins[i % len(medecins)]
    
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "username": data["username"],
            "role": "patient",
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "medecin": medecin_assigne
        }
    )
    if created:
        user.set_password(data["password"])
        user.save()
        Token.objects.get_or_create(user=user)
        print(f"  ✓ Patient créé: {user.username} → Médecin: {medecin_assigne.username}")
    else:
        # Mettre à jour le médecin si pas déjà assigné
        if not user.medecin:
            user.medecin = medecin_assigne
            user.save()
        print(f"  - Patient existant: {user.username} → Médecin: {user.medecin.username if user.medecin else 'Non assigné'}")
    patients.append(user)

# ============================================================
# 3. CRÉATION DES DEVICES POUR CHAQUE PATIENT
# ============================================================
print("\n[3/6] Création des devices...")

devices = []
for patient in patients:
    device, created = Device.objects.get_or_create(
        user=patient,
        defaults={
            "name": f"Capteur de {patient.first_name}",
            "device_key": secrets.token_hex(32),
            "is_active": True
        }
    )
    if created:
        print(f"  ✓ Device créé: {device.name} (key: {device.device_key[:16]}...)")
    else:
        print(f"  - Device existant: {device.name}")
    devices.append(device)

# ============================================================
# 4. CRÉATION DES DONNÉES DE CAPTEURS ET SANTÉ
# ============================================================
print("\n[4/6] Création des données de capteurs et santé...")

# Statuts possibles pour l'IA
ai_statuses = [
    (0, "Sain"),
    (1, "Infection légère"),
    (2, "Infection modérée"),
    (3, "Hypoxie sévère")
]

for device in devices:
    # Créer 30 mesures par device sur les 30 derniers jours
    for j in range(30):
        # Générer des valeurs réalistes
        is_healthy = random.random() > 0.3  # 70% de chances d'être sain
        
        if is_healthy:
            cov_ppb = random.uniform(100, 300)
            eco2_ppm = random.uniform(400, 600)
            heart_rate = random.uniform(60, 90)
            spo2 = random.uniform(96, 100)
            temperature = random.uniform(36.2, 37.2)
            ai_status = 0
        else:
            cov_ppb = random.uniform(300, 800)
            eco2_ppm = random.uniform(600, 1200)
            heart_rate = random.uniform(85, 120)
            spo2 = random.uniform(88, 96)
            temperature = random.uniform(37.5, 39.5)
            ai_status = random.choice([1, 2, 3])
        
        # Créer SensorData
        created_at = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        sensor_data = SensorData.objects.create(
            device=device,
            cov_ppb=round(cov_ppb, 2),
            eco2_ppm=round(eco2_ppm, 2),
            heart_rate=round(heart_rate, 1),
            spo2=round(spo2, 1),
            temperature=round(temperature, 1),
            ai_status=ai_status,
            ai_status_name=ai_statuses[ai_status][1],
            ai_confidence=round(random.uniform(0.75, 0.99), 2),
            ai_probabilities={
                "Sain": round(random.uniform(0.1, 0.9), 2),
                "Infection légère": round(random.uniform(0.05, 0.3), 2),
                "Infection modérée": round(random.uniform(0.02, 0.2), 2),
                "Hypoxie sévère": round(random.uniform(0.01, 0.1), 2)
            },
            processed=True
        )
        sensor_data.created_at = created_at
        sensor_data.save(update_fields=['created_at'])
        
        # Créer HealthData correspondant
        status = 'normal' if ai_status == 0 else 'attention' if ai_status <= 2 else 'danger'
        health_data = HealthData.objects.create(
            user=device.user,
            heart_rate=int(heart_rate),
            oxygen_level=round(spo2, 1),
            temperature=round(temperature, 1),
            respiratory_rate=int(eco2_ppm / 30),
            air_quality=int(cov_ppb / 10),
            status=status
        )
        health_data.created_at = created_at
        health_data.save(update_fields=['created_at'])
    
    # Mettre à jour last_data_at du device
    device.last_data_at = timezone.now()
    device.save()
    
    print(f"  ✓ 30 mesures créées pour {device.user.username}")

# ============================================================
# 5. CRÉATION DES ALERTES
# ============================================================
print("\n[5/6] Création des alertes...")

alertes_templates = [
    {"title": "Fréquence cardiaque élevée", "message": "Votre fréquence cardiaque a dépassé 100 bpm. Veuillez vous reposer.", "level": "warning"},
    {"title": "SpO2 bas détecté", "message": "Votre niveau d'oxygène est inférieur à 95%. Consultez un médecin si cela persiste.", "level": "danger"},
    {"title": "Température élevée", "message": "Votre température corporelle est de 38.5°C. Surveillez votre état.", "level": "warning"},
    {"title": "Qualité de l'air dégradée", "message": "La qualité de l'air dans votre environnement est mauvaise. Aérez la pièce.", "level": "info"},
    {"title": "Rappel de mesure", "message": "N'oubliez pas de prendre vos mesures quotidiennes.", "level": "info"},
]

for patient in patients:
    # Créer 3-7 alertes par patient
    num_alertes = random.randint(3, 7)
    for _ in range(num_alertes):
        template = random.choice(alertes_templates)
        Alert.objects.create(
            user=patient,
            title=template["title"],
            message=template["message"],
            level=template["level"],
            is_read=random.choice([True, False])
        )
    print(f"  ✓ {num_alertes} alertes créées pour {patient.username}")

# ============================================================
# 6. CRÉATION DES MESSAGES
# ============================================================
print("\n[6/6] Création des messages...")

messages_templates = [
    "Bonjour, comment allez-vous aujourd'hui ?",
    "J'ai remarqué que vos dernières mesures sont un peu élevées. Comment vous sentez-vous ?",
    "N'oubliez pas de prendre vos médicaments.",
    "Merci docteur, je me sens mieux aujourd'hui.",
    "J'ai quelques questions concernant mes résultats.",
    "Vos résultats sont bons, continuez ainsi !",
    "Pouvez-vous me rappeler quand je dois revenir pour un contrôle ?",
    "Je ressens une légère fatigue ces derniers jours.",
]

for patient in patients:
    if patient.medecin:
        # Messages du médecin vers le patient
        for _ in range(random.randint(3, 6)):
            msg = Message.objects.create(
                sender=patient.medecin,
                receiver=patient,
                content=random.choice(messages_templates),
                is_read=random.choice([True, False])
            )
            msg.created_at = timezone.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            msg.save(update_fields=['created_at'])
        
        # Messages du patient vers le médecin
        for _ in range(random.randint(2, 5)):
            msg = Message.objects.create(
                sender=patient,
                receiver=patient.medecin,
                content=random.choice(messages_templates),
                is_read=random.choice([True, False])
            )
            msg.created_at = timezone.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            msg.save(update_fields=['created_at'])
        
        print(f"  ✓ Messages créés entre {patient.username} et {patient.medecin.username}")

# ============================================================
# RÉSUMÉ
# ============================================================
print("\n" + "=" * 60)
print("SEEDING TERMINÉ AVEC SUCCÈS!")
print("=" * 60)

print("\n📋 COMPTES DE TEST:")
print("-" * 40)
print("\n🩺 MÉDECINS:")
for m in medecins:
    print(f"   Email: {m.email}")
    print(f"   Mot de passe: medecin123")
    print()

print("👤 PATIENTS:")
for p in patients:
    print(f"   Email: {p.email}")
    print(f"   Mot de passe: patient123")
    print(f"   Médecin assigné: {p.medecin.username if p.medecin else 'Aucun'}")
    print()

print("\n📊 STATISTIQUES:")
print(f"   - {User.objects.filter(role='doctor').count()} médecins")
print(f"   - {User.objects.filter(role='patient').count()} patients")
print(f"   - {Device.objects.count()} devices")
print(f"   - {SensorData.objects.count()} données de capteurs")
print(f"   - {HealthData.objects.count()} données de santé")
print(f"   - {Alert.objects.count()} alertes")
print(f"   - {Message.objects.count()} messages")

print("\n🔑 DEVICE KEYS (pour tester le hardware):")
for d in Device.objects.all()[:3]:
    print(f"   {d.user.username}: {d.device_key}")
