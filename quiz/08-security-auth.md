# Module 8 — Security, Authentication & Authorization — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** JWT Structure
**Type:** Multiple Choice

What are the three parts of a JWT (JSON Web Token)?

A) Header, Encrypted Data, Signature
B) Header, Payload, Signature
C) Token ID, User ID, Expiration
D) Algorithm, Claims, Secret

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A JWT consists of three Base64URL-encoded segments separated by dots: the header (algorithm and token type), the payload (claims like sub, exp, iat), and the signature (verifies the token hasn't been tampered with). The header and payload are only Base64-encoded, not encrypted — they can be decoded by anyone.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 2 🟢
**Topic:** HTTPS / TLS
**Type:** Open-Ended

Why is it important to use HTTPS (TLS) for all API traffic, even for public data?

<details>
<summary>Answer & Explanation</summary>

**Answer:** TLS provides three protections: **confidentiality** (encryption prevents eavesdropping), **integrity** (MAC ensures data isn't tampered in transit), and **authentication** (server certificate verified by a CA prevents man-in-the-middle attacks). Even for public data, without TLS an attacker can inject malicious content, steal session cookies, or perform downgrade attacks.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 3 🟢
**Topic:** OAuth2 Roles
**Type:** Multiple Choice

In OAuth2, which entity issues tokens to the client application?

A) Resource Server
B) Resource Owner
C) Authorization Server
D) Client Application

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** The Authorization Server issues tokens after authenticating the resource owner and obtaining authorization. The Resource Server hosts the protected resources and validates tokens. The Resource Owner (typically the end-user) grants permission. The Client Application makes requests on behalf of the resource owner.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 4 🟢
**Topic:** RBAC Basics
**Type:** Multiple Choice

In Role-Based Access Control (RBAC), what is a "role"?

A) A specific permission like "delete_user"
B) A collection of permissions assigned to users based on their function
C) A group of API endpoints
D) An individual user's clearance level

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** In RBAC, a role is a named collection of permissions (e.g., "admin" has create/read/update/delete, "viewer" has read-only). Users are assigned to roles rather than having individual permissions. This simplifies management — you change the role definition, and all users with that role are updated.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 5 🟢
**Topic:** CSRF
**Type:** Open-Ended

What is a CSRF (Cross-Site Request Forgery) attack and what is one common mitigation?

<details>
<summary>Answer & Explanation</summary>

**Answer:** CSRF tricks an authenticated user into performing an unintended action on a web application (e.g., transferring money, changing email) by embedding a forged request in an image tag or form. The browser automatically includes the user's cookies, making the request appear legitimate. Common mitigations: CSRF tokens (synchronizer token pattern), SameSite cookies (Strict or Lax), or checking Origin/Referer headers.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 6 🟢
**Topic:** Rate Limiting Purpose
**Type:** Open-Ended

Why do APIs implement rate limiting?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Rate limiting protects the API from abuse and ensures fair usage. It prevents a single client from overwhelming the system (denial of service, accidental or intentional), reduces cost from excessive compute, and maintains quality of service for all users. Common algorithms: token bucket, leaky bucket, fixed window, sliding window log.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 7 🟢
**Topic:** Password Hashing
**Type:** Multiple Choice

Which of the following is the most appropriate algorithm for hashing user passwords?

A) MD5
B) SHA-256
C) bcrypt
D) Base64

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** bcrypt is designed specifically for password hashing — it is deliberately slow, includes a salt by default, and has a configurable cost factor. MD5 and SHA-256 are fast general-purpose hash functions unsuitable for passwords (trivially brute-forced with GPUs). Base64 is encoding, not hashing.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 8 🟢
**Topic:** Authentication vs Authorization
**Type:** Multiple Choice

What is the difference between authentication and authorization?

A) They are synonyms
B) Authentication verifies identity; authorization determines what an identity can do
C) Authorization verifies identity; authentication determines permissions
D) Authentication encrypts data; authorization decrypts data

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Authentication (authn) answers "who are you?" — verifying identity via credentials (password, biometric, MFA). Authorization (authz) answers "what are you allowed to do?" — checking permissions after identity is established. You must authenticate before you can be authorized.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 9 🟡
**Topic:** OAuth2 Authorization Code Flow
**Type:** Open-Ended

