from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import products, orders
from app.db.init_db import create_tables

app = FastAPI(
    title="E-Commerce API",
    description="A RESTful API for an e-commerce platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

# Include routers
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/", tags=["health"])
async def health_check():
    return {"status": "healthy", "message": "E-Commerce API is running"} 