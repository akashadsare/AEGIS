"""
Aegis Clinical Records MCP Server
This server handles private access to the hospital's Electronic Health Records (EHR) 
stored in a local SQLite database.
"""

from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Initialize the FastMCP server
mcp = FastMCP("Aegis Clinical Records")

# Path to the SQLite database - using absolute path for consistency in Docker/K8s
DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")

def get_db_connection():
    """Helper to establish a database connection."""
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def get_patient_data(patient_id: str) -> str:
    """
    Retrieve clinical history and known allergies for a specific patient ID.
    
    Args:
        patient_id (str): The anonymized internal ID (e.g., PATIENT_001).
        
    Returns:
        str: Patient's medical history and allergies, or an error message if not found.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # We only select history and allergies to keep data access minimized
            cursor.execute("SELECT history, allergies FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            
        if row:
            return f"Medical History: {row[0]}\nKnown Allergies: {row[1]}"
        return f"Error: Patient record for {patient_id} not found."
    except Exception as e:
        # Log error for audit trails
        return f"Error accessing clinical database: {str(e)}"

@mcp.tool()
def list_patients() -> str:
    """
    List all registered patient IDs in the system. 
    Useful for the Clinical Clerk to verify if a record exists.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM patients")
            rows = cursor.fetchall()
            
        if rows:
            patient_list = "\n".join([f"- {row[0]}" for row in rows])
            return f"### Registered Internal Patient IDs:\n{patient_list}"
        return "No patients registered in the clinical database."
    except Exception as e:
        return f"Error accessing clinical database: {str(e)}"

if __name__ == "__main__":
    # Start the FastMCP server
    mcp.run()
