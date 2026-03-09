from django.urls import path

from endpoints.views import (
    enclave_detail,
    endpoint_detail,
    enclave_vulnerabilities,
    endpoints_index,
    execute_endpoint_operation,
    patch_detail,
)

app_name = "endpoints"

urlpatterns = [
    path("", endpoints_index, name="index"),
    path("<str:enclave_id>/", enclave_detail, name="enclave-detail"),
    path(
        "<str:enclave_id>/vulnerabilities/",
        enclave_vulnerabilities,
        name="enclave-vulnerabilities",
    ),
    path("<str:enclave_id>/<str:resource_type>/<str:resource_id>/", endpoint_detail, name="endpoint-detail"),
    path(
        "<str:enclave_id>/<str:resource_type>/<str:resource_id>/patching/",
        patch_detail,
        name="patch-detail",
    ),
    path(
        "<str:enclave_id>/<str:resource_type>/<str:resource_id>/operations/<str:operation_id>/execute/",
        execute_endpoint_operation,
        name="execute-operation",
    ),
]
