"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket


class ServiceTicketView(ViewSet):
    """Honey Rae API service_tickets view"""

    def list(self, request):
        """Handle GET requests to get all service_tickets

        Returns:
            Response -- JSON serialized list of service_tickets
        """

        service_tickets = ServiceTicket.objects.all()
        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single service_ticket

        Returns:
            Response -- JSON serialized service_ticket record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(service_ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)


class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service_tickets"""
    class Meta:
        model = ServiceTicket
        fields = ('id', 'description', 'emergency', 'date_completed', 'customer', 'employee')
        depth = 1