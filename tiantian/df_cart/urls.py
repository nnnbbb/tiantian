from django.conf.urls import include, url
import views


urlpatterns = [
    url(r'^$', views.cart),
    url(r'^add(\d+)_(\d+)', views.add),

]