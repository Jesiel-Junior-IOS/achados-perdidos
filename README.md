# Sistema Achados e Perdidos - Instituto da Oportunidade Social
# Backend API com FastAPI

## Funcionalidades
- ✅ API completa para gerenciamento de itens
- ✅ Sistema de comentários
- ✅ Sistema de reclamações (claims)  
- ✅ Autenticação de admin
- ✅ Logs estruturados
- ✅ Health check para monitoramento

## Endpoints principais
- `GET /api/items` - Listar itens disponíveis
- `POST /api/items` - Criar novo item (admin)
- `POST /api/items/{id}/claim` - Reclamar item
- `POST /api/auth/login` - Login admin
- `GET /health` - Health check

## Deploy no Render
1. Conectar este repositório
2. Configurar variáveis de ambiente:
   - `PORT=10000`
   - `ADMIN_PASSWORD=973439010`

## Desenvolvimento local
```bash
pip install -r requirements.txt
python main.py
```

Acesse: http://localhost:10000