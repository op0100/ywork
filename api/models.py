# api/models.py

import uuid
from django.db import models

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    baseSalary = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return self.name

class LeaveApplication(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    month = models.CharField(max_length=20) # e.g., "January", "February"
    year = models.CharField(max_length=4)   # e.g., "2024"
    leaves = models.IntegerField(default=0)

    class Meta:
        # Ensures an employee can only have one leave entry per month/year
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee.name} - {self.month} {self.year}"