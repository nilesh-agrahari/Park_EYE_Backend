from django.contrib import admin
from .models import Suspected,VehicleRecord,Police,Location,Parking
# Register your models here.

admin.site.register(Suspected)
admin.site.register(VehicleRecord)
admin.site.register(Police)
admin.site.register(Location)
admin.site.register(Parking)