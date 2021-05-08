from django.urls import path
from django_web_analytics import views
from django_web_analytics.views import api

app_name = 'webanalytics'
urlpatterns = [
    path('analytics.js', api.AnalyticsScriptView.as_view(), name='analytics-script'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/page-view/', api.PageView.as_view(), name='page_view'),
    path('api/event/', api.EventView.as_view(), name='event'),
    path('api/performance/', api.PerformanceEntryView.as_view(), name='performance'),
    path('data-request/', views.DataCollectionView.as_view(), name='data-collection')
]
