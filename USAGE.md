# Usage Guide: Running AEGIS Locally

This guide explains how to run the AEGIS MCP servers on your local machine without using Docker.

## Prerequisites

- Python 3.10 or higher
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) (Recommended for testing)

## 1. Setup Environment

First, create a virtual environment and install the dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt

# Download the required spaCy model for PII analysis
python -m spacy download en_core_web_lg
```

## 2. Seed the Database

Before running the clinical server, initialize the SQLite database with patient records:

```bash
python seed_db.py
```

## 3. Run the PII Scrubber Server

You can run the PII server using the MCP Inspector or directly via Python:

```bash
# Using FastMCP CLI (Preferred for development)
mcp dev pii_server.py
```

Or run it as a standard MCP server for integration:
```bash
python pii_server.py
```

## 4. Run the Clinical Records Server

Similarly, start the clinical records server:

```bash
# Using FastMCP CLI
mcp dev clinical_server.py
```

Or directly:
```bash
python clinical_server.py
```

## 5. Testing with Test Prompts

Once the servers are running, you can use the prompts provided in the [README.md](README.md) to test the workflow. 

### Identity Mapping Logic
Note that for the hackathon demo, the `pii_server.py` contains deterministic mapping for specific names:
- **John Doe** -> `PATIENT_001`
- **Jane Smith** -> `PATIENT_002`
- **Rahul Sharma** -> `PATIENT_003`
- **Priya Patel** -> `PATIENT_004`

Ensure you use these names in your testing to trigger the correct database lookups.
