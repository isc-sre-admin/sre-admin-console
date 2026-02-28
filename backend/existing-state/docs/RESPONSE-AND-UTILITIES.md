# Response Format and Utilities

## Response format

- **Success:** `{ "status": "success", "operation": "<operation>", ... }` with operation-specific fields (e.g. `new_image_id`, `bundle_id`, `workspace_id`).
- **Error:** `{ "status": "error", "error": "<code>", "message": "<description>" }` (e.g. `InvalidRequest`, `ConfigError`, `AwsError`).

## Sanitizing output

The script `scripts/sanitize.py` masks identifiers in text for safe sharing or logging:

- **Email addresses** — Replaced with a stable mask in `@example.com` (e.g. `user1@example.com`).
- **AWS account IDs** — 12-digit sequences replaced with 12 zeros.
- **Resource IDs** — AWS-style IDs (e.g. `ws-03msgd999`, `wsi-abc123`) replaced with same-format generated IDs.

Usage:

```bash
python scripts/sanitize.py --file input.txt
python scripts/sanitize.py "Contact admin@corp.com in 123456789012"
echo "..." | python scripts/sanitize.py
```
