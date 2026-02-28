# Create Security Group

## Summary

Creates an EC2 security group in a destination account with configurable ingress and egress rules (CIDR or source security group). Idempotent: if group with same name exists in VPC, returns success. Optional vpc_id or vpc_name; when both omitted, single/default VPC is used.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-security-group` |
| mode | Yes | `verify` or `modify` |
| security_group_name | Yes | Name |
| ingress_rules | Yes | List of protocol, port_range, source_ip or source_security_group_name |
| egress_rules | Yes | List of protocol, port_range, destination_ip (empty keeps default egress) |
| destination_account_id | Yes | Target account |
| vpc_id / vpc_name | No | VPC; default when omitted |
| description | No | SG description |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| security_group_id | Created or existing |
| already_exists | When group already existed |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-security-group.yaml](../../contracts/operations/create-security-group.yaml)
