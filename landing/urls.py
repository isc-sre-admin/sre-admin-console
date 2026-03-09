from django.urls import path

from landing.views import (
    execute_operation,
    home,
    pipeline_execution_detail,
    pipeline_executions_json,
    start_pipeline_execution,
)

app_name = "landing"

urlpatterns = [
    path("", home, name="home"),
    path("api/pipeline-executions/", pipeline_executions_json, name="pipeline-executions-json"),
    path("pipelines/<str:pipeline_id>/start/", start_pipeline_execution, name="start-pipeline-execution"),
    path("pipelines/executions/<str:execution_id>/", pipeline_execution_detail, name="pipeline-execution-detail"),
    path("operations/<str:operation_id>/execute/", execute_operation, name="execute-operation"),
]
