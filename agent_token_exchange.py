import jwt  # Using PyJWT for demonstration
import datetime

# 1. The Human "Subject" Token (The 'Who')
human_token = {
    "sub": "alexey@enterprise.com",
    "role": "Principal_Architect",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

# 2. The Agent "Actor" Identity (The 'What')
agent_id = "Research-Agent-01"

def exchange_token(subject_token, actor_id):
    """
    Implements a simplified RFC 8693 Token Exchange.
    Wraps the human identity inside an 'act' (actor) claim for the agent.
    """
    chained_token = {
        "sub": subject_token["sub"],  # Original Human
        "act": {
            "sub": actor_id,           # The Agent doing the work
            "type": "AI_Agent",
            "trust_domain": "okta.internal"
        },
        "scp": ["read:research_data"], # Scoped rights (Least Privilege)
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15) # Short-lived
    }
    
    # In a real scenario, this would be signed by Okta/SPIRE
    return jwt.encode(chained_token, "REPLACE_WITH_SECURE_PRIVATE_KEY", algorithm="RS256")

print("Generating Chained Federated Token for Agent...")
token = exchange_token(human_token, agent_id)
print(f"Generated Chained Token: {token[:50]}...")
