# WebAuthn / Passkey MFA Setup

Passkey (WebAuthn) authentication allows users to log in using platform biometrics
(Face ID, Touch ID, Windows Hello) or hardware security keys (YubiKey) instead of
or in addition to passwords.

## Configuration

Passkey login is enabled via `django-allauth`'s `allauth.mfa` module. The following
settings are configured in `projects/cms-fusion/configs/base/auth.py` and
`projects/precis/precis-main/configs/base/auth.py` (shared across all sites):

```python
# allauth.mfa must be in INSTALLED_APPS (set in configs/base/apps.py)
INSTALLED_APPS += ["allauth.mfa"]

# Enable passkey-based login
MFA_PASSKEY_LOGIN_ENABLED = True

# Passkey-only signup (requires email verification + code): defaults to False
MFA_PASSKEY_SIGNUP_ENABLED = False

# Supported MFA types: TOTP (authenticator app), WebAuthn (passkeys), recovery codes
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
```

## What was changed

| File | Change |
|------|--------|
| `projects/cms-fusion/configs/base/apps.py` | Added `"allauth.mfa"` to `THIRD_PARTY_APPS` |
| `projects/precis/precis-main/configs/base/apps.py` | Added `"allauth.mfa"` to `THIRD_PARTY_APPS` |
| `projects/cms-fusion/configs/base/auth.py` | `MFA_PASSKEY_LOGIN_ENABLED` → `True`; added `"webauthn"` to `MFA_SUPPORTED_TYPES` |
| `projects/precis/precis-main/configs/base/auth.py` | Same as above |
| `tests/unit/test_auth_features.py` | Added `test_passkey_mfa_enabled` test |

## Browser requirements

Passkeys require the page to be served over HTTPS (or `localhost` for development).
Browsers that support WebAuthn:

- Chrome 108+ (Windows, macOS, Android)
- Safari 16+ (macOS, iOS)
- Firefox 118+
- Edge 108+

## Enabling passkey signup

To allow users to sign up using only a passkey (no password), set:

```python
MFA_PASSKEY_SIGNUP_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
```

## Troubleshooting

- **"Passkey is not supported"**: The page must be served over HTTPS.
- **"The operation either timed out or was not allowed"**: User cancelled the browser's
  passkey prompt — try again.
- **Passkey doesn't persist across devices**: Passkeys are scoped to the device's
  platform authenticator. Users must set up a passkey on each device they use.
