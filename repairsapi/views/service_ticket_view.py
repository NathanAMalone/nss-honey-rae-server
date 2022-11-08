"""View module for handling requests for customer data"""
from dataclasses import fields
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket
from repairsapi.models.customer import Customer
from repairsapi.models.employee import Employee


class ServiceTicketView(ViewSet):
    """Honey Rae API service_tickets view"""

    def destroy(self, request, pk=None):
        """Handle DELETE requests for service tickets

        Returns:
            Response: None with 204 status code
        """
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    
    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Handle PUT requests for single customer
        
        Returns:
            Response -- No response body. Just 204 status code.
        """

        # Select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        # Get the employee id from the client request
        employee_id = request.data['employee']['id']

        # Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)
        
        # Assign that Employee instance to the employee property of the ticket
        ticket.employee = assigned_employee

        ticket.date_completed = request.data['dateCompleted']

        # Save the updated ticket
        ticket.save( )

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """Handle GET requests to get all service_tickets

        Returns:
            Response -- JSON serialized list of service_tickets
        """

        service_tickets = []

        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = ServiceTicket.objects.filter(date_completed__isnull=False)

                elif request.query_params['status'] == "unclaimed":
                    service_tickets = ServiceTicket.objects.filter(date_completed__isnull=True, employee__isnull=True)

                elif request.query_params['status'] == "inprogress":
                    service_tickets = ServiceTicket.objects.filter(date_completed__isnull=True, employee__isnull=False)

                # elif any(status_value == request.query_params['status'] for status_value in ('claimed', 'inprogress')):
                #     service_tickets = ServiceTicket.objects.filter(employee__isnull=False, date_completed__isnull=True, )

                elif request.query_params['status'] == "all":
                    # pass
                    service_tickets = ServiceTicket.objects.all()
                
                else:
                    return Response({ "message": 'Invalid-status must be equal to "done", "all", "unclaimed", or "inprogress".'}, status.HTTP_400_BAD_REQUEST)
                
        else:
            service_tickets = ServiceTicket.objects.filter(date_completed__isnull=False)

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

class TicketEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'address', 'full_name')

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service_tickets"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'description', 'emergency', 'date_completed', 'customer', 'employee')
        depth = 1