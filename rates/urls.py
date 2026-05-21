from django.urls import path
from . import views

urlpatterns = [
    path('', views.success_page, name='home'),
    path('rates/', views.show_rates, name='rates'),
    path('import/', views.import_excel, name='import_excel'),
    path('scraper/', views.scraper_page, name='scraper'),
    path('run-scraper/', views.run_scraper, name='run_scraper'),
    path('get-ports/', views.get_ports, name='get_ports'),
    path('download-excel/', views.download_excel, name='download_excel'),
    path('run-tracker/', views.tracker_page, name='tracker_page'),
    path('run-tracker/run/', views.run_tracker, name='run_tracker'),

    # ✅ IMPORTANT
    path('get-shipping-lines/', views.get_shipping_lines, name='get_shipping_lines'),

]