import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.models import Agent, AgentAssignment
from app.schemas.agent import AgentSchema,AgentAssignmentSchema
from passlib.context import CryptContext
from app.utility.generate_token import sign_jwt
from app.utility.send_mail import send_otp,verify_otp
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize a CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get all agents
@router.get("/agents", response_model=list[AgentSchema])
async def get_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent))
    agents = result.scalars().all()  # Fetching the result as a list of agents
    return agents

# Get a specific agent by ID
@router.get("/agents/{agent_id}", response_model=AgentSchema)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.execute(select(Agent).filter(Agent.uid == agent_id))
    if not agent:
        return JSONResponse({"error": "Agent not found"}, status_code=404)
    return agent



@router.post("/agents", response_model=AgentSchema)
async def create_agent(request: Request, db: AsyncSession = Depends(get_db)):
    # Check if required fields are present
    print(f"Request: {await request.json()}")
    data = await request.json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not first_name:
        return JSONResponse({"error": "First name is required"}, status_code=400)
    
    if not last_name:
        return JSONResponse({"error": "Last name is required"}, status_code=400)
    
    if not email:
        return JSONResponse({"error": "Email is required"}, status_code=400)
    
    if not phone:
        return JSONResponse({"error": "Phone is required"}, status_code=400)

    # Check if email already exists
    existing_mail = await db.execute(select(Agent).where(Agent.email == email))
    existing_mail = existing_mail.scalars().first()
    if existing_mail:
        return JSONResponse({"error": "Email already exists"}, status_code=400)

    # Check if phone number already exists
    existing_phone = await db.execute(select(Agent).where(Agent.phone == phone))
    existing_phone = existing_phone.scalars().first()
    if existing_phone:
        return JSONResponse({"error": "Phone number already exists"}, status_code=400)

    # Hash the password before saving it to the database
    hashed_password = pwd_context.hash(password)
    
    # Replace password with the hashed version
    data["password"] = hashed_password
    
    # Create Agent instance
    agent = Agent(**data)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return JSONResponse(
        {
            "message": "Agent created successfully"
        }
    )


