# ⚡ EXECUTE ISTO AGORA

## Problema Detectado

Falta instalar `pydantic-settings` e outras dependências.

## Solução em 1 Comando

Execute no PowerShell:

```powershell
.\instalar_agora.ps1
```

**OU** se preferir fazer manualmente:

```powershell
cd api
python -m pip install -r requirements.txt
python migrate_standalone_sensors.py
cd ..
```

## Depois

Reinicie os serviços:

```powershell
# API (em um terminal)
cd api
uvicorn main:app --reload

# Frontend (em outro terminal)
cd frontend
npm start
```

## Testar

1. Acesse: http://localhost:3000
2. Login: admin@coruja.com / admin123
3. Clique em "📚 Biblioteca de Sensores"
4. Adicione seu primeiro sensor!

---

**Pronto!** 🚀
