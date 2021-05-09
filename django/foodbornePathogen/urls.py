from django.urls import path

from . import views

urlpatterns = [path('', views.index, name='index'),
               path('terms/', views.terms, name='terms'),
               path('options/<str:range_choice>', views.options, name='options'),
               path('submitted/<uuid:job_id>', views.submitted, name='submitted'),
               path('info/', views.info, name='info'),
               path('results/<uuid:job_id>', views.results, name='results'),
               path('static/<path:filepath>', views.download_static)]
