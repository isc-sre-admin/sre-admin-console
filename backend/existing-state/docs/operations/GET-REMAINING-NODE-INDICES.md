# Get Remaining Node Indices

## Summary

Returns the indices of nodes in node_ids that have not yet been processed. Used by the provision-ad-connector pipeline when applying duoauthproxy.yaml to multiple Duo Auth Proxy nodes: after applying to the first node, the pipeline uses this to apply to the remaining nodes (when config_changed was true).

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `get-remaining-node-indices` |
| node_ids | Yes | Array of node IDs (e.g. from list-duo-auth-proxy-nodes) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| remaining_indices | Array of indices (0-based) to process |
| error, message | On error |

## Related

- **Contract:** [get-remaining-node-indices.yaml](../../contracts/operations/get-remaining-node-indices.yaml)
