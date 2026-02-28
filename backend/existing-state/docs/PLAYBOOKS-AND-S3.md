# Playbooks and S3

## Syncing playbooks to S3

When using the **config** bucket (`ansible_playbooks_s3_bucket` and optional prefix), the Lambda builds a zip of its **bundled** playbooks (from the image) and sends it to the instance via a presigned URL on every run. For a custom `playbook_s3_url`, upload playbooks yourself.

Upload from repo to the config bucket:

```bash
make sync-playbooks
```

Or:

```bash
python scripts/sync_ansible_playbooks.py
```

This uploads all files under `src/assets/playbooks/` to the S3 bucket in `src/config/config.yaml` (or `config-dev.yaml` if `CONFIG_ENV=dev`). A file is uploaded if it is missing in S3 or its content differs.

## Cross-account playbook delivery

When the EC2 instance (and SSM Run Command) is in a **different account** from the playbooks bucket, a direct S3 object URL in `SourceInfo` can cause **403**: the instance uses its own IAM role in the destination account, which may not have access to the source-account bucket.

**What the code does:** When using the config bucket and `destination_account_id` (or `node_account_id`) differs from the Lambda’s account (`source_account_id`), the operation builds a **zip** of the bundled playbooks, uploads it to the config bucket under `playbook-runs/`, and passes a **presigned URL** (1-hour expiry) to SSM. The instance downloads via HTTPS and does not need S3 permissions on the playbooks bucket.

**IAM alternative:** To have the instance read directly from the bucket: (1) Apply the bucket policy in `cloudformation/ansible-playbooks-bucket-policy.json` (allows org principals `s3:GetObject`, `s3:ListBucket`). (2) Give the instance profile in the destination account `s3:GetObject` and `s3:ListBucket` on the playbooks bucket. The code still uses the presigned URL when target ≠ source so cross-account runs work without that instance policy.
