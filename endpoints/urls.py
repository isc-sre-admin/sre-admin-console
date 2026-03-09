from django.urls import path

from endpoints.views import enclave_detail, endpoint_detail, endpoints_index, execute_endpoint_operation

app_name = "endpoints"

urlpatterns = [
    path("", endpoints_index, name="index"),
    path("<str:enclave_id>/", enclave_detail, name="enclave-detail"),
    path("<str:enclave_id>/<str:resource_type>/<str:resource_id>/", endpoint_detail, name="endpoint-detail"),
    path(
        "<str:enclave_id>/<str:resource_type>/<str:resource_id>/operations/<str:operation_id>/execute/",
        execute_endpoint_operation,
        name="execute-operation",
    ),
]
