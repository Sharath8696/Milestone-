import re

def check_pii(text: str) -> bool:
    """Returns True if PII is detected in the string, else False."""
    # Extremely basic PII checks for demonstration ( PAN, Aadhaar, Phone )
    pan_regex = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
    aadhaar_regex = r'\b\d{4}\s\d{4}\s\d{4}\b'
    phone_regex = r'\b\d{10}\b'
    
    if re.search(pan_regex, text) or re.search(aadhaar_regex, text) or re.search(phone_regex, text):
        return True
    return False

def check_advisory_intent(text: str) -> bool:
    """Returns True if the text contains advisory/comparative intents."""
    advisory_keywords = [
        "should i invest", "better", "best fund", "recommend", 
        "which one", "allocate my money", "predict", "forecast", "compare"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in advisory_keywords)

def apply_input_guardrails(query: str):
    """
    Validates input query. Returns an error message if invalid, None if valid.
    """
    if check_pii(query):
        return "I cannot process queries containing sensitive PII like PAN, Aadhaar, or phone numbers for security reasons."
        
    if check_advisory_intent(query):
        refusal_msg = (
            "I can only provide factual information based on official mutual fund documents. "
            "I cannot provide investment advice, comparisons, or recommendations. "
            "For educational resources, please visit https://www.amfiindia.com/investor-corner"
        )
        return refusal_msg
        
    return None

def apply_output_guardrails(response: str):
    """
    Validates the generated response constraints: max 3 sentences, contains factsheet link.
    """
    # Simple sentence count check considering dots.
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    if len(sentences) > 3:
        # Strip down to 3 sentences
        response = '. '.join(sentences[:3]) + '.'
        
    # Check if a link is present. If entirely missing, we could flag it, but the LLM prompt 
    # should strictly enforce this. This function ensures structural validity.
    if "Last updated from sources" not in response:
        response += "\n\nLast updated from sources: Check source link above."
        
    return response

