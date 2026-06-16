# Authentication & Authorization – A Beginner's Guide

> This guide explains how systems verify who you are (authentication) and what you are allowed to do (authorization) in a distributed, API-driven world.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

---

## Table of Contents

1. [Authentication vs Authorization](#1-authentication-vs-authorization)
2. [Stateful Sessions: The Hotel Key Card](#2-stateful-sessions-the-hotel-key-card)
3. [Stateless Tokens (JWT): The Passport](#3-stateless-tokens-jwt-the-passport)
4. [How JWT Signatures Work](#4-how-jwt-signatures-work)
5. [OAuth 2.0: Delegating Access](#5-oauth-20-delegating-access)
6. [OIDC: Proving Who You Are](#6-oidc-proving-who-you-are)
7. [Service-to-Service Security with mTLS](#7-service-to-service-security-with-mtls)
8. [Common Disasters and How to Avoid Them](#8-common-disasters-and-how-to-avoid-them)
9. [Putting It All Together — A User Logs In](#9-putting-it-all-together--a-user-logs-in)
10. [Glossary of Technical Terms](#10-glossary-of-technical-terms)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. Authentication vs Authorization

These two terms are often confused. They are different:

| Term | Short | Answers | Analogy |
|------|-------|---------|---------|
| **Authentication** | AuthN | "Who are you?" | Showing your ID at airport security |
| **Authorization** | AuthZ | "What are you allowed to do?" | Your boarding pass says you can board the flight but not enter the cockpit |

A system must always do **AuthN first**, then **AuthZ**. There is no point checking permissions if you do not know who the user is.

---

## 2. Stateful Sessions: The Hotel Key Card

**How it works:**

1. The user logs in with username and password.
2. The server creates a session record (a row in a database or a key in Redis) and generates a random **session ID**.
3. The server sends the session ID to the client as a cookie.
4. On every subsequent request, the client sends the cookie. The server looks up the session ID in its database to verify the user.

**Analogy:** This is like a hotel key card. The front desk (server) keeps a record of which room you are in. Every time you enter the building, you hand over your card, and the clerk checks the computer to confirm you are a guest.

**Pros:**
- Easy to revoke — delete the session record and the user is instantly logged out.
- Simple to implement for traditional web applications.

**Cons:**
- The server must store every active session. If you have 10 million users, you need 10 million session entries.
- Cannot scale horizontally without a shared session store (all servers must access the same Redis/database).

---

## 3. Stateless Tokens (JWT): The Passport

**JWT** stands for **JSON Web Token**. It is a compact, self-contained way to transmit identity information.

**How it works:**

1. The user logs in with username and password.
2. The server creates a JWT containing the user's ID, permissions, and an expiration time.
3. The server signs the JWT with a private key (like a digital signature) and sends it to the client.
4. On every subsequent request, the client sends the JWT. The server verifies the signature using the corresponding public key — **no database lookup required**.

**Analogy:** A JWT is like a passport. It contains your photo, your name, and an official stamp (signature) that any border agent can verify using a public document (the signing key). The agent does not need to call your home country to confirm you are who you say you are — the cryptographic signature proves it.

**Pros:**
- **Stateless:** The server does not need to store anything. Scales horizontally instantly.
- **Decentralized verification:** Any service with the public key can verify a JWT.

**Cons:**
- **Cannot be revoked.** If a JWT is stolen, it is valid until it expires (unless you maintain a denylist, which defeats the stateless purpose).
- **Token size** is larger than a session ID.

| Feature | Session (Stateful) | JWT (Stateless) |
|---------|-------------------|-----------------|
| Server storage | Yes, per-session | None |
| Scalability | Need shared session store | Horizontally scalable out of the box |
| Revocation | Instant (delete session) | Impossible before TTL (without denylist) |
| Complexity | Low | Medium (key management) |
| Best for | Monoliths, traditional web apps | APIs, microservices, distributed systems |

---

## 4. How JWT Signatures Work

A JWT looks like this: `xxxxx.yyyyy.zzzzz` — three parts separated by dots.

| Part | Content | Example |
|------|---------|---------|
| **Header** | Algorithm and token type | `{"alg": "RS256", "typ": "JWT"}` |
| **Payload** | Claims (user ID, expiration, issuer) | `{"sub": "user_42", "exp": 1718000000, "iss": "auth.example.com"}` |
| **Signature** | Cryptographic proof | Ensures nobody tampered with the payload |

**The signature is what makes JWT secure.** Here is how it works:

1. The server takes the header and payload, hashes them, and encrypts the hash with its **private key**. This creates the signature.
2. The verifier (any service) does the same hash and uses the server's **public key** to check the signature.

If an attacker modifies the payload (e.g., changes `"sub": "user_42"` to `"sub": "admin"`), the signature will not match, and the JWT is rejected. The attacker cannot create a valid signature because they do not have the private key.

**Key rotation:** The server can publish multiple public keys via a **JWKS (JSON Web Key Set)** endpoint. Each key has a unique `kid` (key ID). The JWT header includes the `kid` so verifiers know which public key to use. This allows the server to rotate keys without invalidating active tokens.

---

## 5. OAuth 2.0: Delegating Access

OAuth 2.0 is a protocol that allows a user to grant a third-party application limited access to their resources **without sharing their password**.

**Analogy:** A nightclub stamp. You show your ID at the door (prove who you are). The club stamps your hand. Later, the bartender sees the stamp and knows you are allowed to be there, but the bartender never sees your ID — they just trust the stamp.

**Real-world example:** You click "Sign in with Google" on a website. The website never sees your Google password. Instead, Google gives the website a temporary token that proves you are you (OIDC — see next section) and optionally allows the website to access specific Google APIs on your behalf (OAuth 2.0).

### PKCE — Protection for Mobile Apps

**PKCE** (Proof Key for Code Exchange) is an extra security layer for OAuth. The app generates a secret (code verifier) and sends a hashed version (code challenge) to the authorization server. When exchanging the code for a token, it must provide the original secret. This prevents an attacker who intercepts the authorization code from using it.

---

## 6. OIDC: Proving Who You Are

**OIDC (OpenID Connect)** is an identity layer on top of OAuth 2.0. While OAuth 2.0 is about access ("this app can read my calendar"), OIDC is about identity ("this is who I am").

**Analogy:**
- **OAuth 2.0** = a key card that opens specific doors (access).
- **OIDC** = a passport that proves your identity (authentication).

In practice, OIDC gives you an **ID Token** (a JWT) containing the user's identity, while OAuth 2.0 gives you an **Access Token** (opaque or JWT) used to call APIs.

---

## 7. Service-to-Service Security with mTLS

**mTLS (mutual TLS)** extends the TLS protocol that secures HTTPS. In normal TLS, only the client verifies the server's certificate. In mTLS, **both sides verify each other**.

**How it works:**

1. Every service gets a digital certificate (like a passport) issued by the organization's Certificate Authority.
2. When Service A calls Service B, Service A presents its certificate.
3. Service B verifies that Service A's certificate is signed by the trusted CA.
4. Service B also presents its own certificate, and Service A verifies it.
5. Only if both certificates are valid does the connection proceed.

This means **only authorized services can communicate**. If an attacker deploys a malicious service, it cannot connect to any other service because it does not have a valid certificate.

---

## 8. Common Disasters and How to Avoid Them

### The `alg: none` Attack

An attacker creates a JWT with `"alg": "none"` in the header and removes the signature. Some JWT libraries would accept this as valid (no signature = always passes).

**Mitigation:** Always hardcode the allowed algorithms on the server. Never accept "none".

### Algorithm Confusion

The server uses RS256 (asymmetric: private key signs, public key verifies). The attacker changes the algorithm to HS256 (symmetric: same key signs and verifies) and uses the server's **public key** (which is public!) as the HMAC secret to forge a valid token.

**Mitigation:** Do not use the same verification function for asymmetric and symmetric algorithms. Hardcode the algorithm.

### Token Revocation

A user is banned, but their JWT is valid for another 24 hours. There is no way to revoke it without a denylist, which defeats the stateless purpose.

**Mitigation:** Use short TTLs (15 minutes) with refresh tokens. The refresh token can be revoked because it requires a server call to exchange for a new access token.

### Clock Skew

The JWT says it expired at 14:00:00 UTC, but the verifying server's clock is 30 seconds behind. The server thinks the token is still valid when it is not.

**Mitigation:** Always add a small leeway (30-60 seconds) to the expiration check.

---

## 9. Putting It All Together — A User Logs In

Let's trace a user logging into a mobile app using "Sign in with Google":

1. **User clicks "Sign in with Google"** — the app opens a browser window to Google's authorization server.
2. **OAuth 2.0 + PKCE** — The app generates a code verifier and sends a code challenge. The user authenticates with Google. Google asks: "This app wants to know your identity. Do you consent?"
3. **User consents** — Google redirects to the app with an **authorization code**.
4. **App exchanges the code** — The app sends the authorization code + code verifier to Google. Google verifies the verifier and returns an ID Token (OIDC — who the user is) and an Access Token (OAuth — access to Google APIs).
5. **App calls its own backend** — The app sends the ID Token to the app's API server.
6. **Backend verifies the JWT** — The backend fetches Google's public key from Google's JWKS endpoint, verifies the JWT signature, checks the expiration and issuer, and extracts the user's identity.
7. **Backend issues its own JWT** — The backend creates a short-lived internal JWT (15 minute TTL) for the app's own API calls. This JWT is signed with the backend's private key.
8. **App calls the API** — The app sends the internal JWT. The API verifies the signature and processes the request.

The user's password was never shared with the app. The app's backend never needed to store session state. And every service verifies the JWT locally without calling a central database.

---

## 10. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Access Token** | A token that grants access to specific resources or APIs (OAuth 2.0). |
| **AuthN (Authentication)** | The process of verifying who a user is. |
| **AuthZ (Authorization)** | The process of determining what a user is allowed to do. |
| **Certificate Authority (CA)** | A trusted entity that issues digital certificates. |
| **Clock Skew** | The time difference between the clocks of two systems. |
| **DPoP (Demonstration of Proof-of-Possession)** | A technique to bind a token to a specific client, preventing stolen-token reuse. |
| **ID Token** | A JWT that contains the user's identity (OIDC). |
| **JWT (JSON Web Token)** | A compact, self-contained, cryptographically-signed token for transmitting identity and claims. |
| **JWKS (JSON Web Key Set)** | A set of public keys published by an authorization server for JWT verification. |
| **mTLS (Mutual TLS)** | A security protocol where both client and server verify each other's certificates. |
| **OAuth 2.0** | A protocol for delegated authorization — granting limited access without sharing passwords. |
| **OIDC (OpenID Connect)** | An identity layer on top of OAuth 2.0 for authentication. |
| **PKCE** | Proof Key for Code Exchange — protects OAuth flows on mobile and public clients. |
| **Private Key** | A secret key used to sign JWTs. Only the issuer knows it. |
| **Public Key** | A key published openly that anyone can use to verify a JWT signature. |
| **Refresh Token** | A long-lived token used to obtain new access tokens without re-authentication. |
| **RS256** | An asymmetric signing algorithm (RSA with SHA-256) — private key signs, public key verifies. |
| **Session** | A server-side record of an authenticated user, stored in a database or cache. |
| **Stateless** | The server does not store any client state between requests. |
| **Token Revocation** | Invalidating a token before its natural expiration. Difficult with stateless JWTs. |

---

## 11. Key Takeaways

1. **Know the difference:** AuthN = who you are, AuthZ = what you can do. Always do AuthN first.
2. **Stateful sessions** are simple and instantly revocable, but do not scale without a shared store.
3. **Stateless JWTs** scale horizontally and need no server storage, but cannot be easily revoked.
4. **JWT signatures** (not just encoding!) are what make tampering detectable. Always verify the signature.
5. **Hardcode the allowed algorithms** on the server to prevent `alg: none` and algorithm confusion attacks.
6. **JWKS enables key rotation** without invalidating active tokens.
7. **OAuth 2.0 delegates access** without sharing passwords. PKCE is mandatory for mobile apps.
8. **OIDC provides identity** on top of OAuth 2.0. The ID Token (JWT) proves who the user is.
9. **mTLS ensures only authorized services** can communicate within your infrastructure.
10. **Short TTLs + refresh tokens** balance security (limited window if stolen) with usability.
11. **Always set a clock skew leeway** of 30-60 seconds when validating token expiration.
12. **The best defense is defense in depth:** short TTLs, constrained tokens, mTLS, algorithm whitelisting, and monitoring all work together.

---

> This guide explains the "why" behind authentication and authorization patterns.
> Once you're comfortable with these concepts, the original module (with its JWT validation code, OAuth 2.0 flow diagrams, and mTLS handshake deep dive) will serve as your in-depth reference.
> Remember: in a zero-trust world, identity is the new perimeter. Every request must be verified, regardless of where it comes from.
