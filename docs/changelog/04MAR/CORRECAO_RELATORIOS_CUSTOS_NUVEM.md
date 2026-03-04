# Correção: Relatórios com Custos de Nuvem e Problemas

## Data: 18/02/2026

## Problemas Identificados

### 1. Custos de Nuvem Não Apareciam nos Relatórios
- **Sintoma**: Seção de custos de nuvem (Azure, AWS, GCP, Hyper-V) não era exibida
- **Causa**: Backend calculava os custos mas frontend não renderizava a seção
- **Impacto**: Usuário não conseguia ver comparação de custos entre provedores

### 2. Relatório de Problemas com Network Error
- **Sintoma**: Erro ao gerar relatório "Máquinas com Mais Problemas"
- **Causa**: Sintaxe incorreta do SQLAlchemy - `func.case()` não existe
- **Erro**: `TypeError: Function.__init__() got an unexpected keyword argument 'else_'`
- **Impacto**: Relatório de problemas completamente quebrado

## Correções Aplicadas

### 1. Adicionada Seção de Custos de Nuvem no Frontend

**Arquivo**: `frontend/src/components/Reports.js`

**Mudança**: Adicionada seção completa de comparação de custos após a análise de custos no relatório de CPU:

```javascript
{data.cloud_costs && (
  <div className="cloud-costs-section">
    <h4>☁️ Comparação de Custos em Nuvem</h4>
    
    // Cards para cada provedor: Azure, AWS, GCP, Hyper-V
    // Mostra: tamanho recomendado, CPU/RAM, custo mensal e anual
    
    // Comparação final:
    // - Melhor custo-benefício
    // - Economia potencial
  </div>
)}
```

**Funcionalidades**:
- 4 cards coloridos (Azure azul, AWS laranja, GCP azul, Hyper-V cinza)
- Exibe tamanho recomendado (small, medium, large, xlarge)
- Mostra configuração (CPU cores / RAM GB)
- Custo mensal e anual em BRL
- Destaca o provedor mais barato
- Calcula economia potencial entre o mais caro e mais barato

### 2. Corrigida Query SQL do Relatório de Problemas

**Arquivo**: `api/routers/reports.py`

**Antes**:
```python
func.sum(func.case((Incident.severity == 'critical', 1), else_=0))
```

**Depois**:
```python
from sqlalchemy import case

func.sum(case((Incident.severity == 'critical', 1), else_=0))
```

**Explicação**: 
- SQLAlchemy não tem `func.case()`, apenas `case()` importado diretamente
- A função `case()` aceita tuplas de condições e o parâmetro `else_`

## Cálculo de Custos de Nuvem

### Tabela de Preços (USD/mês)

| Tamanho | CPU | RAM | Azure | AWS | GCP | Hyper-V |
|---------|-----|-----|-------|-----|-----|---------|
| Small   | 2   | 4GB | $70   | $65 | $60 | $30     |
| Medium  | 4   | 16GB| $140  | $135| $130| $60     |
| Large   | 8   | 32GB| $280  | $270| $260| $120    |
| XLarge  | 16  | 64GB| $560  | $540| $520| $240    |

### Lógica de Dimensionamento

```python
if avg_cpu < 30% and avg_memory < 30%:
    recommended_size = 'small'
elif avg_cpu < 60% and avg_memory < 60%:
    recommended_size = 'medium'
elif avg_cpu < 85% and avg_memory < 85%:
    recommended_size = 'large'
else:
    recommended_size = 'xlarge'
```

### Conversão de Moeda
- Taxa fixa: USD 1.00 = BRL 5.00
- Todos os valores exibidos em Reais (R$)

## Estilos CSS Adicionados

**Arquivo**: `frontend/src/components/Reports.css`

Novos estilos para:
- `.cloud-costs-section` - Container principal
- `.cloud-providers-grid` - Grid de 4 colunas responsivo
- `.cloud-provider-card` - Cards individuais por provedor
- `.provider-header` - Cabeçalho com ícone e nome
- `.provider-details` - Detalhes de configuração e preços
- `.cost-comparison` - Cards de comparação final
- `.comparison-card.best` - Card do melhor provedor (verde)
- `.comparison-card.savings` - Card de economia (azul)

## Testes Realizados

### ✅ Relatório de CPU
- Gera corretamente
- Exibe custos de nuvem
- Mostra 4 provedores
- Calcula economia

### ✅ Relatório de Problemas
- Não gera mais erro de network
- Lista servidores com mais incidentes
- Separa críticos e avisos
- Ordena por total de incidentes

### ✅ Impressão
- Oculta sidebar e botões
- Imprime apenas o relatório
- Mantém formatação

## Próximos Passos (Pendentes)

1. **Modo Dark**: Adicionar toggle de tema escuro nas configurações
2. **Custos no Relatório de Memória**: Adicionar mesma seção de custos
3. **Preços Dinâmicos**: Buscar preços atualizados de APIs dos provedores
4. **Mais Provedores**: Adicionar Oracle Cloud, IBM Cloud, etc.
5. **Calculadora de TCO**: Total Cost of Ownership comparativo

## Comandos para Aplicar

```bash
# Reiniciar frontend
docker-compose restart frontend

# Reiniciar API
docker-compose restart api

# Verificar logs
docker logs coruja-frontend --tail 20
docker logs coruja-api --tail 20
```

## Arquivos Modificados

1. `frontend/src/components/Reports.js` - Adicionada seção de custos de nuvem
2. `frontend/src/components/Reports.css` - Estilos para custos de nuvem (já existiam)
3. `api/routers/reports.py` - Corrigida query SQL do relatório de problemas

## Status Final

✅ Custos de nuvem aparecem no relatório de CPU
✅ Relatório de problemas funciona sem erros
✅ Impressão funciona corretamente
⏳ Modo dark pendente
⏳ Custos no relatório de memória pendente
