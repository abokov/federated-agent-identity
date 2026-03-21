package agent.authz

import future.keywords.in

# ---------------------------------------------------------------------------
# STRATEGIC THESIS: Default Deny. 
# AI Agents operate in a Zero Trust environment. No standing privileges.
# ---------------------------------------------------------------------------
default allow = false
default risk_level = "HIGH"

# ---------------------------------------------------------------------------
# The core authorization rule for Agent-to-Agent (A2A) delegation
# ---------------------------------------------------------------------------
allow {
    # 1. Verify the Human Subject is active/valid
    input.subject.status == "active"
    
    # 2. Ensure the requesting Agent is an approved internal application
    input.actor.client_id in ["client_research_agent_01", "client_summary_agent_02"]
    
    # 3. Calculate dynamic risk (Must be LOW to proceed)
    risk_level == "LOW"
    
    # 4. Ensure requested scope is within the actor's bounded context
    input.requested_scope in allowed_scopes[input.actor.client_id]
}

# ---------------------------------------------------------------------------
# Dynamic Risk Assessment Logic
# (e.g., Did Okta's AI Security gateway detect prompt injection or PII?)
# ---------------------------------------------------------------------------
risk_level = "LOW" {
    input.context.pii_detected == false
    input.context.confidence_score > 0.85
    input.context.anomaly_detected == false
}

# ---------------------------------------------------------------------------
# Role-Based Scope Bounding per Agent
# ---------------------------------------------------------------------------
allowed_scopes = {
    "client_research_agent_01": ["read:anonymized_data", "write:summary_cache"],
    "client_summary_agent_02": ["read:summary_cache", "email:send_draft"]
}
