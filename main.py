from fastapi import FastAPI
from app.routes import agent
app = FastAPI()

# Include routers
app.include_router(agent.router, prefix="/api", tags=["Agents"])
# app.include_router(assignment.router, prefix="/api", tags=["Assignments"])
# app.include_router(tracking.router, prefix="/api", tags=["Tracking"])
