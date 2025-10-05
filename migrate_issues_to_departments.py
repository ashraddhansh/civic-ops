from app.core.dependencies import get_db
from app.models import Issue, CategoryDepartmentMapping
from app.services.department_routing_service import department_routing_service
from sqlalchemy.orm import Session

def migrate_existing_issues_to_departments():
    """Assign departments to existing issues based on their category/subcategory"""
    
    db = next(get_db())
    
    try:
        # Get all issues without department assignment
        issues_without_dept = db.query(Issue).filter(Issue.department_id == None).all()
        
        print(f"Found {len(issues_without_dept)} issues without department assignment")
        
        updated_count = 0
        skipped_count = 0
        
        for issue in issues_without_dept:
            try:
                # Try to get department for this issue
                department_id = department_routing_service.get_department_for_issue(
                    category=issue.category,
                    subcategory=issue.subcategory or "",
                    db=db
                )
                
                if department_id:
                    issue.department_id = department_id
                    updated_count += 1
                    print(f"✅ Issue {issue.issue_id}: {issue.category} -> {issue.subcategory} -> Department {department_id}")
                else:
                    skipped_count += 1
                    print(f"⚠️  Issue {issue.issue_id}: No mapping found for {issue.category} -> {issue.subcategory}")
                    
            except Exception as e:
                skipped_count += 1
                print(f"❌ Issue {issue.issue_id}: Error - {str(e)}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Migration Complete!")
        print(f"✅ Updated: {updated_count} issues")
        print(f"⚠️  Skipped: {skipped_count} issues")
        
        # Show summary by department
        print(f"\n📊 Issues by Department:")
        from app.models import Department
        departments = db.query(Department).all()
        for dept in departments:
            count = db.query(Issue).filter(Issue.department_id == dept.id).count()
            print(f"  {dept.name}: {count} issues")
        
        unassigned_count = db.query(Issue).filter(Issue.department_id == None).count()
        print(f"  Unassigned: {unassigned_count} issues")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_existing_issues_to_departments()