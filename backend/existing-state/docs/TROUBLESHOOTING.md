# Troubleshooting

## Viewing command output when a run fails

When `apply-ansible-playbook` fails, the response may include `standard_output_content` and `standard_error_content` (possibly truncated). For full output:

1. **CloudWatch Logs (default):** Output is streamed to CloudWatch in the destination account. Default log group: `/aws/ssm/AWS-ApplyAnsiblePlaybooks`. Use `output_cloudwatch_log_group_name` in the event for a custom group. The instance profile needs `logs:CreateLogStream` and `logs:PutLogEvents` on that group.
2. **S3 output:** Include `output_s3_bucket_name` (and optionally `output_s3_key_prefix`) in the event. Instance role must have `s3:PutObject` on that bucket. Response will include `standard_output_url` and `standard_error_url`.
3. **AWS CLI:** With destination-account credentials: `aws ssm get-command-invocation --command-id <id> --instance-id <id> --region <region>`.

## Troubleshooting apply-ansible-playbook

**Sudo/password errors:**

1. **Passwordless sudo:** The SSM user (e.g. `ssm-user`) needs passwordless sudo for tasks with `become: true`. Add e.g. `ssm-user ALL=(ALL) NOPASSWD: ALL` to `/etc/sudoers.d/ssm-user`.
2. **Root password expired:** Run playbooks as `ssm-user` with `become: true` only where needed; avoid running as root.
3. **Skip dependency installation:** Set `install_dependencies: false` in the event. The SSM document will skip installing Ansible; ensure Ansible (and required tools) are already on the instance (e.g. in the AMI). For provision-ec2-instance with `install_dependencies: false`, the launch step can create symlinks so the document finds `ansible`/`ansible-playbook`.

**Playbook not found:** Ensure playbooks are synced to S3 (`make sync-playbooks`) and the instance role has `s3:GetObject` on the playbooks bucket (or use the presigned-URL path when target account ≠ source).

## Troubleshooting list-duo-auth-proxy-nodes (empty node_ids)

When the provision-ad-connector pipeline gets `node_ids` as `[]`, the response includes:

- **tagged_count:** EC2 instances in the account/region with tag `Function` = `duo-auth-proxy`.
- **ssm_online_count:** Instances in that region that are SSM-managed and PingStatus Online.

Use these to narrow the cause:

1. **tagged_count is 0:** No instances have the tag. Check tag key `Function` and value `duo-auth-proxy` (lowercase, hyphen). Confirm instances are in the **source account** (config `source_account_id`) and the correct region; add `destination_region` to the event if needed.
2. **tagged_count > 0, ssm_online_count is 0:** Instances have the tag but are not SSM online. Ensure SSM agent is running, instance profile has SSM permissions (e.g. `AmazonSSMManagedInstanceCore`), and instances can reach SSM (VPC endpoint or internet).
3. **Both > 0 but node_ids empty:** Tagged instances are not in the SSM-online set. Confirm same account and region for both.
