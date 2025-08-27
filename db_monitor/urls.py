from django.urls import path


from . import views

urlpatterns = [
    path("",views.show_status, name="status"),
    path("reporte/<str:server>/",views.show_report,name="report"),
    path("check_status",views.check_status,name="check_status"),
    path("mensajeria/",views.mensajeria,name="mensajes")
    
]
