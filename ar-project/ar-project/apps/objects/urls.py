
from django.urls import path

from .text_objects.template_views import *
from .text_objects.object_views import *

from .utils import fetch_text_object_template, like_object, unlike_object, hide_object, unhide_object


urlpatterns = [


    path('objects/templates/create/', create_ar_text_template, name='create_ar_text_template'),
    path('objects/templates/view/<int:pk>/', view_ar_text_template_details, name='view_ar_text_template_details'),
    path('objects/templates/edit/<int:pk>/', edit_ar_text_template, name='edit_ar_text_template'),
    path('objects/templates/delete/<int:pk>/', delete_ar_text_template, name='delete_ar_text_template'),

    path('objects/templates/', ar_text_template_list, name='ar_text_template_list'),


    path('objects/create/', create_ar_text_object, name='create_ar_text_object'),
    path('objects/create/<slug:channel_slug>/', create_ar_text_object_channel_specific, name='create_ar_text_object_channel_specific'),
    path('objects/view/<int:pk>/', view_ar_text_object_details, name='view_ar_text_object_details'),
    path('objects/edit/<int:pk>/', edit_ar_text_object, name='edit_ar_text_object'),
    path('objects/delete/<int:pk>/', delete_ar_text_object, name='delete_ar_text_object'),
    path('objects/suspend/<int:pk>/', suspend_ar_text_object, name='suspend_ar_text_object'),

    path('objects/like/<int:pk>/', like_ar_text_object, name='like_ar_text_object'),
    path('objects/unlike/<int:pk>/', unlike_ar_text_object, name='unlike_ar_text_object'),
    path('objects/hide/<int:pk>/', hide_ar_text_object, name='hide_ar_text_object'),
    path('objects/unhide/<int:pk>/', unhide_ar_text_object, name='unhide_ar_text_object'),

    path('objects/', ar_text_object_list_user, name='ar_text_object_list_user'),
    path('objects/admin', ar_text_object_list_admin, name='ar_text_object_list_admin'),

    path('api/templates/fetch/<int:template>/', fetch_text_object_template, name='fetch_text_object_template'),
    path('api/like/<int:pk>/<str:object_type>/', like_object, name='like_object'),
    path('api/unlike/<int:pk>/<str:object_type>/', unlike_object, name='unlike_object'),
    path('api/hide/<int:pk>/<str:object_type>/', hide_object, name='hide_object'),
    path('api/unhide/<int:pk>/<str:object_type>/', unhide_object, name='unhide_object'),

]
