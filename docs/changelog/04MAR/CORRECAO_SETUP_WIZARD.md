# Correção do Setup Wizard - Requirements.txt

## Problema Identificado

Ao executar `setup_wizard.bat`, o erro ocorria:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## Causa Raiz

O script `setup_wizard.bat` estava sendo executado sem garantir que o diretório de trabalho atual fosse a pasta `probe/`. Quando o usuário executava o script de outro diretório, o comando `pip install -r requirements.txt` não encontrava o arquivo.

## Solução Aplicada

Adicionado comando para mudar para o diretório do script antes de executar qualquer operação:

```batch
REM Mudar para o diretorio do script
cd /d "%~dp0"
echo [OK] Diretorio: %CD%
echo.
```

### Explicação do Comando

- `%~dp0` - Retorna o caminho completo do diretório onde o script .bat está localizado
- `cd /d` - Muda de diretório, incluindo mudança de drive (C:, D:, etc.)

## Arquivo Modificado

- `probe/setup_wizard.bat` - Linha 24 (após verificação de administrador)

## Como Testar

1. Navegue até a pasta `probe/`
2. Execute como Administrador: `setup_wizard.bat`
3. O script agora deve:
   - Confirmar o diretório correto
   - Encontrar o `requirements.txt`
   - Instalar as dependências com sucesso

## Dependências da Probe

O arquivo `probe/requirements.txt` contém:
```
psutil==5.9.8
httpx==0.26.0
pywin32>=307
```

Estas são as bibliotecas necessárias para:
- `psutil` - Coleta de métricas do sistema (CPU, memória, disco, rede)
- `httpx` - Cliente HTTP para comunicação com a API
- `pywin32` - Integração com Windows (serviços, WMI)

## Status

✅ Correção aplicada
✅ Script atualizado
✅ Pronto para instalação

## Próximos Passos

Execute novamente o `setup_wizard.bat` como Administrador para instalar a probe.
