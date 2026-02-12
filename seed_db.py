"""
AEGIS Hospital Database Seeding Script
This script initializes the local SQLite database with sample patient records
for use in the hackathon demo.
"""

import sqlite3

# Connect to the local database file
conn = sqlite3.connect('hospital.db')
c = conn.cursor()

# Create the patients table if it doesn't exist
# We store basic demographics alongside sensitive history and allergies
c.execute('''CREATE TABLE IF NOT EXISTS patients
             (id text, name text, age integer, history text, allergies text)''')

# Clear existing data to ensure a clean state for the demo
c.execute('DELETE FROM patients')

# Insert dummy data (including Indian patient context)
patients = [
    ('PATIENT_001', 'John Doe', 45, 'History of hypertension. Smoker.', 'Penicillin'),
    ('PATIENT_002', 'Jane Smith', 29, 'Type 2 Diabetes. Pregnancy trimester 1.', 'Sulfa drugs'),
    ('PATIENT_003', 'Rahul Sharma', 34, 'Chronic asthma. No history of surgery.', 'Dust, Pollen'),
    ('PATIENT_004', 'Priya Patel', 28, 'G6PD deficiency. History of anemia.', 'Aspirin, NSAIDs')
]

c.executemany('INSERT INTO patients VALUES (?,?,?,?,?)', patients)
conn.commit()
conn.close()
print("Database seeded!")