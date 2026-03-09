# Configuration

Configuration is read from `src/config/config.yaml` (YAML). Use `config-dev.yaml` when deploying with `--config-env dev`.

## Main options

| Key | Required | Description |
|-----|----------|-------------|
| `source_account_id` | Yes | 12-digit AWS account ID of the Shared Services (source) account. |
| `copy_image_source_region` | No | Default region for copy-image / create-bundle / launch-workspace when `source_region` is omitted from the event (e.g. `us-east-1`). |
| `copy_image_destination_role_name` | No | IAM role name for copy-image in destination accounts (default: `SystemManagementModifierRole`). |
| `ansible_playbooks_s3_bucket` | For apply-ansible-playbook | S3 bucket for playbooks when not using `playbook_s3_url` or `source_type`/`source_info` in the event. |
| `ansible_playbooks_s3_prefix` | No | S3 prefix under the playbooks bucket (default: `playbooks`). |

## Operation defaults

Event payloads are **merged** with defaults from config before each operation runs. You do not need to supply every field in the event file.

- **operation_defaults** — Applied to all operations. Typical keys: `mode` (e.g. `"verify"`), `destination_region`, `source_region`.
- **Operation-specific defaults** — Each operation can have a block named `{operation}_defaults` (e.g. `create_ad_connector_defaults`, `create_radius_shared_secret_defaults`). Merge order: `operation_defaults` → operation-specific block → **event** (event wins).

Example: if `operation_defaults` has `destination_region: "us-east-1"` and `create_ad_connector_defaults` has `directory_size: "small"`, you can omit those from the event; if you include `destination_region: "us-west-2"` in the event, that value is used instead.

### Example config snippet

```yaml
source_account_id: "111111111111"
copy_image_source_region: "us-east-1"

operation_defaults:
  mode: "verify"
  destination_region: "us-east-1"
  source_region: "us-east-1"

create_ad_connector_defaults:
  directory_size: "small"
  directory_dns_name: "upennsre.local"
  # ... other create-ad-connector defaults
```

See `src/config/config.yaml` for the full set of keys and default blocks.
