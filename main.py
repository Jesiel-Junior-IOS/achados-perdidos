from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import uuid
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema Achados e Perdidos - Instituto da Oportunidade Social", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class Item(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    image: str
    found_at: str
    location: str
    created_at: Optional[str] = None

class Comment(BaseModel):
    id: Optional[str] = None
    item_id: int
    author: str
    text: str
    created_at: Optional[str] = None

class Claim(BaseModel):
    id: Optional[str] = None
    item_id: int
    claimer_name: str
    claim_date: Optional[str] = None

class LoginRequest(BaseModel):
    password: str

# Dados em memória (para Render free tier)
DEFAULT_DATA = {
    "items": [
        {
            "id": 1,
            "title": "Carteira de couro marrom",
            "description": "Carteira encontrada no pátio da escola. Contém documentos.",
            "image": "images/carteira-marrom-001.jpg",
            "found_at": "2024-10-20",
            "location": "Pátio principal",
            "created_at": "2024-10-20T10:30:00"
        },
        {
            "id": 2,
            "title": "Óculos de sol Ray-Ban",
            "description": "Óculos escuros encontrados na quadra esportiva.",
            "image": "images/oculos-rayban-002.jpg",
            "found_at": "2024-10-21",
            "location": "Quadra de esportes",
            "created_at": "2024-10-21T14:15:00"
        },
        {
            "id": 3,
            "title": "Chaveiro do Batman",
            "description": "Chaveiro com 3 chaves encontrado no corredor.",
            "image": "images/chaves-batman-003.jpg",
            "found_at": "2024-10-22",
            "location": "Corredor do 2º andar",
            "created_at": "2024-10-22T09:45:00"
        }
    ],
    "comments": {},
    "claimed_items": [],
    "claimed_data": {},
    "next_id": 4
}

# Variável global para armazenar dados
_data_store = DEFAULT_DATA.copy()

def get_data():
    """Retorna dados atuais"""
    return _data_store

def save_data(data):
    """Salva dados na memória"""
    global _data_store
    _data_store = data
    logger.info("Dados atualizados no sistema")
    return True

# ========== ENDPOINTS ==========

