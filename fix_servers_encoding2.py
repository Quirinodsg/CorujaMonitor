#!/usr/bin/env python3
"""
Corrige emojis corrompidos no Servers.js via re-encoding.
O arquivo foi salvo como CP1252 e relido como UTF-8, gerando mojibake.
Para reverter: encode cada char corrompido como latin-1, decode como utf-8.
"""
import re

def try_fix_mojibake(text):
    """Tenta corrigir sequências mojibake no texto."""
    result = []
    i = 0
    fixed = 0
    while i < len(text):
        # Tenta pegar uma janela de chars e reverter o mojibake
        # Mojibake: chars latin-1 que foram interpretados como UTF-8
        # Para reverter: encode como latin-1, decode como utf-8
        found = False
        for window in [8, 7, 6, 5, 4, 3, 2]:
            if i + window > len(text):
                continue
            chunk = text[i:i+window]
            try:
                # Tenta encodar como latin-1 e decodar como utf-8
                recovered = chunk.encode('latin-1').decode('utf-8')
                # Só aceita se o resultado for um emoji ou char especial válido
                if len(recovered) <= len(chunk) // 2 + 1 and any(ord(c) > 127 for c in recovered):
                    result.append(recovered)
                    fixed += 1
                    i += window
                    found = True
                    break
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        if not found:
            result.append(text[i])
            i += 1
    return ''.join(result), fixed

with open('frontend/src/components/Servers.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original size: {len(content)} chars")

fixed_content, count = try_fix_mojibake(content)

print(f"Fixed size: {len(fixed_content)} chars")
print(f"Replacements: {count}")

# Verify no more corrupted sequences
remaining = sum(1 for c in fixed_content if '\u2500' <= c <= '\u257F')
print(f"Remaining box-drawing chars: {remaining}")

with open('frontend/src/components/Servers.js', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Done!")
