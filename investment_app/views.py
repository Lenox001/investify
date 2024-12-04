from django.shortcuts import render
from core.models import RecentActivity  # Import the model from the core app

def custom_admin_dashboard(request):
    # Get the 5 most recent activities
    recent_activities = RecentActivity.objects.all()[:5]
    return render(request, 'admin/index.html', {'recent_activities': recent_activities})