# Login Agent
@router.post('/agent-login/', response_model=AgentSchema)
async def login_agent(request:Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()

        email = data.get('email')
        password = data.get('password')

        if not email:
            return JSONResponse({"error":"email is required"},status_code=400)
        
        if not password:
            return JSONResponse({"error":"password is required"},status_code=400)

        # Fetch the agent by email
        result = await db.execute(select(Agent).where(Agent.email == email))
        agent = result.scalars().first()

        if not agent:
            return JSONResponse({"error":"Agent not found with the given email"},status_code=400)
        

        # Verify the password
        if not pwd_context.verify(password, agent.password):
            return JSONResponse({"error":"Invalid credentials"},status_code=400)
        user_token = sign_jwt(agent.email)

        return JSONResponse(
            {
            "message": "User logged in successfully",
            "access_token": user_token.get("access_token")
           },status_code=200
        )

    except Exception as e:
        logger.warning(f"Error during agent login: {e}")
        return JSONResponse({"error":"An error occurred"},status_code=500)
    



@router.post('/forgot-password/', response_model=AgentSchema)
async def forgot_password(request:Request,db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get('email')

        if not email:
            return JSONResponse({"error":"email is required"},status_code=400)
        
        # Fetch the agent by email
        result = await db.execute(select(Agent).where(Agent.email == email))
        agent = result.scalars().first()
        if not agent:
            return JSONResponse({"error":"Agent not found with the given email"},status_code=400)
        
        send_otp(agent.email)

        return JSONResponse({"message":"OTP sent successfully"},status_code=200)
        
        

    except Exception as e:
        logger.warning(f"Error during agent login: {e}")
        return JSONResponse({"error":"An error occurred"},status_code=500)
    

@router.post('/verify-otp/', response_model=AgentSchema)
async def verify_agent_otp(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get("email")
        otp = data.get("otp")

        if not email:
            return JSONResponse({"error": "email is required"}, status_code=400)

        if not otp:
            return JSONResponse({"error": "otp is required"}, status_code=400)

        # Fetch the agent by email
        result = await db.execute(select(Agent).where(Agent.email == email))
        agent = result.scalars().first()
        if not agent:
            return JSONResponse({"error": "Agent not found with the given email"}, status_code=400)

        # Ensure this call is awaited
        ver = verify_otp(agent.email, otp)
        print(f"verify otp status {ver}")

        if ver == True:
            return JSONResponse({"message": "OTP verified successfully"}, status_code=200)
        elif ver == None:
            return JSONResponse({"error": "OTP has expired"}, status_code=400)

        return JSONResponse({"error": "Invalid OTP"}, status_code=400)

    except Exception as e:
        logger.warning(f"Error during agent verification: {e}")
        return JSONResponse({"error": "An error occurred"}, status_code=500)

    

@router.post('/reset-password/', response_model=AgentSchema)
async def reset_password(request:Request,db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not email:
            return JSONResponse({"error":"email is required"},status_code=400)
        
        if not password:
            return JSONResponse({"error":"password is required"},status_code=400)
        
        if not confirm_password:
            return JSONResponse({"error":"confirm_password is required"},status_code=400)
        
        if password != confirm_password:
            return JSONResponse({"error":"Passwords do not match"},status_code=400)
        
        
        # Fetch the agent by email
        result = await db.execute(select(Agent).where(Agent.email == email))
        agent = result.scalars().first()
        if not agent:
            return JSONResponse({"error":"Agent not found with the given email"},status_code=400)
        
        if pwd_context.verify(password,agent.password):
            return JSONResponse({"error":"New password cannot be the same as the old password"},status_code=400) 
        
        hashed_password = pwd_context.hash(password)
        agent.password = hashed_password
        await db.commit()
        return JSONResponse({"message":"Password reset successfully"},status_code=200)
    
    except Exception as e:
        logger.warning(f"Error during agent reset password: {e}")
        return JSONResponse({"error":"An error occurred"},status_code=500)
    
    


@router.put('/update-agent/{agent_id}', response_model=AgentSchema)
async def update_agent(
    agent_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await request.json()

        agent = await db.get(Agent, agent_id)
        if not agent:
            return JSONResponse({"error": "Agent not found"}, status_code=404)

        # Update only provided fields
        for key, value in data.items():
            if hasattr(agent, key) and value is not None:
                setattr(agent, key, value)

        await db.commit()
        await db.refresh(agent)
        return agent 

    except Exception as e:
        logger.warning(f"Error during agent update: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    


@router.delete('/agents/{agent_id}', response_model=AgentSchema)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Agent).filter(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        await db.delete(agent)
        await db.commit()

        return JSONResponse({"message": "Agent deleted successfully"}, status_code=200)

    except Exception as e:
        logger.warning(f"Error during agent deletion: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    


"""

Agent Assignment Routes

"""

@router.get('/assignments/', response_model=list[AgentAssignmentSchema])
async def get_agents_assignments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentAssignment))
    agents = result.scalars().all()  # Fetching the result as a list of agents
    return agents

# Get a specific agent by ID
@router.get("/assignment/{agent_assignment_id}", response_model=AgentAssignmentSchema)
async def get_agent_assignment(agent_assignment_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.get(AgentAssignment, agent_assignment_id)
    if not agent:
        return JSONResponse({"error": "Agent not found"}, status_code=404)
    return agent

# get assignments for a specific agent
@router.get("/assignments/{agent_id}", response_model=List[AgentAssignmentSchema])
async def get_agent_assignments(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentAssignment).where(AgentAssignment.agent_id == str(agent_id)))
    agents = result.scalars().all()
    
    if not agents:
        raise HTTPException(status_code=404, detail="No assignments found for this agent.")

    return agents



@router.post('/assignments/', response_model=AgentAssignmentSchema)
async def create_agent_assignment(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        agent_id = data.get("agent_id")
        assignment_id = data.get("assignment_id")
        action = data.get("action")
        property_id = data.get("property_id")

        if not agent_id:
            return JSONResponse({"error": "Agent ID is required"}, status_code=400)
        
        if not assignment_id:
            return JSONResponse({"error": "Assignment ID is required"}, status_code=400)
        
        if not action:
            return JSONResponse({"error": "Action is required"}, status_code=400)
        
        if not property_id:
            return JSONResponse({"error": "Property ID is required"}, status_code=400)
        
        agent_data = await db.execute(select(Agent).where(Agent.uid == agent_id))
        agent = agent_data.scalars().first()
        if not agent:
            return JSONResponse({"error": "Agent not found"}, status_code=400)

        assignment = AgentAssignment(**data)
        db.add(assignment)
        await db.commit()

        return JSONResponse(
            {
                "message": "Agent assignment created successfully"
            }, status_code=201
        ) 
        
    except Exception as e:
        logger.warning(f"Error during agent assignment creation: {e}")
        return JSONResponse({"error": "An error occurred"}, status_code=500)









# @router.post('/assign-agent/', response_model=AgentSchema)




