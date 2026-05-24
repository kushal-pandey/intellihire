from django.contrib import admin
from django.urls import path

admin.site.site_header = "IntelliHire Administration"
admin.site.site_title = "IntelliHire Admin"
admin.site.index_title = "Platform Management Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
]