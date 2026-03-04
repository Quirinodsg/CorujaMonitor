# Ollama Instalado no Docker - Configuração Completa

## ✅ Status da Instalação

O Ollama foi migrado com sucesso de instalação local para Docker e está totalmente funcional!

## 📦 Configuração Docker

### Container Ollama
```yaml
ollama:
  image: ollama/ollama:latest
  container_name: coruja-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
  environment:
    - OLLAMA_HOST=0.0.0.0
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
```

## 🤖 Modelo Instalado

**Modelo:** llama2  
**Tamanho:** 3.8 GB  
**Status:** ✅ Baixado e pronto para uso

### Verificar modelos instalados:
```bash
docker exec coruja-ollama ollama list
```

## ⚙️ Configuração da Aplicação

### Arquivo .env
```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
AI_MODEL=llama2
```

### Arquivo ai-agent/config.py
```python
AI_PROVIDER: str = "ollama"
OLLAMA_BASE_URL: str = "http://ollama:11434"
AI_MODEL: str = "llama2"
```

## 🔄 Comandos Úteis

### Gerenciar Modelos
```bash
# Listar modelos instalados
docker exec coruja-ollama ollama list

# Baixar novo modelo
docker exec coruja-ollama ollama pull <modelo>

# Remover modelo
docker exec coruja-ollama ollama rm <modelo>

# Testar modelo
docker exec coruja-ollama ollama run llama2 "Olá, como você está?"
```

### Verificar Status
```bash
# Ver logs do Ollama
docker logs coruja-ollama

# Verificar se está rodando
docker ps | grep ollama

# Testar API
curl http://localhost:11434/api/tags
```

## 🚀 Reiniciar Serviços

Após a configuração, reinicie os serviços:

```bash
# Reiniciar apenas o AI Agent
docker-compose restart ai-agent

# Ou reiniciar tudo
docker-compose restart
```

## 📊 Modelos Disponíveis

Você pode instalar outros modelos conforme necessário:

```bash
# Modelos menores (mais rápidos)
docker exec coruja-ollama ollama pull llama2:7b
docker exec coruja-ollama ollama pull mistral

# Modelos maiores (mais precisos)
docker exec coruja-ollama ollama pull llama2:13b
docker exec coruja-ollama ollama pull llama2:70b

# Modelos especializados
docker exec coruja-ollama ollama pull codellama
docker exec coruja-ollama ollama pull neural-chat
```

## 🔍 Troubleshooting

### Ollama não inicia
```bash
# Verificar logs
docker logs coruja-ollama

# Reiniciar container
docker restart coruja-ollama
```

### Modelo não encontrado
```bash
# Verificar modelos instalados
docker exec coruja-ollama ollama list

# Baixar modelo novamente
docker exec coruja-ollama ollama pull llama2
```

### Erro de conexão
- Verifique se o container está rodando: `docker ps | grep ollama`
- Verifique a URL no .env: deve ser `http://ollama:11434` (não localhost)
- Reinicie o ai-agent: `docker-compose restart ai-agent`

## 📝 Notas Importantes

1. **Rede Docker**: O Ollama usa a rede interna do Docker, por isso a URL é `http://ollama:11434`
2. **Persistência**: Os modelos são salvos no volume `ollama_data` e não serão perdidos ao reiniciar
3. **Performance**: O llama2 padrão tem bom equilíbrio entre velocidade e qualidade
4. **Memória**: Certifique-se de ter pelo menos 8GB de RAM disponível para o Docker

## ✨ Próximos Passos

1. Reinicie o ai-agent para aplicar as configurações
2. Teste a funcionalidade de IA no frontend
3. Monitore os logs para verificar se está funcionando corretamente

---

**Data da Instalação:** 25 de Fevereiro de 2026  
**Versão do Ollama:** latest  
**Modelo Principal:** llama2 (3.8 GB)
