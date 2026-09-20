from django.urls import path
from .views import *

urlpatterns = [

    path('moderation/report_object/<int:object_id>/', report_object, name='report_object'),
    path('moderation/view_reports/', view_reports, name='view_reports'),
    path('moderation/review_report/<int:report_id>/', review_report, name='review_report'),
    path('moderation/action_report/<int:report_id>/', action_report, name='action_report'),
    path('moderation/ban_user/<int:user_id>/', ban_user_view, name='ban_user'),
    path('moderation/unban_user/<int:user_id>/', unban_user_view, name='unban_user'),

]
