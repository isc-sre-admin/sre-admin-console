from django.urls import path

from landing.views import home, pipeline_execution_detail, start_pipeline_execution

app_name = "landing"

urlpatterns = [
    path("", home, name="home"),
    path("pipelines/<str:pipeline_id>/start/", start_pipeline_execution, name="start-pipeline-execution"),
    path("pipelines/executions/<str:execution_id>/", pipeline_execution_detail, name="pipeline-execution-detail"),
]
