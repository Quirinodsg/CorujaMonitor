@echo off
echo ========================================
echo   Iniciando Ollama no Docker
echo ========================================
echo.

echo [1/3] Iniciando container Ollama...
docker-compose up -d ollama

echo.
echo [2/3] Aguardando Ollama iniciar (30 segundos)...
timeout /t 30 /nobreak

echo.
echo [3/3] Baixando modelo llama2...
docker exec coruja-ollama ollama pull llama2

echo.
echo ========================================
echo   Ollama iniciado com sucesso!
echo ========================================
echo.
echo Status do Ollama:
docker exec coruja-ollama ollama list

echo.
echo Testando conexao:
curl http://localhost:11434/api/tags

echo.
echo Pressione qualquer tecla para sair...
pause > nul
