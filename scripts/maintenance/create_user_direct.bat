@echo off
echo ========================================
echo Criando Usuario Administrador
echo ========================================
echo.

echo Verificando containers...
docker ps | findstr coruja-api
if %errorLevel% neq 0 (
    echo ERRO: Container coruja-api nao esta rodando!
    echo Execute: docker compose up -d
    pause
    exit /b 1
)

echo.
echo Criando usuario no banco de dados...
docker exec -it coruja-api python -c "from database import SessionLocal; from models import User, Tenant; from auth import get_password_hash; db = SessionLocal(); tenant = db.query(Tenant).filter(Tenant.slug == 'default').first(); if not tenant: tenant = Tenant(name='Default', slug='default'); db.add(tenant); db.flush(); existing = db.query(User).filter(User.email == 'admin@coruja.com').first(); if existing: print('Usuario ja existe!'); db.close(); exit(); user = User(email='admin@coruja.com', hashed_password=get_password_hash('admin123'), full_name='Administrator', tenant_id=tenant.id, role='admin', language='pt-BR'); db.add(user); db.commit(); print('Usuario criado com sucesso!'); print('Email: admin@coruja.com'); print('Senha: admin123'); db.close()"

echo.
echo ========================================
echo Pronto!
echo ========================================
echo.
echo Credenciais:
echo Email: admin@coruja.com
echo Senha: admin123
echo.
echo Acesse: http://localhost:3000
echo.
pause
