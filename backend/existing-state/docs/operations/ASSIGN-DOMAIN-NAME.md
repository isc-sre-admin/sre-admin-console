# Assign Domain Name

## Summary

Ensures a Route 53 A record in the source account's private hosted zone (from config `assign_domain_name_defaults.hosted_zone_name`) points to the IPv4 address of an EC2 instance in a destination account. Instance can be specified by `instance_id` or `instance_name` (Name tag).

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `assign-domain-name` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Account where instance lives |
| subdomain | Yes | Subdomain (e.g. `myserver` → myserver.hosted_zone_name) |
| instance_id or instance_name | Yes | Instance identifier |
| destination_region / source_region | No | Region for instance lookup |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| error, message | On error |

## Related

- **Contract:** [assign-domain-name.yaml](../../contracts/operations/assign-domain-name.yaml)
