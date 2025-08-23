from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_ALGO = 'HS256'
JWT_EXPIRE_MINUTES = int(os.environ.get('JWT_EXPIRE_MINUTES', '1440'))  # 24h default

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


# ===== Auth Models =====
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


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
    owner_id: str
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


# ===== Auth helpers =====
async def find_user_by_email(email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email.lower()})

async def find_user_by_id(user_id: str) -> Optional[dict]:
    return await db.users.find_one({"id": user_id})

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject, "iat": datetime.utcnow()}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)

async def get_current_user(authorization: str = Depends(lambda: None)) -> UserPublic:
    # Manually extract Authorization header via Starlette request state
    from fastapi import Request
    def _get_auth(req: Request):
        return req.headers.get("Authorization")
    # Hack to get request in Depends
    try:
        from fastapi import Request
        req = Request  # type: ignore
    except Exception:
        pass
    # FastAPI pattern: create an inner dependency to read header
    # But simpler: use os.environ not needed. We'll read via workaround in route using Depends(get_user_from_token)
    raise RuntimeError("get_current_user should be injected via get_user_from_token")

from fastapi import Header
async def get_user_from_token(authorization: Optional[str] = Header(None)) -> UserPublic:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_doc = await find_user_by_id(user_id)
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    # sanitize
    user_doc.pop("_id", None)
    user_doc.pop("password_hash", None)
    return UserPublic(**user_doc)


# ===== Routes =====
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# --- Auth ---
@api_router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(body: UserCreate):
    email = body.email.lower()
    existing = await find_user_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=body.name, email=email, password_hash=hash_password(body.password))
    await db.users.insert_one(user.model_dump())
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserPublic(id=user.id, name=user.name, email=user.email))

class LoginBody(BaseModel):
    email: EmailStr
    password: str

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginBody):
    email = body.email.lower()
    user = await find_user_by_email(email)
    if not user or not verify_password(body.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user["id"])
    return TokenResponse(access_token=token, user=UserPublic(id=user["id"], name=user["name"], email=user["email"]))

@api_router.get("/auth/me", response_model=UserPublic)
async def me(current: UserPublic = Depends(get_user_from_token)):
    return current

# --- Status (keep) ---
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(client_name=input.client_name)
    await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# --- Registries (auth required except public view) ---
@api_router.post("/registries", response_model=Registry, status_code=201)
async def create_registry(payload: RegistryCreate, current: UserPublic = Depends(get_user_from_token)):
    # Uniqueness check for slug
    existing = await db.registries.find_one({"slug": payload.slug})
    if existing:
        raise HTTPException(status_code=409, detail="Slug already in use")
    reg = Registry(**payload.model_dump(), owner_id=current.id)
    await db.registries.insert_one(reg.model_dump())
    return reg

@api_router.put("/registries/{registry_id}", response_model=Registry)
async def update_registry(registry_id: str, patch: RegistryUpdate, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    update_doc = {k: v for k, v in patch.model_dump().items() if v is not None}
    update_doc["updated_at"] = datetime.utcnow()
    await db.registries.update_one({"id": registry_id}, {"$set": update_doc})
    reg.update(update_doc)
    reg.pop("_id", None)
    return Registry(**reg)

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
async def bulk_upsert_funds(registry_id: str, body: Dict[str, List[FundIn]], current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Not allowed")

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
async def list_funds(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    items = await db.funds.find({"registry_id": registry_id}).to_list(1000)
    return [Fund(**{k: v for k, v in it.items() if k != "_id"}) for it in items]

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
async def list_contributions(fund_id: str, current: Optional[UserPublic] = Depends(get_user_from_token)):
    # Only registry owners should access; we could check ownership by joining via fund -> registry
    fund = await db.funds.find_one({"id": fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    reg = await db.registries.find_one({"id": fund.get("registry_id")})
    if not reg or (current and reg.get("owner_id") != current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
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