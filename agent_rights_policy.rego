package agent.authz

# Default deny: Start with Zero Trust
default allow = False

# Rule: Allow the Agent to access the Finance API ONLY if:
# 1. It is a 'Chained' token (has an 'act' claim)
# 2. The original human 'sub' is a VP or Architect
# 3. The scope is limited to 'read'

allow {
    input.token.act.type == "AI_Agent"
    input.token.sub == "alexey@enterprise.com" # Example check
    input.token.scp[_] == "read:research_data"
    not token_is_expired
}

token_is_expired {
    input.token.exp < time.now_ns() / 1000000000
}
