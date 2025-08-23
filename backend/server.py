from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, constr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
import io
import csv

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

# File storage
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_TMP = UPLOAD_DIR / "tmp"
UPLOAD_DIR.mkdir(exist_ok=True)
UPLOAD_TMP.mkdir(parents=True, exist_ok=True)
CHUNK_SIZE = 1048576  # 1MB
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Serve uploaded files under /api/files
app.mount("/api/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")

# ===== Utilities =====
async def ensure_indexes():
    await db.users.create_index('email', unique=True)
    await db.registries.create_index('slug', unique=True)
    await db.registries.create_index('owner_id')
    await db.funds.create_index('registry_id')
    await db.funds.create_index('updated_at')
    await db.funds.create_index('order')
    await db.contributions.create_index('fund_id')
    await db.contributions.create_index('created_at')
    await db.uploads.create_index('created_at')

_rate_store: Dict[str, List[float]] = {}

async def rate_limit(req: Request, key: str, limit: int, window_sec: int = 60):
    ip = req.headers.get('x-forwarded-for', req.client.host if req.client else 'unknown')
    k = f"{key}:{ip}"
    now = datetime.now().timestamp()
    lst = _rate_store.get(k, [])
    lst = [t for t in lst if now - t < window_sec]
    if len(lst) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests, please try again later")
    lst.append(now)
    _rate_store[k] = lst

# ===== Existing demo models (keep minimal) =====
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
Slug = constr(pattern=r"^[a-z0-9-]+$", min_length=3, max_length=64)
Currency = constr(pattern=r"^[A-Z]{3}$")

class RegistryCreate(BaseModel):
    couple_names: str
    event_date: Optional[str] = None  # YYYY-MM-DD
    location: Optional[str] = None
    currency: Currency = "AED"
    hero_image: Optional[str] = None
    slug: Slug
    theme: Optional[str] = "modern"  # modern | serif | pastel | dark

