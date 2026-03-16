#!/usr/bin/env python3
"""
Script para corrigir o arquivo api/models.py
Remove a classe Credential duplicada que está DENTRO de AuthenticationConfig
"""

# Ler o arquivo
with open('api/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar as linhas problemáticas
fixed_lines = []
skip_until_line = None
inside_nested_credential = False

for i, line in enumerate(lines, 1):
    # Se estamos pulando linhas, verificar se chegamos no fim
    if skip_until_line and i <= skip_until_line:
        continue
    
    # Detectar início da classe Credential ANINHADA (com indentação de 4 espaços)
    if '    class Credential(Base):' in line and not inside_nested_credential:
        print(f"⚠️ Linha {i}: Detectada classe Credential ANINHADA (dentro de AuthenticationConfig)")
        inside_nested_credential = True
        
        # Procurar o fim desta classe aninhada (próxima linha sem indentação ou com class)
        for j in range(i, len(lines) + 1):
            next_line = lines[j-1] if j <= len(lines) else ''
            
            # Se encontrar outra declaração de classe no nível raiz, parar
            if next_line.strip().startswith('class ') and not next_line.startswith('    '):
                skip_until_line = j - 1
                print(f"✅ Removendo linhas {i} até {skip_until_line} (classe Credential aninhada)")
                break
        continue
    
    # Adicionar linha normal
    fixed_lines.append(line)

# Salvar arquivo corrigido
with open('api/models.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"\n✅ Arquivo api/models.py corrigido!")
print(f"📊 Total de linhas: {len(lines)} → {len(fixed_lines)}")
print(f"🗑️ Linhas removidas: {len(lines) - len(fixed_lines)}")
