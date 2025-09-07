from rest_framework import serializers
from PARK_EYE.models import Suspected, VehicleRecord, Location, Police, Parking


class SuspectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspected
        fields = '__all__'


class VehicleRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleRecord
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password=validated_data.pop('password')
        parking = Parking(username=validated_data['username'])
        parking.set_password(password)
        parking.save()
        return parking

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance    


class PoliceSerializer(serializers.ModelSerializer):
    locations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Parking.objects.all()
    )

    class Meta:
        model = Police
        fields = ['id', 'username', 'password', 'locations']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        locations = validated_data.pop('locations', [])
        police = Police(username=validated_data['username'])
        police.set_password(validated_data['password'])
        police.save()
        police.locations.set(locations)
        return police
    
    

    def update(self, instance, validated_data):
        locations = validated_data.pop('locations', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        if locations is not None:
            instance.locations.set(locations)

        instance.save()
        return instance
