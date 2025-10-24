from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class CommentModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClaimModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    location: str
    image: str  # base64
    date: str
    claimed: bool = False
    resolved: bool = False
    comments: List[CommentModel] = []
    claims: List[ClaimModel] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemCreate(BaseModel):
    title: str
    description: str
    location: str
    image: str
    date: str

class CommentCreate(BaseModel):
    name: str
    text: str

class ClaimCreate(BaseModel):
    name: str
    contact: str

class AdminLogin(BaseModel):
    password: str

class AdminResponse(BaseModel):
    token: str

# Admin password (hash armazenado no banco)
ADMIN_PASSWORD = "admin123"  # Senha padrão

@api_router.post("/admin/login", response_model=AdminResponse)
async def admin_login(login: AdminLogin):
    if login.password == ADMIN_PASSWORD:
        token = str(uuid.uuid4())
        return {"token": token}
    raise HTTPException(status_code=401, detail="Senha incorreta")

@api_router.get("/feed", response_model=List[ItemModel])
async def get_feed():
    items = await db.items.find({}, {"_id": 0}).to_list(1000)
    for item in items:
        if isinstance(item.get('timestamp'), str):
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
        for comment in item.get('comments', []):
            if isinstance(comment.get('timestamp'), str):
                comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
        for claim in item.get('claims', []):
            if isinstance(claim.get('timestamp'), str):
                claim['timestamp'] = datetime.fromisoformat(claim['timestamp'])
    items.sort(key=lambda x: x['timestamp'], reverse=True)
    return items

@api_router.get("/items/{item_id}", response_model=ItemModel)
async def get_item(item_id: str):
    item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if isinstance(item.get('timestamp'), str):
        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    for comment in item.get('comments', []):
        if isinstance(comment.get('timestamp'), str):
            comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
    for claim in item.get('claims', []):
        if isinstance(claim.get('timestamp'), str):
            claim['timestamp'] = datetime.fromisoformat(claim['timestamp'])
    return item

@api_router.post("/items", response_model=ItemModel)
async def create_item(item: ItemCreate):
    item_obj = ItemModel(**item.model_dump())
    doc = item_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.items.insert_one(doc)
    return item_obj

@api_router.post("/items/{item_id}/comment", response_model=ItemModel)
async def add_comment(item_id: str, comment: CommentCreate):
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    comment_obj = CommentModel(**comment.model_dump())
    comment_doc = comment_obj.model_dump()
    comment_doc['timestamp'] = comment_doc['timestamp'].isoformat()
    
    await db.items.update_one(
        {"id": item_id},
        {"$push": {"comments": comment_doc}}
    )
    
    updated_item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if isinstance(updated_item.get('timestamp'), str):
        updated_item['timestamp'] = datetime.fromisoformat(updated_item['timestamp'])
    for c in updated_item.get('comments', []):
        if isinstance(c.get('timestamp'), str):
            c['timestamp'] = datetime.fromisoformat(c['timestamp'])
    return updated_item

@api_router.post("/items/{item_id}/claim", response_model=ItemModel)
async def claim_item(item_id: str, claim: ClaimCreate):
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    claim_obj = ClaimModel(**claim.model_dump())
    claim_doc = claim_obj.model_dump()
    claim_doc['timestamp'] = claim_doc['timestamp'].isoformat()
    
    await db.items.update_one(
        {"id": item_id},
        {"$push": {"claims": claim_doc}, "$set": {"claimed": True}}
    )
    
    updated_item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if isinstance(updated_item.get('timestamp'), str):
        updated_item['timestamp'] = datetime.fromisoformat(updated_item['timestamp'])
    for c in updated_item.get('comments', []):
        if isinstance(c.get('timestamp'), str):
            c['timestamp'] = datetime.fromisoformat(c['timestamp'])
    for cl in updated_item.get('claims', []):
        if isinstance(cl.get('timestamp'), str):
            cl['timestamp'] = datetime.fromisoformat(cl['timestamp'])
    return updated_item

@api_router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db.items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return {"message": "Item deletado"}

@api_router.put("/items/{item_id}/resolve")
async def resolve_item(item_id: str):
    result = await db.items.update_one(
        {"id": item_id},
        {"$set": {"resolved": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return {"message": "Item resolvido"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()