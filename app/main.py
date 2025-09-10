from fastapi import FastAPI
from routers import auth, users

app = FastAPI(title="Your App", version="1.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "API is running"}
