from django.conf.urls import url
from . import views

app_name = 'project_a'
urlpatterns = [
    url(r'^$', views.login_page, name="login"),
]
