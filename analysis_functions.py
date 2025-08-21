import json
import re
import os
import google.generativeai as genai
from typing import Dict, List, Tuple, Any

# A curated set of profane words for pattern matching.
PROFANITY_WORDS = {
    'damn', 'hell', 'crap', 'stupid', 'idiot', 'moron', 'dumb', 'shut up',
    'bullshit', 'bs', 'wtf', 'pissed', 'suck', 'sucks', 'fucked',
    'screwed', 'bastard', 'bitch', 'asshole', 'jerk', 'loser'
}

# Pre-defined keywords for compliance checking.
SENSITIVE_KEYWORDS = {
    'balance', 'account number', 'payment history', 'transaction', 'credit score', 
    'debt amount', 'owe', 'outstanding', 'ssn', 'social security', 'bank account', 
    'routing number'
}
VERIFICATION_KEYWORDS = {
    'date of birth', 'dob', 'address', 'zip code', 'social security number',
    'mother maiden name', 'security question', 'verify', 'confirm your identity'
}

def analyze_profanity_pattern(data: List[Dict[str, Any]]) -> Tuple[bool, bool, List[Dict]]:
    """Analyzes conversation for profanity using direct keyword matching."""
    profanity_details = []
    agent_profanity = False
    customer_profanity = False

    for entry in data:
        text = entry.get('text', '').lower()
        words = set(re.findall(r'\b\w+\b', text))
        
        # Check for intersection between words in text and profanity list
        if PROFANITY_WORDS.intersection(words):
            speaker = entry.get('speaker', '').lower()
            profanity_details.append({
                'speaker': speaker,
                'text': entry.get('text', ''),
                'timestamp': f"{entry.get('stime', 0)}s - {entry.get('etime', 0)}s",
            })
            if 'agent' in speaker:
                agent_profanity = True
            else:
                customer_profanity = True
    
    return agent_profanity, customer_profanity, profanity_details

def analyze_compliance_pattern(data: List[Dict[str, Any]]) -> Tuple[bool, List[Dict]]:
    """Analyzes for compliance violations by checking if sensitive info was shared before verification."""
    violation_details = []
    verified = False

    for entry in data:
        speaker = entry.get('speaker', '').lower()
        text = entry.get('text', '').lower()

        if 'agent' in speaker:
            # If any verification keyword is found, the agent is considered verified for the rest of the call.
            if not verified and any(keyword in text for keyword in VERIFICATION_KEYWORDS):
                verified = True

            # Check for sensitive info sharing; if not verified, it's a violation.
            matched_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in text]
            if matched_keywords and not verified:
                violation_details.append({
                    'text': entry.get('text', ''),
                    'timestamp': f"{entry.get('stime', 0)}s - {entry.get('etime', 0)}s",
                    'keywords_found': matched_keywords,
                })

    # A violation occurred if any such details were logged.
    violation_found = len(violation_details) > 0
    return violation_found, violation_details

def analyze_with_llm(data: List[Dict[str, Any]], entity: str, api_key: str) -> Dict[str, Any]:
    """Analyzes conversation using the Gemini generative AI model."""
    if not api_key:
        return {"error": "Gemini API key is not set."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        return {"error": f"Error configuring Gemini API: {e}"}

    conversation_str = "\n".join(
        f"{item['speaker']} ({item.get('stime', 0)}s): {item['text']}" for item in data
    )
    
    # Prompts are structured for clear instructions and JSON output.
    prompts = {
        'Profanity Detection': f"""
        Analyze this customer service conversation for profane or inappropriate language.
        Look for explicit profanity, unprofessional language, and disrespectful terms.
        Conversation: {conversation_str}
        Respond with JSON: {{
            "agent_profanity": boolean,
            "customer_profanity": boolean,
            "agent_examples": ["specific profane text from agent"],
            "customer_examples": ["specific profane text from customer"]
        }}
        """,
        'Privacy and Compliance Violation': f"""
        Analyze this debt collection call for compliance violations. A violation occurs if an agent
        shares sensitive info (account balance, SSN, etc.) BEFORE verifying the customer's identity
        (by asking for DOB, address, etc.).
        Conversation: {conversation_str}
        Respond with JSON: {{
            "compliance_violation": boolean,
            "verification_attempted": boolean,
            "violation_examples": ["specific violations"],
            "verification_examples": ["verification attempts"]
        }}
        """
    }

    prompt = prompts.get(entity)
    if not prompt:
        return {"error": "Invalid entity for LLM analysis."}

    try:
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
        )
        # Clean response to ensure it's valid JSON
        cleaned_text = re.sub(r'```json\s*|\s*```', '', response.text.strip(), flags=re.DOTALL)
        return json.loads(cleaned_text)

    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON from LLM response."}
    except Exception as e:
        return {"error": f"An error occurred with the Gemini API: {e}"}