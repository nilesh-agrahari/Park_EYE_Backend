from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class Suspected(models.Model):
    regs_no = models.CharField(max_length=20)
    date_time = models.DateTimeField(default=now)
    crime_attempted = models.CharField(max_length=255,null=True)
    spotted_location = models.CharField(max_length=255,null=True)
    found_location = models.CharField(max_length=255, blank=True, null=True)
    is_founded = models.BooleanField(default=False)               # Description of charges (can be long)

    def __str__(self):
        return f"{self.regs_no} ------------- {self.date_time} ---------------{self.crime_attempted} ------------- {self.is_founded}"

class Parking(models.Model):
    username = models.CharField(max_length=100, unique=True)   # Parking name (login username)
    password = models.CharField(max_length=255)                # Hashed password
    # location = models.CharField(max_length=255, blank=True, null=True)  # Optional: parking location/address

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        """Automatically hash password if it's not already hashed"""
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class VehicleRecord(models.Model):
    
    parking=models.ForeignKey(Parking, on_delete=models.CASCADE, related_name="vehicles", null=True, blank=True)  # Associated parking (if any)
    regs_no = models.CharField(max_length=20)                     # Vehicle registration number
    in_date_time = models.DateTimeField(null=True, blank=True)         # Entry date & time (captured automatically when created)
    out_date_time = models.DateTimeField(null=True, blank=True)    # Exit date & time (can be empty initially)
    in_parking = models.BooleanField(default=True)                 # Checkbox to indicate if vehicle is currently inside
    slot_position = models.CharField(max_length=5, blank=True, null=True)  # Slot position (e.g., "A1", "B1", etc.)
    suspected = models.BooleanField(default=False)                  # Is the vehicle suspected?

    def __str__(self):
        return f"{self.regs_no} - {'Inside' if self.in_parking else 'Exited'} "

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Police(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # hashed password
    locations = models.ManyToManyField(Parking, related_name="police_officers")

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        # self.save(update_fields=["password"])

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        locations = ", ".join([loc.username for loc in self.locations.all()])
        return f"{self.username}---------------------({locations})"      
