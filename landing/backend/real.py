"""Real backend: invoke Lambda and Step Functions per contract invocation blocks."""

from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings

from landing.backend.base import Backend

logger = logging.getLogger(__name__)

# Stack output / config keys for ARNs (must match contract stack_output_arn or logical names).
MANAGEMENT_FUNCTION_ARN_SETTING = "SRE_MANAGEMENT_FUNCTION_ARN"
QUERY_FUNCTION_ARN_SETTING = "SRE_QUERY_FUNCTION_ARN"
STATE_MACHINE_ARN_SETTINGS = {
    "provision-ad-connector": "PROVISION_AD_CONNECTOR_STATE_MACHINE_ARN",
    "provision-linux-workspace": "PROVISION_WORKSPACE_STATE_MACHINE_ARN",
    "provision-windows-workspace": "PROVISION_WINDOWS_WORKSPACE_STATE_MACHINE_ARN",
    "provision-ec2-instance": "PROVISION_EC2_INSTANCE_STATE_MACHINE_ARN",
}


def _get_boto_client(service: str):  # noqa: ANN201
    import boto3
    return boto3.client(service)


def _invoke_lambda(function_arn: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    if not function_arn:
        return {
            "status": "error",
            "error": "ConfigurationError",
            "message": (
                "Real backend is enabled but SRE Lambda ARN is not configured. "
                "Set the appropriate ARN in settings."
            ),
        }
    logger.info(
        "real backend: invoking Lambda payload_keys=%s query=%s",
        list(payload.keys()),
        payload.get("query"),
    )
    try:
        client = _get_boto_client("lambda")
        response = client.invoke(
            FunctionName=function_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        raw = response["Payload"].read()
        result = json.loads(raw) if isinstance(raw, bytes) else json.load(raw)
        result_status = result.get("status")
        result_list = result.get("result")
        result_count = len(result_list) if isinstance(result_list, list) else None
        logger.info(
            "real backend: Lambda response status=%s result_count=%s keys=%s",
            result_status,
            result_count,
            list(result.keys()) if isinstance(result, dict) else None,
        )
        if result.get("status") != "success":
            logger.warning(
                "real backend: Lambda error=%s message=%s",
                result.get("error"),
                result.get("message"),
            )
        # Normalize: backend may return status/result or status/error/message
        if result.get("status") == "error" or "error" in result:
            return {
                "status": "error",
                "error": result.get("error", "UnknownError"),
                "message": result.get("message", str(result)),
            }
        return result
    except Exception as e:  # noqa: BLE001
        logger.exception("real backend: Lambda invoke failed")
        return {"status": "error", "error": type(e).__name__, "message": str(e)}


def _start_state_machine(state_machine_arn: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    if not state_machine_arn:
        return {
            "status": "error",
            "error": "ConfigurationError",
            "message": (
                "Real backend is enabled but state machine ARN is not configured. "
                "Set the appropriate ARN in settings."
            ),
        }
    try:
        client = _get_boto_client("stepfunctions")
        response = client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(payload),
        )
        execution_arn = response["executionArn"]
        # executionArn is like arn:aws:states:region:account:execution:name:execution_id
        execution_id = execution_arn.split(":")[-1]
        from django.utils import timezone as django_tz
        now = django_tz.now()
        return {
            "execution_id": execution_id,
            "execution_arn": execution_arn,
            "name": execution_arn.split(":")[-2] if ":" in execution_arn else "",
            "label": "",  # Caller can fill from contract
            "status": "Running",
            "started_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "started_at_relative": "Just now",
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": type(e).__name__, "message": str(e)}


class RealBackend(Backend):
    """Backend that invokes real Lambda and Step Functions using contract payloads and ARNs from settings."""

    def invoke_operation(self, payload: dict[str, Any]) -> dict[str, Any]:
        arn = getattr(settings, MANAGEMENT_FUNCTION_ARN_SETTING, None)
        return _invoke_lambda(arn, payload)

    def start_pipeline(self, pipeline_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        setting_name = STATE_MACHINE_ARN_SETTINGS.get(pipeline_id)
        arn = getattr(settings, setting_name, None) if setting_name else None
        result = _start_state_machine(arn, payload)
        if result.get("status") != "error" and not result.get("label"):
            from landing.pipeline_contracts import get_pipeline_contract
            contract = get_pipeline_contract(pipeline_id)
            if contract:
                result["label"] = contract.label
        return result

    def run_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        arn = getattr(settings, QUERY_FUNCTION_ARN_SETTING, None)
        payload = dict(payload)
        stack_name = getattr(settings, "SRE_STACK_NAME", None)
        if stack_name:
            payload["stack-name"] = stack_name
            logger.debug("real backend: added stack-name=%s to query payload", stack_name)
        return _invoke_lambda(arn, payload)
