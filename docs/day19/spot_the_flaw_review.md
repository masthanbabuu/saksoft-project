# Security Code Review

## 1. SQL Injection
Problem: User input is directly inserted into SQL.
Risk: Unauthorized database access.
Fix: Use parameterized SQL queries.

## 2. Broken Access Control
Problem: Invoice ownership is not validated.
Risk: Users can access other users' invoices.
Fix: Validate invoice ownership and user permissions.

## 3. Weak Password and Token Security
Problem: MD5 hashing, hardcoded secret and missing token expiry.
Risk: Password cracking and unauthorized access.
Fix: Use Argon2id, environment-based secrets and token expiry.

## 4. Unsafe Deserialization
Problem: Untrusted pickle data and unverified dependency.
Risk: Remote code execution and supply-chain attacks.
Fix: Use validated JSON and verify dependencies.

## 5. Sensitive Information Exposure
Problem: Passwords and stack traces are exposed.
Risk: Credential leakage and information disclosure.
Fix: Redact sensitive logs, return generic errors and correct HTTP status.

## 6. SSRF and Path Traversal
Problem: Unrestricted URLs and file paths.
Risk: Internal service access and unauthorized file downloads.
Fix: Validate destinations, restrict file access, enforce
authorization and configure request timeouts.
