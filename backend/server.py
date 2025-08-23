from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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
import resend

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

# Admin emails allowlist (comma-separated)
DEFAULT_ADMIN_EMAILS = {"kshadid@gmail.com"}
ADMIN_EMAILS = set([e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]) or DEFAULT_ADMIN_EMAILS

# Email configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@yourdomain.com')

# Configure Resend if API key is provided
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

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
    await db.audit_logs.create_index([('registry_id', 1), ('created_at', -1)])

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

# ===== Models =====
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    password_hash: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

Slug = constr(pattern=r"^[a-z0-9-]+$", min_length=3, max_length=64)
Currency = constr(pattern=r"^[A-Z]{3}$")

class RegistryCreate(BaseModel):
    couple_names: str
    event_date: Optional[str] = None
    location: Optional[str] = None
    currency: Currency = "AED"
    hero_image: Optional[str] = None
    slug: Slug
    theme: Optional[str] = "modern"

class Registry(RegistryCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    collaborators: List[str] = Field(default_factory=list)
    locked: bool = False
    lock_reason: Optional[str] = None
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
    funds: List[Dict[str, Any]]
    totals: Dict[str, float]

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registry_id: str
    user_id: Optional[str] = None
    action: str
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def log_audit(registry_id: str, user_id: Optional[str], action: str, meta: Dict[str, Any]):
    try:
        entry = AuditLog(registry_id=registry_id, user_id=user_id, action=action, meta=meta)
        await db.audit_logs.insert_one(entry.model_dump())
    except Exception:
        logging.exception("Failed to write audit log")

# ===== Email Service =====
async def send_contribution_receipt(
    guest_email: str,
    guest_name: str,
    amount: float,
    currency: str,
    registry_couple_names: str,
    fund_title: str
):
    """Send a receipt email to the guest who made a contribution"""
    if not RESEND_API_KEY:
        logging.warning("Resend API key not configured, skipping email sending")
        return
    
    try:
        subject = f"Thank you for your contribution to {registry_couple_names}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Contribution Receipt</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank you for your contribution!</h1>
                    <p>Dear {guest_name},</p>
                    <p>Thank you for your generous contribution to {registry_couple_names}'s special day.</p>
                </div>
                
                <div class="details">
                    <h3>Contribution Details:</h3>
                    <p><strong>Amount:</strong> <span class="amount">{currency} {amount:.2f}</span></p>
                    <p><strong>Fund:</strong> {fund_title}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <p>Your thoughtful contribution will help make their dreams come true. They will be so grateful for your generosity!</p>
                
                <div class="footer">
                    <p>This is an automated receipt for your contribution.</p>
                    <p>Thank you for using our wedding registry service.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Thank you for your contribution!
        
        Dear {guest_name},
        
        Thank you for your generous contribution to {registry_couple_names}'s special day.
        
        Contribution Details:
        Amount: {currency} {amount:.2f}
        Fund: {fund_title}
        Date: {datetime.now().strftime('%B %d, %Y')}
        
        Your thoughtful contribution will help make their dreams come true. They will be so grateful for your generosity!
        
        This is an automated receipt for your contribution.
        Thank you for using our wedding registry service.
        """
        
        params = {
            "from": FROM_EMAIL,
            "to": [guest_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        
        email = resend.Emails.send(params)
        logging.info(f"Receipt email sent to {guest_email}, email_id: {email.get('id', 'unknown')}")
        return email
        
    except Exception as e:
        logging.error(f"Failed to send receipt email to {guest_email}: {str(e)}")
        return None

async def send_owner_notification(
    owner_email: str,
    owner_name: str,
    guest_name: str,
    amount: float,
    currency: str,
    fund_title: str,
    message: Optional[str] = None
):
    """Send a notification email to the registry owner about a new contribution"""
    if not RESEND_API_KEY:
        logging.warning("Resend API key not configured, skipping email sending")
        return
    
    try:
        subject = f"New contribution received: {currency} {amount:.2f}"
        
        message_section = ""
        if message:
            message_section = f"""
            <div class="message">
                <h4>Message from {guest_name}:</h4>
                <p style="font-style: italic; background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">"{message}"</p>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Contribution Received</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 New Contribution Received!</h1>
                    <p>Hello {owner_name},</p>
                    <p>Great news! You've received a new contribution for your registry.</p>
                </div>
                
                <div class="details">
                    <h3>Contribution Details:</h3>
                    <p><strong>From:</strong> {guest_name}</p>
                    <p><strong>Amount:</strong> <span class="amount">{currency} {amount:.2f}</span></p>
                    <p><strong>Fund:</strong> {fund_title}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                {message_section}
                
                <p>This contribution brings you one step closer to your special day goals!</p>
                
                <div class="footer">
                    <p>Log in to your registry dashboard to see more details and track your progress.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Contribution Received!
        
        Hello {owner_name},
        
        Great news! You've received a new contribution for your registry.
        
        Contribution Details:
        From: {guest_name}
        Amount: {currency} {amount:.2f}
        Fund: {fund_title}
        Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        {f'Message from {guest_name}: "{message}"' if message else ''}
        
        This contribution brings you one step closer to your special day goals!
        
        Log in to your registry dashboard to see more details and track your progress.
        """
        
        params = {
            "from": FROM_EMAIL,
            "to": [owner_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        
        email = resend.Emails.send(params)
        logging.info(f"Owner notification email sent to {owner_email}, email_id: {email.get('id', 'unknown')}")
        return email
        
    except Exception as e:
        logging.error(f"Failed to send owner notification email to {owner_email}: {str(e)}")
        return None

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

async def is_admin_user(user: UserPublic) -> bool:
    if user.email.lower() in ADMIN_EMAILS:
        return True
    doc = await find_user_by_id(user.id)
    return bool(doc and doc.get('is_admin'))

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
    user = User(name=body.name, email=email, password_hash=hash_password(body.password), is_admin=(email in ADMIN_EMAILS))
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
    # If admin allowlisted email does not exist yet, bootstrap account on first login
    if not user and email in ADMIN_EMAILS:
        user_obj = User(name=email.split('@')[0], email=email, password_hash=hash_password(body.password), is_admin=True)
        await db.users.insert_one(user_obj.model_dump())
        user = user_obj.model_dump()
    if not user or not verify_password(body.password, user.get("password_hash", "")):
        # If it's an allowlisted admin email, reset password on failed login (dev convenience)
        if user and email in ADMIN_EMAILS:
            new_hash = hash_password(body.password)
            await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": new_hash, "is_admin": True}})
            user["password_hash"] = new_hash
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user["id"]) 
    return TokenResponse(access_token=token, user=UserPublic(id=user["id"], name=user.get("name", email), email=user["email"]))

@api_router.get("/auth/me", response_model=UserPublic)
async def me(current: UserPublic = Depends(get_user_from_token)):
    return current

# --- Admin ---
class AdminMe(BaseModel):
    email: EmailStr
    is_admin: bool

@api_router.get("/admin/me", response_model=AdminMe)
async def admin_me(current: UserPublic = Depends(get_user_from_token)):
    return AdminMe(email=current.email, is_admin=await is_admin_user(current))

@api_router.get("/admin/stats")
async def admin_stats(current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    users_count = await db.users.count_documents({})
    regs_count = await db.registries.count_documents({})
    funds_count = await db.funds.count_documents({})
    contribs_count = await db.contributions.count_documents({})
    last_users = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).to_list(10)
    for u in last_users:
        u.pop("_id", None)
    last_regs = await db.registries.find({}).sort("created_at", -1).to_list(10)
    owner_ids = list({r['owner_id'] for r in last_regs if 'owner_id' in r})
    owners = {u['id']: u for u in await db.users.find({"id": {"$in": owner_ids}}).to_list(len(owner_ids))}
    out_regs = []
    for r in last_regs:
        r.pop("_id", None)
        out_regs.append({**r, "owner_email": owners.get(r.get('owner_id',''), {}).get('email')})
    top_funds_raw = await db.contributions.aggregate([
        {"$group": {"_id": "$fund_id", "sum": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        {"$sort": {"sum": -1}},
        {"$limit": 10},
    ]).to_list(10)
    return {
        "counts": {"users": users_count, "registries": regs_count, "funds": funds_count, "contributions": contribs_count},
        "last_users": last_users,
        "last_registries": out_regs,
        "top_funds": top_funds_raw,
    }

@api_router.get("/admin/metrics")
async def admin_metrics(current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    distinct_fund_ids = await db.contributions.distinct('fund_id')
    active_gifts = len(distinct_fund_ids)
    active_event_ids: set[str] = set()
    if distinct_fund_ids:
        funds = await db.funds.find({"id": {"$in": distinct_fund_ids}}).to_list(len(distinct_fund_ids))
        active_event_ids = {f.get('registry_id') for f in funds if f.get('registry_id')}
    active_events = len(active_event_ids)

    agg = await db.contributions.aggregate([
        {"$group": {"_id": None, "avg": {"$avg": "$amount"}, "max": {"$max": "$amount"}}}
    ]).to_list(1)
    avg_amount = float(agg[0]['avg']) if agg else 0.0
    max_amount = float(agg[0]['max']) if agg else 0.0
    return {"active_events": active_events, "active_gifts": active_gifts, "average_amount": avg_amount, "max_amount": max_amount}

@api_router.get("/admin/users")
async def admin_users(query: Optional[str] = None, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    q = {}
    if query:
        q = {"email": {"$regex": query, "$options": "i"}}
    items = await db.users.find(q, {"password_hash": 0}).sort("created_at", -1).to_list(50)
    for it in items:
        it.pop("_id", None)
    return items

@api_router.get("/admin/users/lookup")
async def admin_users_lookup(ids: str, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    arr = [i.strip() for i in ids.split(',') if i.strip()]
    items = await db.users.find({"id": {"$in": arr}}, {"password_hash": 0}).to_list(len(arr))
    for it in items:
        it.pop("_id", None)
    return items

@api_router.get("/admin/users/{user_id}/detail")
async def admin_user_detail(user_id: str, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    usr = await db.users.find_one({"id": user_id}, {"password_hash": 0})
    if not usr:
        raise HTTPException(status_code=404, detail="User not found")
    usr.pop("_id", None)
    owned = await db.registries.find({"owner_id": user_id}).sort("created_at", -1).to_list(100)
    for r in owned:
        r.pop("_id", None)
    collab = await db.registries.find({"collaborators": {"$in": [user_id]}}).sort("created_at", -1).to_list(100)
    for r in collab:
        r.pop("_id", None)
    recent_audit = await db.audit_logs.find({"user_id": user_id}).sort("created_at", -1).to_list(20)
    for a in recent_audit:
        a.pop("_id", None)
    return {"user": usr, "registries_owned": owned, "registries_collab": collab, "recent_audit": recent_audit}

@api_router.get("/admin/registries")
async def admin_registries(query: Optional[str] = None, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    q = {}
    if query:
        q = {"$or": [
            {"slug": {"$regex": query, "$options": "i"}},
            {"couple_names": {"$regex": query, "$options": "i"}},
        ]}
    regs = await db.registries.find(q).sort("created_at", -1).to_list(100)
    owner_ids = list({r['owner_id'] for r in regs if 'owner_id' in r})
    owners = {u['id']: u for u in await db.users.find({"id": {"$in": owner_ids}}).to_list(len(owner_ids))}
    out = []
    for r in regs:
        r.pop("_id", None)
        out.append({**r, "owner_email": owners.get(r.get('owner_id',''), {}).get('email')})
    return out

class LockBody(BaseModel):
    locked: bool
    reason: Optional[str] = None

@api_router.post("/admin/registries/{registry_id}/lock")
async def admin_lock_registry(registry_id: str, body: LockBody, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    await db.registries.update_one({"id": registry_id}, {"$set": {"locked": bool(body.locked), "lock_reason": body.reason or None, "updated_at": datetime.utcnow()}})
    await log_audit(registry_id, current.id, "registry.lock", {"locked": bool(body.locked)})
    return {"ok": True}

@api_router.get("/admin/registries/{registry_id}/funds", response_model=List[Fund])
async def admin_registry_funds(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    items = await db.funds.find({"registry_id": registry_id}).sort("order", 1).to_list(1000)
    return [Fund(**{k: v for k, v in it.items() if k != "_id"}) for it in items]

# --- Status ---
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
async def create_registry(body: RegistryCreate, current: UserPublic = Depends(get_user_from_token)):
    slug_conflict = await db.registries.find_one({"slug": body.slug})
    if slug_conflict:
        raise HTTPException(status_code=409, detail="Slug already taken")
    registry = Registry(**body.model_dump(), owner_id=current.id)
    await db.registries.insert_one(registry.model_dump())
    await log_audit(registry.id, current.id, "registry.create", {"slug": body.slug})
    return registry

@api_router.get("/registries", response_model=List[Registry])
async def my_registries(current: UserPublic = Depends(get_user_from_token)):
    items = await db.registries.find({"$or": [{"owner_id": current.id}, {"collaborators": {"$in": [current.id]}}]}).sort("created_at", -1).to_list(1000)
    return [Registry(**{k: v for k, v in it.items() if k != "_id"}) for it in items]

@api_router.get("/registries/{registry_id}", response_model=Registry)
async def get_registry(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    reg.pop("_id", None)
    return Registry(**reg)

@api_router.put("/registries/{registry_id}", response_model=Registry)
async def update_registry(registry_id: str, body: RegistryUpdate, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if body.slug and body.slug != reg.get("slug"):
        slug_conflict = await db.registries.find_one({"slug": body.slug, "id": {"$ne": registry_id}})
        if slug_conflict:
            raise HTTPException(status_code=409, detail="Slug already taken")
    
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.registries.update_one({"id": registry_id}, {"$set": update_data})
    await log_audit(registry_id, current.id, "registry.update", update_data)
    
    updated_reg = await db.registries.find_one({"id": registry_id})
    updated_reg.pop("_id", None)
    return Registry(**updated_reg)

@api_router.delete("/registries/{registry_id}")
async def delete_registry(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if reg.get("owner_id") != current.id:
        raise HTTPException(status_code=403, detail="Only owners can delete registries")
    
    await db.registries.delete_one({"id": registry_id})
    await db.funds.delete_many({"registry_id": registry_id})
    await db.contributions.delete_many({"fund_id": {"$in": await db.funds.distinct("id", {"registry_id": registry_id})}})
    await log_audit(registry_id, current.id, "registry.delete", {"slug": reg.get("slug")})
    
    return {"ok": True}

# --- Public Registry ---
@api_router.get("/public/registries/{slug}", response_model=PublicRegistryResponse)
async def get_public_registry(slug: str):
    reg = await db.registries.find_one({"slug": slug})
    if not reg or reg.get("locked"):
        raise HTTPException(status_code=404, detail="Registry not found")
    
    reg.pop("_id", None)
    registry = Registry(**reg)
    
    funds = await db.funds.find({"registry_id": registry.id, "visible": True}).sort("order", 1).to_list(1000)
    funds_with_totals = []
    total_raised = 0.0
    total_goal = 0.0
    
    for fund in funds:
        fund.pop("_id", None)
        fund_total = 0.0
        contributions = await db.contributions.find({"fund_id": fund["id"]}).to_list(1000)
        for contrib in contributions:
            fund_total += contrib.get("amount", 0)
        
        total_raised += fund_total
        total_goal += fund.get("goal", 0)
        
        funds_with_totals.append({
            **fund,
            "raised": fund_total,
            "contributions_count": len(contributions)
        })
    
    return PublicRegistryResponse(
        registry=registry,
        funds=funds_with_totals,
        totals={"raised": total_raised, "goal": total_goal}
    )

# --- Funds ---
@api_router.get("/registries/{registry_id}/funds", response_model=List[Fund])
async def get_funds(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    items = await db.funds.find({"registry_id": registry_id}).sort("order", 1).to_list(1000)
    return [Fund(**{k: v for k, v in it.items() if k != "_id"}) for it in items]

@api_router.post("/registries/{registry_id}/funds", response_model=Fund, status_code=201)
async def create_fund(registry_id: str, body: FundIn, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if body.order is None:
        max_order = await db.funds.find({"registry_id": registry_id}).sort("order", -1).limit(1).to_list(1)
        body.order = (max_order[0].get("order", 0) + 1) if max_order else 1
    
    fund = Fund(**body.model_dump(), registry_id=registry_id)
    await db.funds.insert_one(fund.model_dump())
    await log_audit(registry_id, current.id, "fund.create", {"fund_id": fund.id, "title": body.title})
    return fund

@api_router.put("/registries/{registry_id}/funds/{fund_id}", response_model=Fund)
async def update_fund(registry_id: str, fund_id: str, body: FundIn, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    fund = await db.funds.find_one({"id": fund_id, "registry_id": registry_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    update_data = body.model_dump()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.funds.update_one({"id": fund_id}, {"$set": update_data})
    await log_audit(registry_id, current.id, "fund.update", {"fund_id": fund_id, "title": body.title})
    
    updated_fund = await db.funds.find_one({"id": fund_id})
    updated_fund.pop("_id", None)
    return Fund(**updated_fund)

@api_router.delete("/registries/{registry_id}/funds/{fund_id}")
async def delete_fund(registry_id: str, fund_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    fund = await db.funds.find_one({"id": fund_id, "registry_id": registry_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    await db.funds.delete_one({"id": fund_id})
    await db.contributions.delete_many({"fund_id": fund_id})
    await log_audit(registry_id, current.id, "fund.delete", {"fund_id": fund_id, "title": fund.get("title")})
    
    return {"ok": True}

# --- Contributions ---
@api_router.post("/contributions", response_model=Contribution, status_code=201)
async def create_contribution(
    body: ContributionIn, 
    request: Request,
    background_tasks: BackgroundTasks
):
    await rate_limit(request, key="contribution", limit=5, window_sec=60)
    
    fund = await db.funds.find_one({"id": body.fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    registry = await db.registries.find_one({"id": fund["registry_id"]})
    if not registry or registry.get("locked"):
        raise HTTPException(status_code=404, detail="Registry not found or locked")
    
    contribution = Contribution(**body.model_dump())
    await db.contributions.insert_one(contribution.model_dump())
    await log_audit(registry["id"], None, "contribution.create", {
        "fund_id": body.fund_id,
        "amount": body.amount,
        "guest_name": body.name or "Anonymous"
    })
    
    # Send emails in background if configured
    if RESEND_API_KEY:
        guest_name = body.name or "Anonymous"
        
        # Send receipt to guest if email provided
        if body.guest_email:
            background_tasks.add_task(
                send_contribution_receipt,
                guest_email=body.guest_email,
                guest_name=guest_name,
                amount=body.amount,
                currency=registry.get("currency", "AED"),
                registry_couple_names=registry.get("couple_names", ""),
                fund_title=fund.get("title", "")
            )
        
        # Send notification to registry owner
        owner = await db.users.find_one({"id": registry["owner_id"]})
        if owner:
            background_tasks.add_task(
                send_owner_notification,
                owner_email=owner["email"],
                owner_name=owner.get("name", ""),
                guest_name=guest_name,
                amount=body.amount,
                currency=registry.get("currency", "AED"),
                fund_title=fund.get("title", ""),
                message=body.message
            )
    
    return contribution

@api_router.get("/registries/{registry_id}/contributions")
async def get_contributions(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    fund_ids = [f["id"] for f in await db.funds.find({"registry_id": registry_id}).to_list(1000)]
    contributions = await db.contributions.find({"fund_id": {"$in": fund_ids}}).sort("created_at", -1).to_list(1000)
    
    for contrib in contributions:
        contrib.pop("_id", None)
    
    return contributions

@api_router.get("/registries/{registry_id}/analytics")
async def get_analytics(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    fund_ids = [f["id"] for f in await db.funds.find({"registry_id": registry_id}).to_list(1000)]
    
    total_contributions = await db.contributions.count_documents({"fund_id": {"$in": fund_ids}})
    
    agg_result = await db.contributions.aggregate([
        {"$match": {"fund_id": {"$in": fund_ids}}},
        {"$group": {"_id": None, "total_amount": {"$sum": "$amount"}, "avg_amount": {"$avg": "$amount"}}}
    ]).to_list(1)
    
    total_amount = agg_result[0]["total_amount"] if agg_result else 0
    avg_amount = agg_result[0]["avg_amount"] if agg_result else 0
    
    # Daily breakdown for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_stats = await db.contributions.aggregate([
        {"$match": {"fund_id": {"$in": fund_ids}, "created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1},
            "amount": {"$sum": "$amount"}
        }},
        {"$sort": {"_id": 1}}
    ]).to_list(30)
    
    return {
        "total_contributions": total_contributions,
        "total_amount": total_amount,
        "average_amount": avg_amount,
        "daily_stats": daily_stats
    }

@api_router.get("/registries/{registry_id}/export/csv")
async def export_csv(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    if not is_owner_or_collab(reg, current.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    fund_ids = [f["id"] for f in await db.funds.find({"registry_id": registry_id}).to_list(1000)]
    contributions = await db.contributions.find({"fund_id": {"$in": fund_ids}}).sort("created_at", -1).to_list(10000)
    
    # Get fund titles for reference
    funds = {f["id"]: f for f in await db.funds.find({"registry_id": registry_id}).to_list(1000)}
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Name", "Email", "Amount", "Fund", "Message", "Public", "Method"])
    
    for contrib in contributions:
        fund_title = funds.get(contrib["fund_id"], {}).get("title", "Unknown Fund")
        writer.writerow([
            contrib["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            contrib.get("name", ""),
            contrib.get("guest_email", ""),
            contrib["amount"],
            fund_title,
            contrib.get("message", ""),
            "Yes" if contrib.get("public", True) else "No",
            contrib.get("method", "")
        ])
    
    output.seek(0)
    headers = {
        'Content-Disposition': f'attachment; filename="contributions_{registry_id}_{datetime.now().strftime("%Y%m%d")}.csv"'
    }
    
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers=headers
    )

# --- File Upload ---
class ChunkUpload(BaseModel):
    filename: str
    chunk_index: int
    total_chunks: int

@api_router.post("/upload/chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    current: UserPublic = Depends(get_user_from_token)
):
    if file.size and file.size > CHUNK_SIZE:
        raise HTTPException(status_code=413, detail="Chunk size too large")
    
    # Create user-specific temp directory
    user_tmp_dir = UPLOAD_TMP / current.id
    user_tmp_dir.mkdir(exist_ok=True)
    
    chunk_path = user_tmp_dir / f"{filename}.part{chunk_index}"
    
    with open(chunk_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # If this is the last chunk, combine all chunks
    if chunk_index == total_chunks - 1:
        final_filename = f"{uuid.uuid4()}_{filename}"
        final_path = UPLOAD_DIR / final_filename
        
        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_file_path = user_tmp_dir / f"{filename}.part{i}"
                if chunk_file_path.exists():
                    with open(chunk_file_path, "rb") as chunk_file:
                        final_file.write(chunk_file.read())
                    chunk_file_path.unlink()  # Delete chunk file
        
        # Save upload record
        upload_record = {
            "id": str(uuid.uuid4()),
            "user_id": current.id,
            "original_filename": filename,
            "stored_filename": final_filename,
            "size": final_path.stat().st_size,
            "created_at": datetime.utcnow()
        }
        await db.uploads.insert_one(upload_record)
        
        return {"filename": final_filename, "url": f"/api/files/{final_filename}"}
    
    return {"chunk_received": chunk_index}

# --- Admin Registry Detail ---
@api_router.get("/admin/registries/{registry_id}/detail")
async def admin_registry_detail(registry_id: str, current: UserPublic = Depends(get_user_from_token)):
    if not await is_admin_user(current):
        raise HTTPException(status_code=403, detail="Admin only")
    
    reg = await db.registries.find_one({"id": registry_id})
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    
    reg.pop("_id", None)
    
    # Get owner info
    owner = await db.users.find_one({"id": reg["owner_id"]}, {"password_hash": 0})
    if owner:
        owner.pop("_id", None)
    
    # Get funds
    funds = await db.funds.find({"registry_id": registry_id}).sort("order", 1).to_list(1000)
    for f in funds:
        f.pop("_id", None)
    
    # Get contributions with totals
    fund_ids = [f["id"] for f in funds]
    contributions = await db.contributions.find({"fund_id": {"$in": fund_ids}}).sort("created_at", -1).to_list(1000)
    for c in contributions:
        c.pop("_id", None)
    
    total_amount = sum(c.get("amount", 0) for c in contributions)
    
    # Get audit logs
    audit_logs = await db.audit_logs.find({"registry_id": registry_id}).sort("created_at", -1).to_list(50)
    for a in audit_logs:
        a.pop("_id", None)
    
    return {
        "registry": reg,
        "owner": owner,
        "funds": funds,
        "contributions": contributions,
        "total_amount": total_amount,
        "audit_logs": audit_logs
    }

# Include the router in the main app
app.include_router(api_router)

_raw_origins = os.environ.get('CORS_ALLOW_ORIGINS', '*')
allow_origins = ['*'] if _raw_origins.strip() == '*' else [o.strip() for o in _raw_origins.split(',') if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            if request.url.path.startswith('/api/files/') and 200 <= response.status_code < 400:
                response.headers.setdefault('Cache-Control', 'public, max-age=86400, immutable')
        except Exception:
            pass
        return response

app.add_middleware(CacheHeaderMiddleware)

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