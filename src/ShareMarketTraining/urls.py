"""ShareMarketTraining URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('live/nse/', views.nse),
    path('live/bse/', views.bse),
    path('live/', views.fullStatus),
    path('reload/', views.reload),
    path("topChangers/",views.getTopChangers),
    path('users/', views.getUsers),
    path('trades/<str:uid>', views.getTrades),
#     path('user/<str:userName>', views.getUserByName),
    path('stockStatus/<str:stockName>/', views.stockStatus),
    path('search/<str:queryString>/', views.searchByName),
]
