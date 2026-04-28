"""
Script pour peupler la base de données PostgreSQL de production
Exécuter avec: python populate_db.py
"""

import os
os.environ['DATABASE_URL'] = 'postgresql://sante_92qb_user:Xe1fnHAEvFJilM44ExvpReJpvXYreb5E@dpg-d7nu5q68bjmc7393bvtg-a.virginia-postgres.render.com/sante_92qb'

# Importer et exécuter seed_data
import seed_data

print("\n✅ Base de données PostgreSQL peuplée avec succès!")
