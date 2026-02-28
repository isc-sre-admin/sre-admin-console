from datetime import date, timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Render the primary workflow-oriented landing page."""
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    context = {
        "active_executions": [
            {
                "name": "provision-ad-connector",
                "enclave": "sre-dev-enclave-01",
                "started_at": "6 minutes ago",
                "status": "Running",
            },
            {
                "name": "provision-linux-workspace",
                "enclave": "sre-research-enclave-02",
                "started_at": "18 minutes ago",
                "status": "Waiting for workspace registration",
            },
        ],
        "recent_executions": [
            {
                "name": "provision-windows-workspace",
                "enclave": "sre-research-enclave-01",
                "completed_at": "Today, 09:42 UTC",
                "status": "Succeeded",
            },
            {
                "name": "provision-ec2-instance",
                "enclave": "sre-research-enclave-03",
                "completed_at": "Today, 08:17 UTC",
                "status": "Failed",
            },
            {
                "name": "provision-ad-connector",
                "enclave": "sre-dev-enclave-01",
                "completed_at": "Yesterday, 20:06 UTC",
                "status": "Succeeded",
            },
        ],
        "relative_ranges": [7, 30, 60],
        "default_range_days": 7,
        "default_start_date": start_date.isoformat(),
        "default_end_date": end_date.isoformat(),
    }
    return render(request, "landing/home.html", context)
