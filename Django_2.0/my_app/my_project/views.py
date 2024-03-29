from pstats import Stats
import statistics
from telnetlib import STATUS
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework.decorators import  parser_classes
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from .models import Drone,Medication,DroneMedication,BatteryLog
from .serialize import DroneSerializer,MedicationSerializer,DroneMedicationSerializer,BatteryLogSerializer
from django.core.management.base import BaseCommand


def prevent_overlaod(drone, medication):
    """Checks whether the given drone can carry the specified medication without overloading it"""
    if medication.weight > drone.weight_limit:
        raise Exception(f"The medication {medication.name} is too heavy for the drone {drone.serial_number}")
    
class DroneModelViewSet(viewsets.ModelViewSet):
   queryset = Drone.objects.all()
   serializer_class = DroneSerializer


class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

class DroneMedicationViewSet(viewsets.ModelViewSet):
    queryset = DroneMedication.objects.all()
    serializer_class = DroneMedicationSerializer
    def create(self, request, *args, **kwargs):
        """
        Custom create method to call prevent_drone_overload function.

        """
        drone_id = request.data.get('drone')
        medication_id = request.data.get('medication')

        drone = Drone.objects.get(id=drone_id)
        medication = Medication.objects.get(id=medication_id)

       
        prevent_overlaod(drone, medication)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
        

class BatteryLogViewSet(viewsets.ModelViewSet):
    queryset = BatteryLog.objects.all()
    serializer_class = BatteryLogSerializer



@api_view(['GET'])
@parser_classes([JSONParser])
def drones_with_low_battery(request):
    battery_capacity = request.query_params.get('battery_capacity', None)
    if battery_capacity is None:
        return Response({"error": "Battery capacity is not provided"}, status=STATUS.HTTP_400_BAD_REQUEST)

    try:
        battery_capacity = int(battery_capacity)
    except ValueError:
         return Response({"error": "Invalid battery capacity"}, status=STATUS.HTTP_400_BAD_REQUEST)

    # Get all Drones with a battery_capacity lower than the provided value
    drones = Drone.objects.filter(battery_capacity=battery_capacity)

    # Serialize the Drone instances
    serializer = DroneSerializer(drones, many=True, )

    # Return a response with the serialized Drone instances
    return Response(serializer.data)
    
@api_view(['GET'])
@parser_classes([JSONParser])
def drone_battery(request):
    serial_number= request.query_params.get('serial_number', None)
    if serial_number is None:
        return Response({"error": "Battery capacity is not provided"}, status=STATUS.HTTP_400_BAD_REQUEST)

    try:
        serial_number = int(serial_number)
    except ValueError:
        return Response({"error": "Invalid battery capacity"}, status=STATUS.HTTP_400_BAD_REQUEST)

    # Get all Drones with a battery_capacity lower than the provided value
    drones = Drone.objects.filter(serial_number=serial_number)

    # Serialize only the battery_capacity field of the Drone instances
    serializer = DroneSerializer(drones, many=True, context={'request': request})

    # Return a response with the serialized battery_capacity field
    return Response([d['battery_capacity'] for d in serializer.data])