Describe the OAuth2 Authorization Code flow. Why is the authorization code (not the access token) returned directly to the frontend?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. User clicks "Login with Provider" → frontend redirects to the authorization server's `/authorize` endpoint with client_id, redirect_uri, and response_type=code.
2. User authenticates and consents → authorization server redirects back with a short-lived **authorization code** in the URL query string.
3. Frontend sends the authorization code to the backend (not the authorization server directly).
4. Backend exchanges the code + client_secret for an access token (and optionally refresh token) via a server-to-server POST to `/token`.

The authorization code is returned to the frontend (redirect URL) rather than directly to the backend because the frontend initiates the flow. The code is single-use, short-lived, and useless without the client_secret (which only the backend holds). This prevents the access token from being exposed in the browser URL or history.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 10 🟡
**Topic:** PKCE
**Type:** Multiple Choice

What problem does PKCE (Proof Key for Code Exchange) solve in OAuth2?

A) It replaces the need for refresh tokens
B) It prevents authorization code interception attacks, especially in mobile and SPA clients
C) It allows the authorization server to skip user consent
D) It enables client credentials grant without a secret

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** PKCE (pronounced "pixie") protects public clients (mobile apps, SPAs) that cannot securely store a client_secret. The client generates a `code_verifier` (random string) and sends its SHA-256 hash (`code_challenge`) during the authorization request. When exchanging the code, the client sends the raw `code_verifier`, and the server verifies it matches the challenge. Even if an attacker intercepts the authorization code, they can't exchange it without the verifier.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 11 🟡
**Topic:** OIDC vs OAuth2
**Type:** Open-Ended

How does OpenID Connect (OIDC) extend OAuth2? What is an ID Token and how does it differ from an Access Token?

<details>
<summary>Answer & Explanation</summary>

**Answer:** OIDC adds an authentication (identity) layer on top of OAuth2's authorization framework. OIDC introduces the **ID Token** — a JWT containing identity claims (sub, name, email, picture, etc.) about the end-user. The Access Token grants access to resources; the ID Token proves who the user is. OIDC also defines the `/userinfo` endpoint for fetching additional claims, and the `openid` scope must be included in the request.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 12 🟡
**Topic:** mTLS
**Type:** Open-Ended

What is mutual TLS (mTLS) and in what scenarios is it commonly used?

<details>
<summary>Answer & Explanation</summary>

**Answer:** In standard TLS, only the server presents a certificate to prove its identity. In mTLS, both the client and server present certificates, creating **mutual authentication**. mTLS is commonly used in: service mesh communication (e.g., Istio automatically issues certificates to every sidecar), zero-trust networks, B2B API integrations where both parties need to verify each other, and IoT device authentication.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 13 🟡
**Topic:** JWKS
**Type:** Calculation

A JWT is signed with RS256 (RSA with SHA-256). The verification process needs the public key. What is the JWKS (JSON Web Key Set) and how does the verifier use it? If the JWKS endpoint returns a set with 3 keys (kid: key1, key2, key3), how does the verifier know which key to use?

<details>
<summary>Answer & Explanation</summary>

**Answer:** JWKS is a JSON document that contains a set of public keys (each with a unique `kid` — Key ID). The JWT header includes a `kid` field that matches one of the keys in the JWKS. The verifier:
1. Reads the `kid` from the JWT header.
2. Fetches and caches the JWKS from the well-known endpoint (e.g., `https://auth.example.com/.well-known/jwks.json`).
3. Finds the key whose `kid` matches.
4. Uses that key's `n` (modulus) and `e` (exponent) to verify the signature.

Key rotation: the authorization server adds new keys and removes old ones. Clients should refresh the JWKS periodically (typically every hour).

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 14 🟡
**Topic:** Replay Attacks
**Type:** Open-Ended

What is a replay attack on an API? How does including a nonce (number used once) or a timestamp in the request help prevent it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A replay attack occurs when an attacker intercepts a valid API request (including authentication headers) and re-sends it to the server, causing duplicate or unauthorized actions. Mitigation: 
- **Nonce:** A unique, single-use random string per request. The server tracks used nonces and rejects duplicates.
- **Timestamp:** Include the current Unix timestamp in the request. The server rejects requests outside a small time window (e.g., ±5 minutes).
- **Combined approach:** Nonce + timestamp is most robust — the nonce prevents replay within the window, the timestamp limits the window size.

