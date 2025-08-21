# api/serializers.py

from rest_framework import serializers
from .models import Department, Employee, LeaveApplication

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    # We include department details for better readability in the API response
    department = DepartmentSerializer(read_only=True)
    
    # THIS IS THE FIX: Use PrimaryKeyRelatedField for the incoming ID.
    # This field is designed to handle converting a primary key into a model object.
    departmentId = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True,
        source='department'
    )

    class Meta:
        model = Employee
        fields = ['id', 'name', 'baseSalary', 'department', 'departmentId']
        extra_kwargs = {
            'baseSalary': {'required': False} # Not required on initial creation
        }


class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ['employee', 'month', 'year', 'leaves']
