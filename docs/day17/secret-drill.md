# Leaked Secret Drill

- Created an isolated temporary Git repository.
- Created a secret-drill branch.
- Committed a simulated credential.
- Removed the credential in a subsequent commit.
- Verified that the credential remained in Git history.
- No real credentials were used.
- No drill commits were pushed remotely.

Lesson: Deleting a secret from a file does not remove
it from Git history. Exposed real credentials must
be revoked and rotated.

Result: PASSED
