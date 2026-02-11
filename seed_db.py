import sqlite3

conn = sqlite3.connect('hospital.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS patients
             (id text, name text, age integer, history text, allergies text)''')

# Insert dummy data
patients = [
    ('PATIENT_001', 'John Doe', 45, 'History of hypertension. Smoker.', 'Penicillin'),
    ('PATIENT_002', 'Jane Smith', 29, 'Type 2 Diabetes. Pregnancy trimester 1.', 'Sulfa drugs')
]

c.executemany('INSERT INTO patients VALUES (?,?,?,?,?)', patients)
conn.commit()
conn.close()
print("Database seeded!")