# Backend API Specification for ubounty CLI Integration (Simplified)

## Overview

The CLI authenticates using **GitHub tokens directly** - no need for a separate API key system!

### Authentication Flow

```
1. User runs: ubounty login
   → CLI performs GitHub device flow OAuth
   → Gets GitHub access token
   → Saves to ~/.config/ubounty/credentials.json

2. User runs: ubounty whoami
   → CLI sends GitHub token to ubounty.ai
   → Backend verifies token with GitHub API
   → Returns user info + wallet
```

**Key Benefits:**
- ✅ No new database tables needed
- ✅ No API key management UI needed
- ✅ GitHub handles expiration & revocation
- ✅ CLI already has device flow implemented

---

## Required API Endpoints

Only **2 endpoints** need to be modified!

### 1. Get User Settings

**GET** `/api/users/me/settings`

**Authentication**: Session (Web) OR Bearer Token (CLI)

**CLI Request:**
```http
GET /api/users/me/settings HTTP/1.1
Host: ubounty.ai
Authorization: Bearer gho_xxxxxxxxxxxxxxxxxxxx
User-Agent: ubounty-cli/0.1.0
```

**Response 200:**
```json
{
  "github_username": "1bcMax",
  "name": "Max",
  "avatar_url": "https://avatars.githubusercontent.com/u/123456",
  "email": "max@example.com",
  "wallet": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "network": "base",
    "chain_id": 8453,
    "status": "bound",
    "bound_at": "2025-01-10T12:00:00Z"
  }
}
```

**Response 401:**
```json
{
  "error": "Invalid or expired GitHub token",
  "message": "Please run 'ubounty login' to re-authenticate"
}
```

---

### 2. Update User Settings

**POST** `/api/users/me/settings`

**Authentication**: Session (Web) OR Bearer Token (CLI)

**CLI Request:**
```http
POST /api/users/me/settings HTTP/1.1
Host: ubounty.ai
Authorization: Bearer gho_xxxxxxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

**Response 200:**
```json
{
  "success": true,
  "wallet": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "network": "base",
    "chain_id": 8453,
    "updated_at": "2025-01-16T10:00:00Z"
  }
}
```

**Response 400:**
```json
{
  "error": "Invalid wallet address",
  "details": "Address must be 0x followed by 40 hex characters"
}
```

---

## Backend Implementation

### Authentication Middleware

Add this to `ubounty-web/utils/auth.py` (or update existing):

```python
import requests
from flask import request, session, jsonify
from functools import wraps

# Cache for GitHub token verification (avoid rate limits)
_github_token_cache = {}  # {token_prefix: (username, timestamp)}

def authenticate_request():
    """
    Unified authentication for Web (session) and CLI (GitHub token).

    Returns:
        username (str) or None
    """
    # Method 1: Session (Web UI)
    if "github_user" in session:
        return session["github_user"]["username"]

    # Method 2: GitHub Bearer token (CLI)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        github_token = auth_header[7:]  # Remove "Bearer "

        # Check cache first (avoid hitting GitHub API every time)
        token_prefix = github_token[:20]
        if token_prefix in _github_token_cache:
            cached_username, cached_time = _github_token_cache[token_prefix]
            # Cache valid for 5 minutes
            if (datetime.utcnow() - cached_time).seconds < 300:
                return cached_username

        # Verify with GitHub API
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=5
            )

            if response.status_code == 200:
                user_data = response.json()
                username = user_data["login"]

                # Cache the result
                _github_token_cache[token_prefix] = (username, datetime.utcnow())

                return username
        except Exception:
            pass

    return None


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = authenticate_request()
        if not username:
            return jsonify({
                "error": "Authentication required",
                "message": "Please log in via web or CLI"
            }), 401

        # Inject username into request
        request.current_user = username
        return f(*args, **kwargs)

    return decorated_function
```

---

### Update API Routes

Modify `ubounty-web/routes/api.py`:

```python
from utils.auth import authenticate_request, require_auth

# ============================================
# GET /api/users/me/settings
# ============================================

@api_bp.route("/users/me/settings", methods=["GET"])
@require_auth
def get_user_settings():
    """Get user settings - works for both Web and CLI."""
    username = request.current_user

    # Fetch from database
    user = supabase.table("users").select("*").eq(
        "github_username", username
    ).execute()

    if not user.data:
        return jsonify({"error": "User not found"}), 404

    user_data = user.data[0]

    return jsonify({
        "github_username": user_data["github_username"],
        "name": user_data.get("name"),
        "avatar_url": user_data.get("avatar_url"),
        "email": user_data.get("email"),
        "wallet": {
            "address": user_data.get("wallet_address"),
            "network": NETWORK,  # from config
            "chain_id": get_chain_id(),
            "status": "bound" if user_data.get("wallet_address") else "not_bound",
            "bound_at": user_data.get("updated_at") if user_data.get("wallet_address") else None
        }
    }), 200


