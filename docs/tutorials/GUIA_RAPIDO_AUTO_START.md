# Guia Rápido: Probe com Auto-Start

## 🚀 Instalação em 3 Passos

### 1. Pegar Token
```
http://192.168.0.9:3000
→ Empresas
→ + Nova Probe
→ Copiar token
```

### 2. Instalar
```batch
# Botão direito → Executar como administrador
probe/install_completo_com_servico.bat
```

**Configurar**:
- IP: `192.168.0.9`
- Token: `[colar]`
- Senha: `[sua senha do Windows]`

### 3. Verificar
```batch
probe/verificar_instalacao.bat
```

**Aguardar 2-3 minutos e acessar**:
```
http://192.168.0.9:3000 → Servidores
```

---

## 🎮 Comandos Rápidos

### Ver Status
```batch
tasklist | findstr python
schtasks /query /tn "CorujaProbe"
type probe.log
```

### Controlar
```batch
# Parar
taskkill /F /IM python.exe

# Iniciar
start_probe.bat

# Desabilitar auto-start
schtasks /delete /tn "CorujaProbe" /f
```

---

## ✅ Vantagens

- ✅ Inicia automaticamente
- ✅ Não precisa deixar janela aberta
- ✅ Reinicia com Windows
- ✅ Roda em segundo plano

---

## 🐛 Problemas?

### Probe não inicia?
```batch
python --version
pip install -r requirements.txt
python probe_core.py
```

### Sensores não aparecem?
1. Aguarde 2-3 minutos
2. Verifique: `type probe.log`
3. Recarregue: Ctrl+Shift+R

---

## 📖 Documentação Completa

- `COMO_INSTALAR_NOVA_PROBE.md` - Guia completo
- `PROBE_AUTO_START_IMPLEMENTADO.md` - Detalhes técnicos
- `RESUMO_CORRECOES_24FEV_PARTE2.md` - Resumo da implementação

---

**Use `install_completo_com_servico.bat` para instalação profissional!** 🚀
