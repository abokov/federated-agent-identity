import requests
import json
import time
import base64

# Note: In a real environment, use PyJWT for actual signing. 
# We use a mock formatter here for zero-dependency PoC execution.

# =============================================================================
# STRATEGIC CAPABILITY: RFC 8693 Token Exchange (Agent Delegation)
# =============================================================================
def mock_idp_token_exchange(subject_token, actor_client_id, requested_scope, telemetry_context):
    print(f"\n[INFO] {actor_client_id} requesting downstream delegation...")
    print("[POLICY_ENGINE] Evaluating contextual risk via Open Policy Agent (OPA)...")

    # 1. Build the decision payload for OPA
    opa_payload = {
        "input": {
            "subject": {"status": "active", "id": subject_token["sub"]},
            "actor": {"client_id": actor_client_id},
            "requested_scope": requested_scope,
            "context": telemetry_context
        }
    }

    # 2. Query the Local OPA Server (assumes OPA is running on port 8181)
    try:
        response = requests.post("http://localhost:8181/v1/data/agent/authz", json=opa_payload)
        decision = response.json().get("result", {})
    except requests.exceptions.ConnectionError:
        print("[ERROR] OPA Server not running. Start it with: opa run --server ./agent_rights_policy.rego")
        return None

    # 3. Enforce the Zero Trust Decision
    if not decision.get("allow", False):
        print(f"[IDP-DENY] Token Exchange Rejected. Risk Level: {decision.get('risk_level')}")
        return None

    print(f"[POLICY_ENGINE] Risk score: {decision.get('risk_level')}. Approved for scope: '{requested_scope}'.")
    
    # 4. Mint the Delegated Token (RFC 8693 compliant structure)
    # The 'act' (actor) claim cryptographically links the Agent to the Human.
    header = {"alg": "RS256", "typ": "at+jwt"}
    payload = {
        "iss": "https://auth.enterprise.okta.local",
        "sub": subject_token["sub"],              # The original human user
        "aud": "urn:okta:resource:database_agent",
        "exp": int(time.time()) + 300,            # 5-minute ephemeral lifespan
        "scope": requested_scope,
        "act": {                                  # The RFC 8693 Actor Claim
            "sub": actor_client_id
        }
    }

    # Mock Base64 encoding for the PoC visual
    enc_hdr = base64.b64encode(json.dumps(header).encode()).decode().rstrip("=")
    enc_pay = base64.b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    mock_jwt = f"{enc_hdr}.{enc_pay}.[MOCK_CRYPTOGRAPHIC_SIGNATURE]"
    
    print("[IDP-ALLOW] Token Exchange Successful (RFC 8693).")
    return mock_jwt

# =============================================================================
# SIMULATION ENGINE
# =============================================================================
if __name__ == "__main__":
    # 1. The Human authenticates to Okta (Standard OIDC)
    human_jwt = {"sub": "alexey.bokov@enterprise.com", "role": "VP_Strategy"}
    
    # 2. The Human triggers the Research Agent, passing their JWT.
    # The Research Agent now needs to call the Database Agent, but it needs 
    # a highly scoped, safe token to do so.
    
    # Telemetry data collected by the API Gateway
    agent_context = {
        "pii_detected": False,
        "confidence_score": 0.92,
        "anomaly_detected": False
    }

    # 3. Execute the Token Exchange
    actor_token = mock_idp_token_exchange(
        subject_token=human_jwt,
        actor_client_id="client_research_agent_01",
        requested_scope="read:anonymized_data",
        telemetry_context=agent_context
    )

    if actor_token:
        print(f"[IDP] Issued Actor Token: {actor_token[:40]}... (truncated)")
        print("[INFO] Database_Agent executing query with delegated, ephemeral authority.")
        
        # Flex: Show the decoded payload so recruiters see the RFC 8693 structure
        payload_b64 = actor_token.split('.')[1] + "=="
        decoded_payload = json.loads(base64.b64decode(payload_b64).decode())
        print(f"\n[DECODED JWT PAYLOAD]:\n{json.dumps(decoded_payload, indent=2)}")
