from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
import socket
from django.http import JsonResponse

from PARK_EYE.models import Suspected, Police, VehicleRecord, Location, Parking
from .serializers import (
    SuspectedSerializer,
    PoliceSerializer,
    VehicleRecordSerializer,
    LocationSerializer
)

# ------------------ MODEL VIEWSETS ------------------

class SuspectedViewSet(viewsets.ModelViewSet):
    queryset = Suspected.objects.all().order_by('-date_time')
    serializer_class = SuspectedSerializer


class VehicleRecordViewSet(viewsets.ModelViewSet):
    queryset = VehicleRecord.objects.all().order_by('-in_date_time')
    serializer_class = VehicleRecordSerializer

    def list(self, request, *args, **kwargs):
        """
        Optionally filter vehicle records by a given date (?date=YYYY-MM-DD).
        """
        date_str = request.query_params.get("date", None)
        parking_id = request.query_params.get("parking_id", None)
        parking = get_object_or_404(Parking, id=parking_id) if parking_id else None
        queryset = self.get_queryset()

        if date_str:
            try:
                # Parse the given date
                from datetime import datetime
                from django.utils.timezone import make_aware

                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                start_of_day = make_aware(datetime.combine(date_obj, datetime.min.time()))
                end_of_day = make_aware(datetime.combine(date_obj, datetime.max.time()))

                # Filter records where in_date_time is within the day
                queryset = queryset.filter(in_date_time__range=(start_of_day, end_of_day), parking=parking)

            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PoliceViewSet(viewsets.ModelViewSet):
    queryset = Police.objects.all()
    serializer_class = PoliceSerializer


# ------------------ CUSTOM API ENDPOINTS ------------------

@api_view(["POST"])
def add_suspected_vehicle(request):
    """
    API to add a suspected vehicle
    """
    serializer = SuspectedSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(date_time=now(), is_founded=False)
        return Response({"message": "Suspected vehicle added successfully", "data": serializer.data},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def police_login_check(request):
    """
    API for police login authentication
    """
    username = request.data.get("username")
    password = request.data.get("password")
    try:
        police = Police.objects.get(username=username)
        if police.check_password(password):
            return Response({
                "message": "Login successful",
                "police_id": police.id,
                "username": police.username,
                "locations": list(police.locations.values_list("username", flat=True))
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
    except Police.DoesNotExist:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def police_dashboard(request, police_id):
    """
    API for police dashboard - fetch suspected vehicles in police assigned locations
    """
    police = get_object_or_404(Police, id=police_id)
    police_locations = police.locations.values_list("username", flat=True)

    suspected_vehicles = Suspected.objects.filter(found_location__in=police_locations , is_founded=False).order_by('-date_time')
    serializer = SuspectedSerializer(suspected_vehicles, many=True)

    return Response({
        "police": {
            "id": police.id,
            "username": police.username,
            "locations": list(police_locations)
        },
        "suspected_vehicles": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def parking_login_check(request):
    """
    API for parking owner login authentication
    """
    username = request.data.get("username")
    password = request.data.get("password")
    print(username,password)

    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        parking = Parking.objects.get(username=username)
        if parking.check_password(password):
            return Response({
                "message": "Login successful",
                "parking_id": parking.id,
                "username": parking.username,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": " or password"}, status=status.HTTP_401_UNAUTHORIZED)

    except Parking.DoesNotExist:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)



def check_ipv6(request):
    try:
        socket.getaddrinfo("db.wvepeeooudxzjfkoiuri.supabase.co", 5432, socket.AF_INET6)
        return JsonResponse({"IPv6": "Supported"})
    except Exception as e:
        return JsonResponse({"IPv6": str(e)})     