class Registry(RegistryCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    collaborators: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RegistryUpdate(BaseModel):
    couple_names: Optional[str] = None
    event_date: Optional[str] = None
    location: Optional[str] = None
    currency: Optional[Currency] = None
    hero_image: Optional[str] = None
    slug: Optional[Slug] = None
    theme: Optional[str] = None

class FundIn(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    goal: float = 0
    cover_url: Optional[str] = None
    category: Optional[str] = None
    visible: bool = True
    order: Optional[int] = None
    pinned: bool = False

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
    guest_email: Optional[EmailStr] = None

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
    user_doc.pop("_id", None)
    user_doc.pop("password_hash", None)
    return UserPublic(**user_doc)

# Authorization helper
def is_owner_or_collab(reg: dict, user_id: str) -> bool:
    return reg.get("owner_id") == user_id or user_id in (reg.get("collaborators") or [])

# ===== Routes =====
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# --- Auth ---
@api_router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(body: UserCreate, request: Request):
    await rate_limit(request, key="register", limit=10, window_sec=60)
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
async def login(body: LoginBody, request: Request):
    await rate_limit(request, key="login", limit=20, window_sec=60)
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

# --- Registries ---
@api_router.post("/registries", response_model=Registry, status_code=201)
async def create_registry(payload: RegistryCreate, current: UserPublic = Depends(get_user_from_token)):
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
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    update_doc = {k: v for k, v in patch.model_dump().items() if v is not None}
    update_doc["updated_at"] = datetime.utcnow()
    await db.registries.update_one({"id": registry_id}, {"$set": update_doc})
    reg.update(update_doc)
    reg.pop("_id", None)
    return Registry(**reg)

@api_router.get("/registries/{registry_id}", response_model=Registry)
async def get_registry(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    reg.pop("_id", None)
    return Registry(**reg)

@api_router.get("/registries/mine", response_model=List[Registry])
async def list_my_registries(current: UserPublic = Depends(get_user_from_token)):
    cursor = db.registries.find({"$or": [{"owner_id": current.id}, {"collaborators": {"$in": [current.id]}}]}).sort("updated_at", -1)
    items = await cursor.to_list(100)
    for it in items:
        it.pop("_id", None)
    return [Registry(**it) for it in items]

@api_router.get("/registries/{slug}/public", response_model=PublicRegistryResponse)
async def get_registry_public(slug: str):
    reg_doc = await db.registries.find_one({"slug": slug})
    if not reg_doc:
        raise HTTPException(status_code=404, detail="Registry not found")

    funds = await db.funds.find({"registry_id": reg_doc["id"], "visible": True}).sort("order", 1).to_list(1000)

    response_funds: List[Dict[str, Any]] = []
    total_raised = 0.0
    for f in funds:
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
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")

    funds_in = body.get("funds", [])
    created = 0
    updated = 0
    for idx, f in enumerate(funds_in):
        data = f.model_dump()
        now = datetime.utcnow()
        if data.get("order") is None:
            data["order"] = idx
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
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    items = await db.funds.find({"registry_id": registry_id}).sort("order", 1).to_list(1000)
    return [Fund(**{k: v for k, v in it.items() if k != "_id"}) for it in items]

# --- Contributions ---
@api_router.post("/contributions", response_model=Contribution, status_code=201)
async def create_contribution(payload: ContributionIn):
    fund = await db.funds.find_one({"id": payload.fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    contrib = Contribution(**payload.model_dump())
    await db.contributions.insert_one(contrib.model_dump())
    return contrib

@api_router.get("/funds/{fund_id}/contributions", response_model=List[Contribution])
async def list_contributions(fund_id: str, current: Optional[UserPublic] = Depends(get_user_from_token)):
    fund = await db.funds.find_one({"id": fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    reg = await db.registries.find_one({"id": fund.get("registry_id")})
    if not reg or not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    items = await db.contributions.find({"fund_id": fund_id}).to_list(1000)
    return [Contribution(**it) for it in items]

# --- Analytics & Export ---
@api_router.get("/registries/{registry_id}/contributions", response_model=List[Contribution])
async def list_registry_contributions(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    fund_ids = [f["id"] for f in await db.funds.find({"registry_id": registry_id}).to_list(1000)]
    items = await db.contributions.find({"fund_id": {"$in": fund_ids}}).to_list(5000)
    return [Contribution(**it) for it in items]

@api_router.get("/registries/{registry_id}/contributions/export/csv")
async def export_registry_contributions_csv(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")

    fund_map: Dict[str, str] = {}
    for f in await db.funds.find({"registry_id": registry_id}).to_list(1000):
        fund_map[f['id']] = f.get('title', '')

    items = await db.contributions.find({"fund_id": {"$in": list(fund_map.keys())}}).sort("created_at", -1).to_list(10000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["created_at", "fund_title", "amount", "name", "message", "method", "public"])
    for it in items:
        created_at = it.get('created_at')
        if isinstance(created_at, datetime):
            created_at = created_at.replace(tzinfo=timezone.utc).isoformat()
        writer.writerow([
            created_at,
            fund_map.get(it.get('fund_id'), ''),
            it.get('amount'),
            it.get('name', ''),
            it.get('message', ''),
            it.get('method', ''),
            it.get('public', True)
        ])
    output.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=contributions_{registry_id}.csv"}
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)

@api_router.get("/registries/{registry_id}/analytics")
async def registry_analytics(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")

    funds = await db.funds.find({"registry_id": registry_id}).to_list(1000)
    fund_ids = [f['id'] for f in funds]
    fund_titles = {f['id']: f.get('title', '') for f in funds}

    pipeline = [
        {"$match": {"fund_id": {"$in": fund_ids}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    ]
    summary = await db.contributions.aggregate(pipeline).to_list(1)
    total = float(summary[0]['total']) if summary else 0.0
    count = int(summary[0]['count']) if summary else 0
    avg = (total / count) if count else 0.0

    by_fund_pipeline = [
        {"$match": {"fund_id": {"$in": fund_ids}}},
        {"$group": {"_id": "$fund_id", "sum": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        {"$sort": {"sum": -1}}
    ]
    by_fund_raw = await db.contributions.aggregate(by_fund_pipeline).to_list(100)
    by_fund = [
        {"fund_id": x['_id'], "title": fund_titles.get(x['_id'], ''), "sum": float(x['sum']), "count": int(x['count'])}
        for x in by_fund_raw
    ]

    since = datetime.utcnow() - timedelta(days=30)
    daily_pipeline = [
        {"$match": {"fund_id": {"$in": fund_ids}, "created_at": {"$gte": since}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "sum": {"$sum": "$amount"}}},
        {"$sort": {"_id": 1}}
    ]
    daily_raw = await db.contributions.aggregate(daily_pipeline).to_list(1000)
    daily = [{"date": x['_id'], "sum": float(x['sum'])} for x in daily_raw]

    by_method_pipeline = [
        {"$match": {"fund_id": {"$in": fund_ids}}},
        {"$group": {"_id": "$method", "sum": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        {"$sort": {"sum": -1}}
    ]
    by_method_raw = await db.contributions.aggregate(by_method_pipeline).to_list(50)
    by_method = [
        {"method": x.get('_id') or 'unknown', "sum": float(x['sum']), "count": int(x['count'])}
        for x in by_method_raw
    ]

    recent = await db.contributions.find({"fund_id": {"$in": fund_ids}}).sort("created_at", -1).to_list(5)
    recent = [
        {"name": r.get('name', 'Guest'), "amount": float(r.get('amount', 0)), "message": r.get('message'), "created_at": r.get('created_at')} for r in recent
    ]

    return {"total": total, "count": count, "average": avg, "by_fund": by_fund, "daily": daily, "by_method": by_method, "recent": recent}

# --- Collaborators ---
class CollaboratorAdd(BaseModel):
    email: EmailStr

@api_router.post("/registries/{registry_id}/collaborators")
async def add_collaborator(registry_id: str, body: CollaboratorAdd, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Only owner can add collaborators")
    user = await find_user_by_email(body.email.lower())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user['id'] == reg['owner_id']:
        raise HTTPException(status_code=400, detail="Owner already has access")
    collabs = set(reg.get('collaborators') or [])
    collabs.add(user['id'])
    await db.registries.update_one({"id": registry_id}, {"$set": {"collaborators": list(collabs), "updated_at": datetime.utcnow()}})
    return {"ok": True}

@api_router.delete("/registries/{registry_id}/collaborators/{user_id}")
async def remove_collaborator(registry_id: str, user_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Only owner can remove collaborators")
    collabs = set(reg.get('collaborators') or [])
    if user_id in collabs:
        collabs.remove(user_id)
        await db.registries.update_one({"id": registry_id}, {"$set": {"collaborators": list(collabs), "updated_at": datetime.utcnow()}})
    return {"ok": True}

# --- Chunked Uploads ---
class UploadInitBody(BaseModel):
    filename: str
    size: int
    mime: Optional[str] = None
    registry_id: str

class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int

@api_router.post("/uploads/initiate", response_model=UploadInitResponse)
async def initiate_upload(body: UploadInitBody, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": body.registry_id})
    if not reg or not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    if body.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    if body.mime and not body.mime.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
    upload_id = str(uuid.uuid4())
    tmp_dir = UPLOAD_TMP / upload_id
    tmp_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "upload_id": upload_id,
        "filename": body.filename,
        "size": body.size,
        "mime": body.mime,
        "registry_id": body.registry_id,
        "created_at": datetime.utcnow(),
        "completed": False,
    }
    await db.uploads.insert_one(meta)
    return UploadInitResponse(upload_id=upload_id, chunk_size=CHUNK_SIZE)

@api_router.post("/uploads/chunk")
async def upload_chunk(upload_id: str = Form(...), index: int = Form(...), chunk: UploadFile = File(...), current: UserPublic = Depends(get_user_from_token)):
    meta = await db.uploads.find_one({"upload_id": upload_id})
    if not meta:
        raise HTTPException(status_code=404, detail="Upload not found")
    reg = await db.registries.find_one({"id": meta.get('registry_id')})
    if not reg or not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    data = await chunk.read()
    if len(data) > CHUNK_SIZE + 1024:
        raise HTTPException(status_code=400, detail="Chunk too large")
    tmp_dir = UPLOAD_TMP / upload_id
    tmp_dir.mkdir(parents=True, exist_ok=True)
    part_path = tmp_dir / f"{index}.part"
    with open(part_path, "wb") as f:
        f.write(data)
    return {"ok": True}

class UploadCompleteBody(BaseModel):
    upload_id: str

class UploadCompleteResponse(BaseModel):
    url: str

@api_router.post("/uploads/complete", response_model=UploadCompleteResponse)
async def complete_upload(body: UploadCompleteBody, current: UserPublic = Depends(get_user_from_token)):
    meta = await db.uploads.find_one({"upload_id": body.upload_id})
    if not meta:
        raise HTTPException(status_code=404, detail="Upload not found")
    reg = await db.registries.find_one({"id": meta.get('registry_id')})
    if not reg or not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Not allowed")

    tmp_dir = UPLOAD_TMP / body.upload_id
    parts = sorted([p for p in tmp_dir.glob("*.part")], key=lambda p: int(p.stem))
    if not parts:
        raise HTTPException(status_code=400, detail="No parts uploaded")

    safe_name = f"{uuid.uuid4()}_{meta['filename'].replace('/', '_')}"
    final_dir = UPLOAD_DIR / "registry" / meta['registry_id']
    final_dir.mkdir(parents=True, exist_ok=True)
    final_path = final_dir / safe_name

    with open(final_path, "wb") as out:
        for part in parts:
            with open(part, "rb") as pf:
                out.write(pf.read())

    # cleanup tmp
    for part in parts:
        try:
            part.unlink()
        except Exception:
            pass
    try:
        tmp_dir.rmdir()
    except Exception:
        pass

    await db.uploads.update_one({"upload_id": body.upload_id}, {"$set": {"completed": True, "final_path": str(final_path)}})
    url_path = f"/api/files/registry/{meta['registry_id']}/{safe_name}"
    return UploadCompleteResponse(url=url_path)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def on_startup():
    await ensure_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()