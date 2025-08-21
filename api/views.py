# api/views.py

from django.db.models import F, Window
from django.db.models.functions import DenseRank
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Department, Employee, LeaveApplication
from .serializers import DepartmentSerializer, EmployeeSerializer

# 1. POST API to create a department
class DepartmentCreateAPIView(APIView):
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. POST API to create an employee
class EmployeeCreateAPIView(APIView):
    def post(self, request):
        # Set a default baseSalary if not provided
        if 'baseSalary' not in request.data:
            request.data['baseSalary'] = 0
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. POST API to set base salary for an employee
class SetBaseSalaryAPIView(APIView):
    def post(self, request):
        employee_id = request.data.get('employeeId')
        salary = request.data.get('baseSalary')
        if not employee_id or salary is None:
            return Response({"error": "employeeId and baseSalary are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.baseSalary = salary
            employee.save()
            return Response({"success": f"Base salary for {employee.name} updated to {salary}."}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

# 4. UPDATE API to increase a leave count of an employee
class UpdateLeaveCountAPIView(APIView):
    def patch(self, request):
        employee_id = request.data.get('employeeId')
        month = request.data.get('month')
        year = request.data.get('year')
        leaves_to_add = request.data.get('leaves', 1) # Default to adding 1 leave

        if not all([employee_id, month, year]):
            return Response({"error": "employeeId, month, and year are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            leave_app, created = LeaveApplication.objects.get_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={'leaves': 0}
            )
            leave_app.leaves += int(leaves_to_add)
            leave_app.save()
            return Response({
                "success": f"Updated leaves for {employee.name} in {month} {year}.",
                "total_leaves": leave_app.leaves
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

# 5. POST API to calculate payable salary
class CalculatePayableSalaryAPIView(APIView):
    def post(self, request):
        employee_id = request.data.get('employeeId')
        month = request.data.get('month')
        year = request.data.get('year')

        if not all([employee_id, month, year]):
            return Response({"error": "employeeId, month, and year are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            leave_app = LeaveApplication.objects.filter(employee=employee, month=month, year=year).first()
            
            leaves = leave_app.leaves if leave_app else 0
            base_salary = employee.baseSalary

            if base_salary == 0:
                 return Response({"payable_salary": 0, "message": "Base salary is 0."}, status=status.HTTP_200_OK)

            deduction = leaves * (base_salary / 25)
            payable_salary = base_salary - deduction

            return Response({"payable_salary": payable_salary}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

# 6. GET API to find high earners in a department
class HighEarnersInDepartmentAPIView(APIView):
    def get(self, request, department_id):
        try:
            # Rank employees by salary within the department
            department_employees = Employee.objects.filter(department_id=department_id).annotate(
                salary_rank=Window(
                    expression=DenseRank(),
                    order_by=F('baseSalary').desc()
                )
            ).order_by('-baseSalary')

            # Filter for the top 3 ranks
            high_earners = department_employees.filter(salary_rank__lte=3)

            if not high_earners.exists():
                return Response({"message": "No employees found in this department."}, status=status.HTTP_200_OK)

            serializer = EmployeeSerializer(high_earners, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
             return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 7. GET API to find high earners in a specific month
class HighEarnersByMonthAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not all([month, year]):
            return Response({"error": "month and year query parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        employees = Employee.objects.all()
        salaries = []

        for emp in employees:
            leave_app = LeaveApplication.objects.filter(employee=emp, month=month, year=year).first()
            leaves = leave_app.leaves if leave_app else 0
            base_salary = emp.baseSalary
            
            if base_salary > 0:
                deduction = leaves * (base_salary / 25)
                payable_salary = base_salary - deduction
                salaries.append({
                    "employee_id": emp.id,
                    "name": emp.name,
                    "department": emp.department.name,
                    "payable_salary": payable_salary
                })

        # Sort by payable salary and get the top 3
        top_earners = sorted(salaries, key=lambda x: x['payable_salary'], reverse=True)[:3]

        return Response(top_earners, status=status.HTTP_200_OK)