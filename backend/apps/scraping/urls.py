from django.urls import path

from . import views

urlpatterns = [
    path("automate-log/", views.automate_log, name="automate-log"),
    path("logs/", views.get_automate_logs, name="get-automate-logs"),
    path("runs/", views.get_scrape_runs, name="get-scrape-runs"),
    path("gaps/", views.get_gap_analysis, name="get-gap-analysis"),
]
