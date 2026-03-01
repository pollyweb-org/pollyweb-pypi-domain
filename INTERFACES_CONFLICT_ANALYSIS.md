# Interfaces Conflict Analysis

## Overview

`pollyweb-pypi-domain/src/PW_DOMAIN` contains a subset of interfaces that overlap with `pollyweb/python/interfaces`. The package version was refactored for standalone use (PyPI, lambdas) while the monorepo version has tight coupling to NLWEB, WEB, ACTOR, and PW_AWS.

---

## File Mapping

| pollyweb/python/interfaces | pollyweb-pypi-domain/src/PW_DOMAIN | Notes |
|---------------------------|------------------------------------|-------|
| Manifest/MANIFEST.py | MANIFEST.py | Nearly identical; PW uses `.` imports |
| Manifest/MANIFEST_TRUST.py | MANIFEST_TRUST.py | Nearly identical |
| Code/CODE.py | CODE.py | Nearly identical |
| Code/CODE_CODES.py | CODE_CODES.py | Nearly identical |
| MSG/MSG.py | MSG.py | **Different** – see below |
| Domain/DOMAIN_CONFIG.py | DOMAIN_CONFIG.py | Nearly identical |
| Domain/DOMAIN_PARSER.py | DOMAIN_PARSER.py | Nearly identical |
| — | MSG_RECEIVER.py | **New in package** – inbox handler |
| — | ITEM.py | **New in package** – DynamoDB item abstraction |

### Not in PW_DOMAIN (pollyweb-only)

- Domain/DOMAIN.py, DOMAIN_DEPLOY.py, DOMAIN_VERIFIER.py (depends on PW_AWS, ACTOR, NLWEB)
- QrCode/QR.py
- UPDATE.py, TOKEN.py, CONFIG.py, QUERY.py, ORDER2.py, CHARGE.py, SESSION.py

---

## Key Conflicts

### 1. MSG.VerifySignature()

**pollyweb** (interfaces/MSG/MSG.py):
```python
def VerifySignature(self, publicKey: str=None):
    if publicKey == None:
        domain = NLWEB.DOMAIN(name=self.RequireFrom())
        publicKey = domain.GetPublicKey()
    dkim = NLWEB.BEHAVIORS().SYNCAPI().DKIM()
    validator = dkim.ValidateSignature(...)
```
- Fetches public key from domain if not provided
- Uses NLWEB for DKIM validation

**PW_DOMAIN** (MSG.py):
```python
def VerifySignature(self, publicKey: str = None, validator: object = None):
    if publicKey is None:
        raise ValueError('publicKey is required to verify the signature.')
    if validator is None:
        raise ValueError('validator is required to verify the signature.')
    # Uses injected validator (callable or object with ValidateSignature)
```
- Requires both `publicKey` and `validator` – no NLWEB dependency
- Suitable for lambdas and standalone contexts

### 2. MSG.MatchSubject()

**pollyweb**: Uses `NLWEB.CONFIG().RequireDomain()` for `expectedTo` when `ignoreTo` is False.

**PW_DOMAIN**: Requires explicit `expectedTo` parameter when `ignoreTo` is False.

### 3. MSG.Send()

**pollyweb**: Uses `WEB().HttpPost()` (internal WEB module).

**PW_DOMAIN**: Uses `urllib.request` directly – no WEB dependency.

### 4. Import style

- **pollyweb**: Flat imports (`from CODE import CODE`, `from MANIFEST import MANIFEST`) – assumes `interfaces` on PYTHONPATH.
- **PW_DOMAIN**: Package-relative imports (`from .CODE import CODE`, `from .MANIFEST import MANIFEST`).

---

## Resolution Strategies

### Option A: pollyweb-domain as canonical source (recommended)

1. Treat `pollyweb-pypi-domain` as the single source of truth for shared interfaces.
2. Add `pollyweb-domain` as a dependency of the pollyweb monorepo.
3. Replace `pollyweb/python/interfaces` with a thin compatibility layer that:
   - Re-exports from `PW_DOMAIN` for CODE, MANIFEST, MANIFEST_TRUST, DOMAIN_CONFIG, DOMAIN_PARSER
   - For MSG: either use PW_DOMAIN.MSG directly and adapt callers, or add a `MSG_NLWEB` subclass that overrides `VerifySignature` and `MatchSubject` to use NLWEB when available
4. Keep pollyweb-specific interfaces (DOMAIN, DOMAIN_DEPLOY, etc.) in pollyweb; they can import from `PW_DOMAIN` for shared types.

### Option B: Sync both directions

1. Keep both locations.
2. Establish a sync script: pollyweb → PW_DOMAIN for shared files.
3. Apply package-specific adaptations (imports, dependency injection) in PW_DOMAIN.
4. Risk: divergence over time; manual sync burden.

### Option C: Adapter in pollyweb-domain

1. Add optional `pollyweb-domain[pollyweb]` extra with NLWEB dependency.
2. Provide `MSG.with_pollyweb()` or `MSG_NLWEB` that wraps PW_DOMAIN.MSG and adds NLWEB-based `VerifySignature`/`MatchSubject`.
3. pollyweb uses the pollyweb extra; lambdas use base package.

### Option D: Compatibility shim in pollyweb

1. Keep PW_DOMAIN as-is (minimal deps).
2. In pollyweb, create `interfaces/msg_compat.py` that wraps `PW_DOMAIN.MSG` and adds NLWEB behavior.
3. pollyweb code imports from the compat layer.

---

## Recommended Path: Option A + C

1. **Make pollyweb-domain canonical** for CODE, MANIFEST, MANIFEST_TRUST, DOMAIN_CONFIG, DOMAIN_PARSER, MSG, MSG_RECEIVER, ITEM.
2. **Add optional NLWEB integration** in pollyweb-domain:
   - `PW_DOMAIN.MSG` stays dependency-free.
   - Add `PW_DOMAIN.MSG_NLWEB` (or `MSG.with_pollyweb_validator()`) in an optional submodule that requires `pollyweb` (or similar) as an extra.
   - pollyweb uses `MSG_NLWEB` where it needs automatic domain/DKIM resolution.
3. **Migrate pollyweb** to depend on `pollyweb-domain` and remove duplicated interface code.
4. **Update pollyweb-aws lambdas** to use `pollyweb-domain` directly (they already fit the validator-injection model).

---

## Migration Completed (Option A + C)

1. **pollyweb-domain** is the canonical source for CODE, CODE_CODES, MANIFEST, MANIFEST_TRUST, DOMAIN_CONFIG, DOMAIN_PARSER, MSG, MSG_RECEIVER, ITEM.
2. **pollyweb** depends on `pollyweb-domain` (added to requirements.txt).
3. **pollyweb/python/interfaces** now re-exports from PW_DOMAIN (Code, Manifest, Domain subdirs) and MSG/MSG.py provides MSG_NLWEB.
4. pollyweb-specific interfaces (DOMAIN, DOMAIN_DEPLOY, etc.) remain in pollyweb.

## Original Next Steps (superseded)

1. Decide which option to pursue.
2. If Option A: add `pollyweb-domain` to pollyweb’s dependencies and create the compatibility layer.
3. If Option C: add the optional pollyweb integration to pollyweb-domain.
4. Update all consumers (pollyweb, pollyweb-aws, etc.) to import from `PW_DOMAIN` where applicable.
5. Deprecate or remove duplicated files in `pollyweb/python/interfaces`.
