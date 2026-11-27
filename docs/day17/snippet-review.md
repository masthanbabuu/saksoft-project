# Day 17 - AI Code Security Review

| No | Vulnerability | Severity | Recommended Fix |
|---|---|---|---|
| 1 | SQL injection using f-string queries | High | Use parameterized SQL queries |
| 2 | Hardcoded API credentials | High | Use environment variables and rotate exposed keys |
| 3 | Unsafe user-controlled filenames | High | Generate random filenames and validate file content |
| 4 | Passwords stored in plaintext | High | Use Argon2id password hashing |
| 5 | Untrusted input passed to eval() | Critical | Remove eval and use safe parsing |
| 6 | HTTP requests without timeout | Medium | Configure explicit connection and read timeouts |

## Lessons learned

AI-generated code must be reviewed before acceptance.
Validate inputs, protect credentials, enforce authentication,
and run security scanners and automated tests.

These are substitute review examples because the original
training snippets were unavailable.