**Reference:** Docs/08-security-auth.md
</details>

---

## Question 15 🔴
**Topic:** DPoP (Demonstration of Proof-of-Possession)
**Type:** Open-Ended

What is DPoP and what attack does it prevent that standard OAuth2 bearer tokens are vulnerable to?

<details>
<summary>Answer & Explanation</summary>

**Answer:** DPoP (Demonstration of Proof-of-Possession) binds an access token to a specific client by requiring the client to prove possession of a private key. The client generates a key pair, sends the public key thumbprint to the authorization server during token issuance (embedded in the token), and signs each API request with the private key using a DPoP header.

**Attack prevented:** **Bearer token theft.** With standard bearer tokens, if an attacker steals the access token (via MITM, log leakage, XSS), they can use it from any device. DPoP makes the stolen token useless without the corresponding private key, which never leaves the legitimate client. It's especially important for high-value APIs (banking, healthcare).

**Reference:** Docs/08-security-auth-advanced.md
</details>

---

## Question 16 🔴
**Topic:** API Gateway Auth Design
**Type:** Whiteboard

Design a centralized authentication and authorization layer for a platform with 50+ microservices, supporting both user-facing APIs (JWT from OIDC provider) and machine-to-machine APIs (client credentials + mTLS). How do you handle token validation efficiently without making every service call the auth server? How do you handle permissions that vary per request (e.g., "can user X view document Y")?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Centralized API Gateway** (e.g., Envoy, Kong, NGINX + auth plugin):
1. **User-facing:** Gateway validates the JWT (signature via cached JWKS, expiry, issuer, audience). Extracts claims (user_id, roles) and injects them as trusted headers (X-User-Id, X-Roles) to downstream services.
2. **Machine-to-machine:** Gateway validates the client certificate (mTLS) and maps the certificate CN to a service identity. Then validates a client-credentials JWT with scopes.
3. **Efficiency:** JWKS is cached and refreshed hourly. Token validation is at the gateway — downstream services trust the injected headers (only accepting them from localhost/local network, stripping from external requests).
4. **Fine-grained authorization (ABAC):** The gateway handles coarse checks (is this user authenticated? Has scope?). For resource-level permissions (document ownership), each service embeds a small authorization engine (e.g., OPA, Casbin) that evaluates policy against the request context. The policy can be pulled from a central policy store and cached locally.

**Reference:** Docs/08-security-auth-advanced.md
</details>

---

## Question 17 🔴
**Topic:** OAuth2 Token Refresh Race Condition
**Type:** Debug

A mobile app using OAuth2 Authorization Code + PKCE experiences intermittent 401 errors. The access token expires in 15 minutes. Multiple concurrent API calls are made. Logs show that when the client tries to refresh the token (POST /token with refresh_token), some API calls still fail with 401 after the refresh completes. What is the cause and the fix?

<details>
<summary>Answer & Explanation</summary>

**Answer:** **Race condition:** Multiple concurrent API calls detect the token is expired (or about to expire) and each independently attempts to refresh the token. The first refresh succeeds (issuing a new access_token and refresh_token). The subsequent refresh attempts may fail because:
1. The old refresh token was rotated (spent) by the first refresh — OAuth2 best practice is single-use refresh tokens.
2. The old access token was invalidated by the first refresh.
3. Meanwhile, API calls using the old access token fail with 401.

**Fix:** Implement a token refresh lock/mutex in the client. When one request detects an expired token, it acquires a lock, refreshes, and caches the new token. All other concurrent requests wait on the lock and then use the fresh token. Additionally, use a buffer (refresh at 10 min even though token expires at 15 min) and queue API calls during refresh.

**Reference:** Docs/08-security-auth-advanced.md
</details>

---

## Question 18 🔴
**Topic:** RBAC vs ABAC Trade-offs
**Type:** Whiteboard