# ============================================
# POST /api/users/me/settings
# ============================================

@api_bp.route("/users/me/settings", methods=["POST"])
@require_auth
def update_user_settings():
    """Update user settings - works for both Web and CLI."""
    username = request.current_user
    data = request.get_json()

    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    # Validate address format
    import re
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        return jsonify({
            "error": "Invalid wallet address",
            "details": "Address must be 0x followed by 40 hex characters"
        }), 400

    # Optional: Validate checksum (requires eth-utils)
    try:
        from eth_utils import is_checksum_address, to_checksum_address
        if wallet_address != wallet_address.lower() and wallet_address != wallet_address.upper():
            if not is_checksum_address(wallet_address):
                return jsonify({
                    "error": "Invalid checksum",
                    "details": "Please use a properly checksummed address"
                }), 400
        wallet_address = to_checksum_address(wallet_address)
    except ImportError:
        # eth-utils not installed, skip checksum validation
        pass

    # Update database
    supabase.table("users").update({
        "wallet_address": wallet_address,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("github_username", username).execute()

    return jsonify({
        "success": True,
        "wallet": {
            "address": wallet_address,
            "network": NETWORK,
            "chain_id": get_chain_id(),
            "updated_at": datetime.utcnow().isoformat()
        }
    }), 200
```

---

## Rate Limiting

Add rate limiting to prevent abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Apply to endpoints
@api_bp.route("/users/me/settings", methods=["GET"])
@limiter.limit("60 per minute")
@require_auth
def get_user_settings():
    pass

@api_bp.route("/users/me/settings", methods=["POST"])
@limiter.limit("10 per minute")  # Stricter for writes
@require_auth
def update_user_settings():
    pass
```

---

## Optional: Audit Logging

If you want to track CLI usage (optional):

```python
def log_cli_request():
    """Log CLI requests for analytics."""
    if request.headers.get("User-Agent", "").startswith("ubounty-cli"):
        # Log to database or analytics service
        logger.info(f"CLI request: {request.current_user} {request.method} {request.path}")
```

---

## Testing

### 1. Test with curl

```bash
# Get user settings
curl -H "Authorization: Bearer gho_your_github_token" \
     https://ubounty.ai/api/users/me/settings

# Update wallet
curl -X POST \
     -H "Authorization: Bearer gho_your_github_token" \
     -H "Content-Type: application/json" \
     -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"}' \
     https://ubounty.ai/api/users/me/settings
```

### 2. Test with CLI

```bash
# Login
ubounty login

# Check status
ubounty whoami

# Bind wallet
ubounty wallet bind 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

# Check again
ubounty wallet status
```

---

## Security Considerations

### ✅ Handled

1. **Token Verification**: Every request validates GitHub token with GitHub API
2. **Caching**: Results cached for 5 minutes to avoid rate limits
3. **Rate Limiting**: Prevents abuse
4. **Address Validation**: Format checking on server side
5. **HTTPS**: All API calls over HTTPS

### ⚠️ Notes

1. **GitHub Rate Limit**: GitHub API allows 5000 requests/hour for authenticated requests
   - With caching (5 min), 60 req/min = max 3600 req/hour - well under limit

2. **Token Expiration**: GitHub tokens can expire or be revoked
   - CLI user will get 401 error
   - Just run `ubounty login` again

3. **Token Storage**: GitHub token stored locally in `~/.config/ubounty/`
   - File permissions: 0600 (user read/write only)
   - User is responsible for keeping their machine secure

---

## Deployment Checklist

Backend changes (ubounty-web):

- [ ] Add/update `authenticate_request()` function in `utils/auth.py`
- [ ] Add/update `require_auth` decorator
- [ ] Update `GET /api/users/me/settings` to use `@require_auth`
- [ ] Update `POST /api/users/me/settings` to use `@require_auth`
- [ ] Add wallet address validation
- [ ] Add rate limiting
- [ ] (Optional) Add audit logging for CLI requests
- [ ] Test with curl
- [ ] Test with CLI
- [ ] Deploy to production

No database changes needed! ✅

---

## Summary

**Total changes needed:**
- ✅ 1 new function: `authenticate_request()`
- ✅ 2 endpoints updated: GET + POST `/api/users/me/settings`
- ✅ No new tables
- ✅ No API key management UI

**Time estimate**: 1-2 hours

Much simpler than the original API key system! 🎉
