#!/usr/bin/env python3
"""
Create sample departments and admin users for the civic issues platform
"""

import sys
sys.path.append('.')

from app.models import Department, AdminUser
from app.services.admin_auth_service import AdminAuthService
from app.database import SessionLocal
from sqlalchemy.orm import Session

def create_departments_and_admins():
    """Create the 4 specific departments and their admin users"""
    db = SessionLocal()
    
    try:
        print("🏛️ Creating Departments and Admin Users...")
        print("=" * 50)
        
        # Create 4 specific departments
        departments = [
            {
                "name": "Solid waste management",
                "code": "SWM",
                "description": "Garbage collection, waste disposal, recycling services"
            },
            {
                "name": "Garden Department",
                "code": "GD",
                "description": "Parks, gardens, tree maintenance, landscaping"
            },
            {
                "name": "Pollution Department",
                "code": "PD",
                "description": "Air quality, noise pollution, environmental monitoring"
            },
            {
                "name": "Streetlighting Department",
                "code": "SLD",
                "description": "Street lights, electrical maintenance, public lighting"
            }
        ]
        
        created_departments = []
        for dept_data in departments:
            existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
                db.commit()
                db.refresh(dept)
                created_departments.append(dept)
                print(f"✅ Created department: {dept.name} ({dept.code})")
            else:
                created_departments.append(existing)
                print(f"ℹ️  Department already exists: {existing.name} ({existing.code})")
        
        print("\n🔐 Creating Admin Users...")
        print("=" * 50)
        
        # Create admin users for each department with simple passwords
        admin_users = [
            {
                "username": "swm_admin",
                "email": "swm@civic.gov",
                "password": "swm123",
                "full_name": "Solid Waste Management Admin",
                "department_code": "SWM"
            },
            {
                "username": "garden_admin",
                "email": "garden@civic.gov",
                "password": "garden123",
                "full_name": "Garden Department Admin",
                "department_code": "GD"
            },
            {
                "username": "pollution_admin",
                "email": "pollution@civic.gov",
                "password": "pollution123",
                "full_name": "Pollution Department Admin",
                "department_code": "PD"
            },
            {
                "username": "lighting_admin",
                "email": "lighting@civic.gov",
                "password": "lighting123",
                "full_name": "Streetlighting Department Admin",
                "department_code": "SLD"
            },
            {
                "username": "super_admin",
                "email": "super@civic.gov",
                "password": "super123",
                "full_name": "System Super Administrator",
                "department_code": "SWM",  # Assign to first department
                "role": "super_admin"
            }
        ]
        
        for admin_data in admin_users:
            existing = db.query(AdminUser).filter(AdminUser.username == admin_data["username"]).first()
            if not existing:
                # Find department
                department = db.query(Department).filter(Department.code == admin_data["department_code"]).first()
                
                if not department:
                    print(f"❌ Department {admin_data['department_code']} not found for {admin_data['username']}")
                    continue
                
                try:
                    admin = AdminAuthService.create_admin_user(
                        username=admin_data["username"],
                        email=admin_data["email"],
                        password=admin_data["password"],
                        full_name=admin_data["full_name"],
                        department_id=department.id,
                        role=admin_data.get("role", "admin"),
                        db=db
                    )
                    print(f"✅ Created admin: {admin.username} for {department.name}")
                except Exception as e:
                    print(f"❌ Failed to create admin {admin_data['username']}: {str(e)}")
            else:
                print(f"ℹ️  Admin already exists: {existing.username}")
        
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("\n📋 ADMIN LOGIN CREDENTIALS:")
        print("=" * 50)
        print("Department: Solid waste management")
        print("  Username: swm_admin")
        print("  Password: swm123")
        print("\nDepartment: Garden Department")
        print("  Username: garden_admin")
        print("  Password: garden123")
        print("\nDepartment: Pollution Department")
        print("  Username: pollution_admin")
        print("  Password: pollution123")
        print("\nDepartment: Streetlighting Department")
        print("  Username: lighting_admin")
        print("  Password: lighting123")
        print("\nSystem Administrator:")
        print("  Username: super_admin")
        print("  Password: super123")
        print("  Role: super_admin (can manage all departments)")
        print("\n💡 Use these credentials to test the admin endpoints!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_departments_and_admins()