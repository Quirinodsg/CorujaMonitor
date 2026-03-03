# ⚠️ Problema: psycopg2-binary

## Erro Encontrado

```
ERROR: Failed to build 'psycopg2-binary' when getting requirements to build wheel
Error: pg_config executable not found.
```

## Causa

O `psycopg2-binary` está tentando compilar do código fonte e precisa de:
- PostgreSQL instalado
- Compiladores C++ (Visual Studio Build Tools)

## ✅ Solução Rápida

Você provavelmente JÁ TEM o `psycopg2-binary` instalado (o sistema está funcionando).

Execute este script que pula o psycopg2 e instala apenas o que falta:

```powershell
.\instalar_sem_psycopg2.ps1
```

## OU Manualmente

```powershell
cd api

# Instalar apenas o que falta
python -m pip install pydantic-settings
python -m pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-monitor
python -m pip install pysnmp requests httpx pytz

# Executar migração
python migrate_standalone_sensors.py

cd ..
```

## Verificar se psycopg2 já está instalado

```powershell
python -c "import psycopg2; print('psycopg2 OK:', psycopg2.__version__)"
```

Se aparecer a versão, está tudo certo!

## Depois

Reinicie API e Frontend:

```powershell
# API
cd api
uvicorn main:app --reload

# Frontend (outro terminal)
cd frontend
npm start
```

---

**Execute o script agora!** 🚀
