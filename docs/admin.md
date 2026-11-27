# Administrator Guide

Audience: System administrators.

## Administration
- Configure database and LLM settings.
- Manage authorized reader and administrator roles.
- Rotate credentials securely.
- Restrict access to internal services.

## Backup and restore
Use PostgreSQL pg_dump for database backups.
Use pg_restore for custom-format backups.
Store backups securely and test restoration separately.

Backup restoration has not yet been verified.

## Monitoring
    docker compose -p day18 ps
    docker compose -p day18 logs --tail=100 app
    curl -f http://127.0.0.1:8081/health/ready

Investigate unhealthy containers and repeated errors.
Automated alerting is not yet verified.