@app.get("/")
async def root():
    logger.info("Acesso ao endpoint raiz")
    return {
        "message": "Sistema Achados e Perdidos - Instituto da Oportunidade Social",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/api/items", response_model=List[Item])
async def get_items():
    """Buscar todos os items não reclamados"""
    logger.info("Buscando items disponíveis")
    data = get_data()
    available_items = []
    
    for item in data["items"]:
        if item["id"] not in data["claimed_items"]:
            available_items.append(item)
    
    logger.info(f"Retornando {len(available_items)} items disponíveis")
    return available_items

@app.post("/api/items", response_model=Item)
async def create_item(item: Item):
    """Criar novo item"""
    logger.info(f"Criando novo item: {item.title}")
    data = get_data()
    
    # Gerar ID único
    item.id = data["next_id"]
    data["next_id"] += 1
    
    # Adicionar timestamp
    item.created_at = datetime.now().isoformat()
    
    # Adicionar à lista
    data["items"].append(item.model_dump())
    
    save_data(data)
    logger.info(f"Item criado com ID {item.id}")
    return item

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    """Deletar item"""
    logger.info(f"Deletando item ID: {item_id}")
    data = get_data()
    
    # Remover item da lista principal
    data["items"] = [item for item in data["items"] if item["id"] != item_id]
    
    # Remover das listas de reclamados
    if item_id in data["claimed_items"]:
        data["claimed_items"].remove(item_id)
    
    if str(item_id) in data["claimed_data"]:
        del data["claimed_data"][str(item_id)]
    
    # Remover comentários do item
    if str(item_id) in data["comments"]:
        del data["comments"][str(item_id)]
    
    save_data(data)
    logger.info(f"Item {item_id} deletado com sucesso")
    return {"message": "Item deletado com sucesso"}

@app.get("/api/items/{item_id}/comments")
async def get_comments(item_id: int):
    """Buscar comentários de um item"""
    logger.info(f"Buscando comentários do item {item_id}")
    data = get_data()
    return data["comments"].get(str(item_id), [])

@app.post("/api/items/{item_id}/comments")
async def add_comment(item_id: int, comment: Comment):
    """Adicionar comentário a um item"""
    logger.info(f"Adicionando comentário ao item {item_id}")
    data = get_data()
    
    # Verificar se item existe
    item_exists = any(item["id"] == item_id for item in data["items"])
    if not item_exists:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    # Gerar ID único para comentário
    comment.id = str(uuid.uuid4())
    comment.item_id = item_id
    comment.created_at = datetime.now().isoformat()
    
    # Adicionar comentário
    if str(item_id) not in data["comments"]:
        data["comments"][str(item_id)] = []
    
    data["comments"][str(item_id)].append(comment.model_dump())
    
    save_data(data)
    logger.info(f"Comentário adicionado ao item {item_id}")
    return comment

@app.post("/api/items/{item_id}/claim")
async def claim_item(item_id: int, claim: Claim):
    """Reclamar um item"""
    logger.info(f"Reclamando item {item_id}")
    data = get_data()
    
    # Verificar se item existe e não foi reclamado
    item_exists = any(item["id"] == item_id for item in data["items"])
    if not item_exists:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    if item_id in data["claimed_items"]:
        raise HTTPException(status_code=400, detail="Item já foi reclamado")
    
    # Adicionar aos reclamados
    claim.item_id = item_id
    claim.claim_date = datetime.now().isoformat()
    
    data["claimed_items"].append(item_id)
    data["claimed_data"][str(item_id)] = claim.model_dump()
    
    save_data(data)
    logger.info(f"Item {item_id} reclamado por {claim.claimer_name}")
    return {"message": "Item reclamado com sucesso", "claim": claim}

@app.get("/api/claimed-items")
async def get_claimed_items():
    """Buscar items reclamados (admin)"""
    logger.info("Buscando items reclamados")
    data = get_data()
    claimed_items = []
    
    for item in data["items"]:
        if item["id"] in data["claimed_items"]:
            claim_info = data["claimed_data"].get(str(item["id"]), {})
            claimed_items.append({
                **item,
                "claim_info": claim_info
            })
    
    logger.info(f"Retornando {len(claimed_items)} items reclamados")
    return claimed_items

@app.post("/api/items/{item_id}/restore")
async def restore_item(item_id: int):
    """Devolver item ao feed"""
    logger.info(f"Devolvendo item {item_id} ao feed")
    data = get_data()
    
    if item_id in data["claimed_items"]:
        data["claimed_items"].remove(item_id)
    
    if str(item_id) in data["claimed_data"]:
        del data["claimed_data"][str(item_id)]
    
    save_data(data)
    return {"message": "Item devolvido ao feed"}

@app.post("/api/items/{item_id}/deliver")
async def confirm_delivery(item_id: int):
    """Confirmar entrega do item (remove definitivamente)"""
    logger.info(f"Confirmando entrega do item {item_id}")
    data = get_data()
    
    # Remover completamente
    data["items"] = [item for item in data["items"] if item["id"] != item_id]
    
    if item_id in data["claimed_items"]:
        data["claimed_items"].remove(item_id)
    
    if str(item_id) in data["claimed_data"]:
        del data["claimed_data"][str(item_id)]
    
    if str(item_id) in data["comments"]:
        del data["comments"][str(item_id)]
    
    save_data(data)
    logger.info(f"Item {item_id} marcado como entregue")
    return {"message": "Item marcado como entregue"}

@app.post("/api/auth/login")
async def login(login_request: LoginRequest):
    """Verificar senha do admin"""
    logger.info("Tentativa de login admin")
    # Senha personalizada para Instituto da Oportunidade Social
    correct_password = "973439010"
    
    if login_request.password == correct_password:
        logger.info("Login admin realizado com sucesso")
        return {"success": True, "message": "Login realizado com sucesso"}
    else:
        logger.warning("Tentativa de login com senha incorreta")
        raise HTTPException(status_code=401, detail="Senha incorreta")

@app.post("/api/reset")
async def reset_data():
    """Resetar dados para padrão original"""
    logger.info("Resetando dados para padrão original")
    global _data_store
    _data_store = DEFAULT_DATA.copy()
    return {"message": "Dados resetados para padrão original"}

# Health check para Render
@app.get("/health")
async def health_check():
    """Health check para monitoramento do Render"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Iniciando servidor na porta {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)