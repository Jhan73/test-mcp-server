import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as DBConnection
from fastmcp import FastMCP

mcp = FastMCP(
    name="company_db_server",
    version="0.1.0",
    description="A FastMCP plugin for PostgreSQL database interactions.",
    author="Jhan",
    author_email="jhan@gmail.com")


def get_db_connection() -> DBConnection:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "company_db"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=RealDictCursor
    )
    return conn

@mcp.tool()
def list_employees(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch a list of employees from the database.
    Args:
        limit (int): The maximum number of employees to retrieve.
    Returns:
        List[Dict[str, Any]]: A list of employees with their details.
    """

    try: 
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                        SELECT id, name, position, department, salary, hire_date 
                        FROM employees
                        ORDER BY hire_date DESC
                        LIMIT %s;""", (limit,))
            employees = cursor.fetchall()
        conn.close()
        return employees
    except Exception as e:
        return {"error": f"It was not possible to hire employees: {str(e)}"}

@mcp.tool()
def get_employee_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch an employee's details by their ID.
    Args:
        employee_id (int): The ID of the employee to retrieve.
    Returns:
        Optional[Dict[str, Any]]: The employee's details or None if not found.
    """

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                        SELECT id, name, position, department, salary, hire_date 
                        FROM employees
                        WHERE id = %s;""", (employee_id,))
            employee = cursor.fetchone()
        conn.close()
        return employee
    except Exception as e:
        return {"error": f"Could not retrieve employee: {str(e)}"}
    
@mcp.tool()
def add_employee(name: str, position: str, department: str, salary: float) -> Dict[str, Any]:
    """
    Add a new employee to the database.
    Args:
        name (str): The name of the employee.
        position (str): The position of the employee.
        department (str): The department of the employee.
        salary (float): The salary of the employee.
    Returns:
        Dict[str, Any]: The details of the newly added employee.
    """

    try:
        if not name.strip():
            return {"error": "Employee name cannot be empty."}
        if not position.strip():
            return {"error": "Employee position cannot be empty."}
        if not department.strip():
            return {"error": "Employee department cannot be empty."}
        if salary <= 0:
            return {"error": "Employee salary must be a positive number."}

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                        INSERT INTO employees (name, position, department, salary, hire_date)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id, name, position, department, salary, hire_date;""",
                        (name, position, department, salary, datetime.now()))
            new_employee = cursor.fetchone()
            conn.commit()
        conn.close()
        return {
                "message": "Employee added successfully.",
                "employee": new_employee
            }
    except Exception as e:
        return {"error": f"Could not add employee: {str(e)}"}


def main():
    mcp.run(transport="sse", host="0.0.0.0", port=3000)


if __name__ == "__main__":
    main()
