from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ===== Existing demo models (keep) =====
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# ===== Product Models =====
class RegistryCreate(BaseModel):
    couple_names: str
    event_date: Optional[str] = None  # YYYY-MM-DD
    location: Optional[str] = None
    currency: str = "AED"
    hero_image: Optional[str] = None
    slug: str

class Registry(RegistryCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RegistryUpdate(BaseModel):
    couple_names: Optional[str] = None
    event_date: Optional[str] = None
    location: Optional[str] = None
    currency: Optional[str] = None
    hero_image: Optional[str] = None
    slug: Optional[str] = None

class FundIn(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    goal: float = 0
    cover_url: Optional[str] = None
    category: Optional[str] = None

class Fund(FundIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContributionIn(BaseModel):
    fund_id: str
    name: Optional[str] = None
    amount: float
    message: Optional[str] = None
    public: bool = True
    method: Optional[str] = None

class Contribution(ContributionIn):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PublicRegistryResponse(BaseModel):
    registry: Registry
    funds: List[Dict[str, Any]]  # Fund + {raised, progress}
    totals: Dict[str, float]

# ===== Routes =====
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(client_name=input.client_name)
    await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# --- Registries ---
@api_router.post("/registries", response_model=Registry, status_code=201)
async def create_registry(payload: RegistryCreate):
    # Uniqueness check for slug
    existing = await db.registries.find_one({"slug": payload.slug})
    if existing:
        raise HTTPException(status_code=409, detail="Slug already in use")
    reg = Registry(**payload.model_dump())
    await db.registries.insert_one(reg.model_dump())
    return reg

@api_router.put("/registries/{registry_id}", response_model=Registry)
async def update_registry(registry_id: str, patch: RegistryUpdate):
    update_doc = {k: v for k, v in patch.model_dump().items() if v is not None}
    update_doc["updated_at"] = datetime.utcnow()
    result = await db.registries.find_one_and_update(
        {"id": registry_id}, {"$set": update_doc}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Registry not found")
    return Registry(**result)

@api_router.get("/registries/{slug}/public", response_model=PublicRegistryResponse)
async def get_registry_public(slug: str):
    reg_doc = await db.registries.find_one({"slug": slug})
    if not reg_doc:
        raise HTTPException(status_code=404, detail="Registry not found")

    funds = await db.funds.find({"registry_id": reg_doc["id"]}).to_list(1000)

    # Compute sums per fund
    response_funds: List[Dict[str, Any]] = []
    total_raised = 0.0
    for f in funds:
        # Remove MongoDB _id field to avoid serialization issues
        if "_id" in f:
            del f["_id"]
            
        agg = await db.contributions.aggregate([
            {"$match": {"fund_id": f["id"]}},
            {"$group": {"_id": None, "sum": {"$sum": "$amount"}}},
        ]).to_list(1)
        raised = float(agg[0]["sum"]) if agg else 0.0
        total_raised += raised
        progress = min(100, round((raised / float(f.get("goal") or 1)) * 100)) if f.get("goal") else 0
        response_funds.append({**f, "raised": raised, "progress": progress})

    # Remove MongoDB _id field from registry doc
    if "_id" in reg_doc:
        del reg_doc["_id"]

    return PublicRegistryResponse(
        registry=Registry(**reg_doc),
        funds=response_funds,
        totals={"raised": total_raised},
    )

# --- Funds ---
@api_router.post("/registries/{registry_id}/funds/bulk_upsert")
async def bulk_upsert_funds(registry_id: str, body: Dict[str, List[FundIn]]):
    funds_in = body.get("funds", [])
    created = 0
    updated = 0
    for f in funds_in:
        data = f.model_dump()
        now = datetime.utcnow()
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())
        existing = await db.funds.find_one({"id": data["id"]})
        if existing:
            data["updated_at"] = now
            await db.funds.update_one({"id": data["id"]}, {"$set": data})
            updated += 1
        else:
            doc = Fund(**{**data, "registry_id": registry_id, "created_at": now, "updated_at": now})
            await db.funds.insert_one(doc.model_dump())
            created += 1
    return {"created": created, "updated": updated}

@api_router.get("/registries/{registry_id}/funds", response_model=List[Fund])
async def list_funds(registry_id: str):
    items = await db.funds.find({"registry_id": registry_id}).to_list(1000)
    return [Fund(**it) for it in items]

# --- Contributions ---
@api_router.post("/contributions", response_model=Contribution, status_code=201)
async def create_contribution(payload: ContributionIn):
    # Validate fund exists
    fund = await db.funds.find_one({"id": payload.fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    contrib = Contribution(**payload.model_dump())
    await db.contributions.insert_one(contrib.model_dump())
    return contrib

@api_router.get("/funds/{fund_id}/contributions", response_model=List[Contribution])
async def list_contributions(fund_id: str):
    items = await db.contributions.find({"fund_id": fund_id}).to_list(1000)
    return [Contribution(**it) for it in items]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()