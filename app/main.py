from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, admin
from app.services.s3_service import s3_service

app = FastAPI(
    title="Civic Issues Reporting API",
    description="A prototype API for citizens to report civic issues to authorities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "message": "Civic Issues Reporting API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running properly"
    }

@app.get("/s3/health")
def check_s3_health():
    """Check S3 connectivity and bucket access"""
    try:
        bucket_exists = s3_service.check_bucket_exists()
        return {
            "status": "healthy" if bucket_exists else "unhealthy",
            "bucket_name": s3_service.bucket_name,
            "bucket_accessible": bucket_exists
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
