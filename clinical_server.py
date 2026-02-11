from mcp.server.fastmcp import FastMCP
import sqlite3

# Initialize the server
mcp = FastMCP("Aegis Clinical Records")
DB_PATH = "hospital.db"

@mcp.tool()
def get_patient_data(patient_id: str) -> str:
    """
    Retrieves history and allergies for a specific patient ID (e.g., PATIENT_001).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT history, allergies FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return f"History: {row[0]}\nAllergies: {row[1]}"
    return "Patient record not found."

if __name__ == "__main__":
    mcp.run()