Design the authorization system for a multi-tenant SaaS document management platform. There are 10,000+ tenants, each with custom roles. Some permissions are context-dependent (e.g., "a manager can view documents in their department but not in other departments"). Compare RBAC, ABAC, and a hybrid approach. Which would you choose and why?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**RBAC alone:** Well-defined roles (Admin, Editor, Viewer). But with 10,000 tenants × custom roles, role explosion occurs. Can't express context ("own department only").

**ABAC alone:** Policies based on attributes (user.department = document.department). Highly flexible but can become complex to debug, and performance depends on policy evaluation speed.

**Hybrid (RBAC + ABAC):** Start with RBAC for coarse permissions (role determines baseline: Admin has full access, Editor can write, Viewer can read). Add ABAC for fine-grained constraints (e.g., "Editor can only edit documents where user.department == doc.department AND doc.status != 'archived'"). This keeps role management simple while enabling context-aware rules.

**Implementation:** Use a policy engine like OPA (Rego) or Casbin. Store role-to-permission mappings per tenant in a database. Cache compiled policies. Evaluate at the API gateway for coarse checks and at the service layer for resource-level checks.

**Reference:** Docs/08-security-auth-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Secrets Management Architecture
**Type:** Whiteboard

Design a secrets management system for a 500-microservice deployment. Services need database credentials, API keys, and TLS certificates. Requirements: automatic rotation every 24 hours, audit log of all secret access, zero downtime during rotation, and no hardcoded secrets in config files or CI/CD pipelines.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Vault-based architecture** (HashiCorp Vault):
1. **Dynamic secrets:** Vault generates short-lived database credentials on-demand (e.g., a 24-hour password for a specific service to access its database). Each service authenticates to Vault (via Kubernetes service account JWT, mTLS, or AWS IAM) and requests credentials. Vault issues a lease; when it expires, the credentials are revoked.
2. **Rotation:** Vault's built-in rotation rotates the root/admin credentials, while dynamic secrets are short-lived by default. For TLS certificates, use Vault's PKI backend with automatic renewal (e.g., cert-manager on Kubernetes, or Vault agent sidecar).
3. **Audit:** Vault logs every read, write, and authentication event. Send audit logs to a SIEM.
4. **No hardcoded secrets:** Secrets are never in config files. Sidecars (Vault Agent, Bank-Vaults, or `envconsul`) inject secrets as environment variables or files at pod startup. CI/CD pipelines authenticate to Vault using ephemeral tokens.
5. **Zero-downtime rotation:** Use a grace period where old and new credentials coexist. Database connection pools re-establish connections with new credentials before dropping the old ones.

**Reference:** Docs/08-security-auth-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Rate Limiting at Global Scale
**Type:** Calculation

Design a rate limiter for a global API gateway spanning 5 regions. Each region has 20 gateway nodes. The limit is 1000 requests/second per API key. The rate limiter must be accurate within ±5%. Compare a centralized (Redis) vs distributed (local sliding window with gossip) approach. Calculate the error in a local approach without synchronization and explain how you would tune it.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Centralized (Redis cluster):** A Redis cluster across regions (using CRDT-based replication or a single leader in one region with followers in others). Each request atomically increments a counter. Pro: exact, within ±1%. Con: adds 2-5ms latency per request, Redis is a single point of failure, cross-region network costs.

**Distributed (local sliding window):** Each gateway node maintains a local in-memory sliding window counter for each API key. No cross-node synchronization. For 1000 req/s across 5 regions × 20 nodes = 100 nodes, each node handles ~10 req/s on average (1000/100). Local window can allow up to 1000 requests/node (if all traffic hits one node). Error = ~99x over-limit in worst case. To bound error: each node gets a **quota** = 1000 / 100 × burst_factor. If burst_factor = 1.5, each node allows 15 req/s. Buried error allows at most 1500 req/s globally (50% over). Reduce windows to 100ms granularity.

**Recommended hybrid:** Use a local token-bucket per node (low latency, no network calls) with periodic (every 1s) synchronization to a global Redis counter. Each node has a quota based on estimated share. If global count is exceeded, new tokens stop being issued until next sync. This gives <5% error with ~1ms p99 added latency.

**Reference:** Docs/08-security-auth-advanced.md
</details>
