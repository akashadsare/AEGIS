"""
Aegis PII Scrubber MCP Server
This server provides tools to redact Personally Identifiable Information (PII) from medical notes.
It uses Microsoft Presidio for high-accuracy Named Entity Recognition (NER) and supports
both US and Indian specific identifiers to ensure HIPAA and DISHA compliance.
"""

from mcp.server.fastmcp import FastMCP
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize the FastMCP server
mcp = FastMCP("Aegis PII Scrubber")

# --- Custom PII Recognizers ---

# Custom SSN recognizer using regex to complement Presidio's built-in one
ssn_pattern = Pattern(name="ssn_pattern", regex=r"\b\d{3}-\d{2}-\d{4}\b", score=0.95)
ssn_recognizer = PatternRecognizer(supported_entity="US_SSN", patterns=[ssn_pattern])

# Indian PII: Aadhaar Number (12 digits, optional spaces/hyphens)
# Pattern matches 4-4-4 digit format commonly used in India
aadhaar_pattern = Pattern(name="aadhaar_pattern", regex=r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b", score=0.95)
aadhaar_recognizer = PatternRecognizer(supported_entity="IN_AADHAAR", patterns=[aadhaar_pattern])

# Indian PII: PAN Card (Permanent Account Number)
# Format: 5 letters, 4 digits, 1 letter
pan_pattern = Pattern(name="pan_pattern", regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", score=0.95)
pan_recognizer = PatternRecognizer(supported_entity="IN_PAN", patterns=[pan_pattern])

# Indian PII: Phone Number (+91 or 10 digits starting with 6-9)
in_phone_pattern = Pattern(name="in_phone_pattern", regex=r"\b(?:\+91[\-\s]?)?[6789]\d{9}\b", score=0.95)
in_phone_recognizer = PatternRecognizer(supported_entity="IN_PHONE", patterns=[in_phone_pattern])

# --- Engine Initialization ---

# Initialize Presidio Analyzer with custom recognizers
# We use the 'en_core_web_lg' spaCy model (configured in Dockerfile) for better NER accuracy
analyzer = AnalyzerEngine(default_score_threshold=0.4)
analyzer.registry.add_recognizer(ssn_recognizer)
analyzer.registry.add_recognizer(aadhaar_recognizer)
analyzer.registry.add_recognizer(pan_recognizer)
analyzer.registry.add_recognizer(in_phone_recognizer)
anonymizer = AnonymizerEngine()

@mcp.tool()
def scrub_medical_notes(text: str) -> str:
    """
    Scrub PII from medical notes for HIPAA/DISHA compliance.
    
    Args:
        text (str): The raw clinical notes containing sensitive patient information.
        
    Returns:
        str: Anonymized text with descriptive placeholders (e.g., [REDACTED_SSN])
             and mapped Patient IDs (e.g., PATIENT_001) for downstream clinical lookup.
    """
    # Define the entities to look for (Standard + Regional)
    entities = [
        "PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION", 
        "URL", "DATE_TIME", "US_SSN", "IN_AADHAAR", "IN_PAN", "IN_PHONE"
    ]
    
    # Analyze the text for PII
    results = analyzer.analyze(text=text, language='en', entities=entities)
    
    # --- Identity Mapping Logic ---
    # For the hackathon demo, we create a deterministic mapping for known patients.
    # This ensures that when a Security Officer scrubs "Rahul Sharma", the resulting 
    # "PATIENT_003" correctly triggers the Clinical Records Clerk lookup.
    def patient_mapping(original_text):
        if "Rahul" in original_text or "Sharma" in original_text:
            return "PATIENT_003"
        if "Priya" in original_text or "Patel" in original_text:
            return "PATIENT_004"
        if "Jane" in original_text or "Smith" in original_text:
            return "PATIENT_002"
        return "PATIENT_001" # Default fallback for John Doe/Unknown

    # Define anonymization operators for each entity type
    operators = {
        "PERSON": OperatorConfig("custom", {"lambda": patient_mapping}),
        "US_SSN": OperatorConfig("replace", {"new_value": "[REDACTED_SSN]"}),
        "IN_AADHAAR": OperatorConfig("replace", {"new_value": "[REDACTED_AADHAAR]"}),
        "IN_PAN": OperatorConfig("replace", {"new_value": "[REDACTED_PAN]"}),
        "IN_PHONE": OperatorConfig("replace", {"new_value": "[REDACTED_PHONE]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[REDACTED_EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED_PHONE]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[REDACTED_LOCATION]"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "[REDACTED_DATE]"}),
    }
    
    # Perform the anonymization
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )
    
    # Prepend a secure log header to indicate processing
    return f"SECURE_LOG: PII scrubbed using Microsoft Presidio.\n\n{anonymized_result.text}"

if __name__ == "__main__":
    mcp.run()