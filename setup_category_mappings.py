from app.models import Department, CategoryDepartmentMapping
from app.core.dependencies import get_db
from sqlalchemy.orm import Session

def setup_category_department_mappings():
    """Setup the category to department mappings based on your requirements"""
    
    db = next(get_db())
    
    try:
        # First, get all department IDs
        solid_waste_dept = db.query(Department).filter(Department.name == "Solid waste management").first()
        garden_dept = db.query(Department).filter(Department.name == "Garden Department").first()
        pollution_dept = db.query(Department).filter(Department.name == "Pollution Department").first()
        streetlight_dept = db.query(Department).filter(Department.name == "Streetlighting Department").first()
        
        if not all([solid_waste_dept, garden_dept, pollution_dept, streetlight_dept]):
            print("Error: Some departments are missing. Please run the department setup script first.")
            return
        
        # Define the mappings based on your issue types
        mappings = [
            # Solid Waste & Sanitation -> Solid Waste Management Department
            {"category": "Solid Waste & Sanitation", "subcategory": "Uncollected garbage", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "Overflowing bins", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "No garbage bin available", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "Improper segregation of waste", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "Dead animal carcass", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "Illegal dumping / construction debris", "dept_id": solid_waste_dept.id},
            {"category": "Solid Waste & Sanitation", "subcategory": "Burning of waste", "dept_id": solid_waste_dept.id},
            
            # Street Lighting & Electricity -> Streetlighting Department
            {"category": "Street Lighting & Electricity", "subcategory": "Streetlight not working", "dept_id": streetlight_dept.id},
            {"category": "Street Lighting & Electricity", "subcategory": "Streetlight flickering", "dept_id": streetlight_dept.id},
            {"category": "Street Lighting & Electricity", "subcategory": "Broken streetlight pole", "dept_id": streetlight_dept.id},
            {"category": "Street Lighting & Electricity", "subcategory": "Dark spots (no streetlight in area)", "dept_id": streetlight_dept.id},
            {"category": "Street Lighting & Electricity", "subcategory": "Exposed electric wires", "dept_id": streetlight_dept.id},
            
            # Parks & Public Spaces -> Garden Department
            {"category": "Parks & Public Spaces", "subcategory": "Broken benches", "dept_id": garden_dept.id},
            {"category": "Parks & Public Spaces", "subcategory": "Damaged play equipment", "dept_id": garden_dept.id},
            {"category": "Parks & Public Spaces", "subcategory": "Overgrown grass / poor maintenance", "dept_id": garden_dept.id},
            {"category": "Parks & Public Spaces", "subcategory": "Littering in parks", "dept_id": garden_dept.id},
            {"category": "Parks & Public Spaces", "subcategory": "Non-functional fountains / facilities", "dept_id": garden_dept.id},
            {"category": "Parks & Public Spaces", "subcategory": "Tree maintenance (fallen tree, trimming required)", "dept_id": garden_dept.id},
            
            # Pollution & Environment -> Pollution Department
            {"category": "Pollution & Environment", "subcategory": "Air pollution (burning, dust)", "dept_id": pollution_dept.id},
            {"category": "Pollution & Environment", "subcategory": "Water pollution (industrial waste, sewage discharge)", "dept_id": pollution_dept.id},
            {"category": "Pollution & Environment", "subcategory": "Noise pollution (loudspeakers, vehicles)", "dept_id": pollution_dept.id},
            {"category": "Pollution & Environment", "subcategory": "Deforestation / tree cutting", "dept_id": pollution_dept.id},
        ]
        
        # Create mappings
        created_count = 0
        for mapping_data in mappings:
            # Check if mapping already exists
            existing = db.query(CategoryDepartmentMapping).filter(
                CategoryDepartmentMapping.category == mapping_data["category"],
                CategoryDepartmentMapping.subcategory == mapping_data["subcategory"]
            ).first()
            
            if not existing:
                mapping = CategoryDepartmentMapping(
                    category=mapping_data["category"],
                    subcategory=mapping_data["subcategory"],
                    department_id=mapping_data["dept_id"]
                )
                db.add(mapping)
                created_count += 1
                print(f"✅ Created mapping: {mapping_data['category']} -> {mapping_data['subcategory']}")
            else:
                print(f"⚠️  Mapping already exists: {mapping_data['category']} -> {mapping_data['subcategory']}")
        
        db.commit()
        print(f"\n🎉 Setup complete! Created {created_count} new mappings.")
        
        # Print summary
        print("\n📊 Department Mapping Summary:")
        print(f"🗑️  Solid Waste Management: {solid_waste_dept.name} (ID: {solid_waste_dept.id})")
        print(f"🌳 Garden Department: {garden_dept.name} (ID: {garden_dept.id})")
        print(f"🏭 Pollution Department: {pollution_dept.name} (ID: {pollution_dept.id})")
        print(f"💡 Streetlighting Department: {streetlight_dept.name} (ID: {streetlight_dept.id})")
        
    except Exception as e:
        print(f"❌ Error setting up mappings: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_category_department_mappings()