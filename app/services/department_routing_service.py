from sqlalchemy.orm import Session
from app.models import Department, CategoryDepartmentMapping
import logging

logger = logging.getLogger(__name__)

class DepartmentRoutingService:
    @staticmethod
    def get_department_for_issue(category: str, subcategory: str, db: Session) -> int:
        """
        Get the appropriate department ID for an issue based on category and subcategory
        Returns None if no mapping found (keeps existing behavior)
        
        Args:
            category: Issue category (e.g., "Solid Waste & Sanitation")
            subcategory: Issue subcategory (e.g., "Uncollected garbage")
            db: Database session
            
        Returns:
            department_id: ID of the department that should handle this issue, or None
        """
        try:
            # Look for exact match
            mapping = db.query(CategoryDepartmentMapping).filter(
                CategoryDepartmentMapping.category == category,
                CategoryDepartmentMapping.subcategory == subcategory,
                CategoryDepartmentMapping.is_active == True
            ).first()
            
            if mapping:
                logger.info(f"Found department mapping: {category} -> {subcategory} -> Department {mapping.department_id}")
                return mapping.department_id
            
            logger.info(f"No department mapping found for: {category} -> {subcategory}")
            return None  # Return None if no mapping found
            
        except Exception as e:
            logger.error(f"Error in department routing: {str(e)}")
            return None
    
    @staticmethod
    def get_all_mappings(db: Session):
        """Get all active category-department mappings"""
        return db.query(CategoryDepartmentMapping).filter(
            CategoryDepartmentMapping.is_active == True
        ).all()
    
    @staticmethod
    def create_mapping(category: str, subcategory: str, department_id: int, db: Session):
        """Create a new category-department mapping"""
        # Check if mapping already exists
        existing = db.query(CategoryDepartmentMapping).filter(
            CategoryDepartmentMapping.category == category,
            CategoryDepartmentMapping.subcategory == subcategory
        ).first()
        
        if existing:
            raise ValueError(f"Mapping already exists for {category} -> {subcategory}")
        
        mapping = CategoryDepartmentMapping(
            category=category,
            subcategory=subcategory,
            department_id=department_id
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping

# Create global instance
department_routing_service = DepartmentRoutingService()