#!/usr/bin/env python3
"""
Corrige emojis e texto corrompidos no Servers.js
Mojibake: arquivo salvo como CP1252, relido como UTF-8.
Para reverter: encode como latin-1, decode como utf-8.
"""

# Mapeamento completo: sequência corrompida -> correto
EMOJI_MAP = {
    # Emojis corrompidos
    '≡ƒôü': '📁',
    '≡ƒôí': '📡',
    '≡ƒûÑ∩╕Å': '🖥️',
    '≡ƒÆ╛': '🧠',
    '≡ƒÆ┐': '💾',
    '≡ƒîÉ': '🌐',
    'ΓÜÖ∩╕Å': '⚙️',
    'ΓÅ▒∩╕Å': '⏱️',
    '≡ƒû╝∩╕Å': '🖼️',
    '≡ƒÉ│': '🐳',
    '≡ƒôè': '📊',
    '≡ƒöî': '🔎',
    '≡ƒôª': '📪',
    'Γ£à': '✔',
    'ΓÅ╕∩╕Å': '⏹️',
    'ΓÜá∩╕Å': '⚠️',
    'Γû╝': '▼',
    'Γû╢': '▶',
    'ΓùÅ': '●',
    'Γ₧ò': '🗂️',
    '≡ƒùæ∩╕Å': '🖱️',
    '≡ƒî│': '🌳',
    '≡ƒôï': '📏',
    '≡ƒöì': '🔬',
    '≡ƒöÑ': '🔥',
    '≡ƒô¥': '📥',
    'Γ£ô': '✔',
    'Γ¥î': '✖',
    '≡ƒÄ»': '🎯',
    'ΓÅ│': '⏳',
    'Γ£Å∩╕Å': '✅',
    '≡ƒôé': '📂',
    '≡ƒô£': '📣',
    '≡ƒôÄ': '📄',
    '≡ƒôë': '📋',
    '≡ƒôÆ': '📆',
    '≡ƒôÇ': '📇',
    '≡ƒôÈ': '📈',
    '≡ƒôÊ': '📊',
    '≡ƒôÌ': '📌',
    '≡ƒôÍ': '📍',
    '≡ƒôÎ': '📎',
    '≡ƒôÐ': '📐',
    '≡ƒôÑ': '📑',
    '≡ƒôÒ': '📒',
    '≡ƒôÓ': '📓',
    '≡ƒôÔ': '📔',
    '≡ƒôÕ': '📕',
    '≡ƒôÖ': '📖',
    '≡ƒô×': '📗',
    '≡ƒôØ': '📘',
    '≡ƒôÙ': '📙',
    '≡ƒôÚ': '📚',
    '≡ƒôÛ': '📛',
    '≡ƒôÜ': '📜',
    '≡ƒôÝ': '📝',
    '≡ƒôÞ': '📞',
    '≡ƒôß': '📟',
    '≡ƒôà': '📠',
    '≡ƒôâ': '📢',
    '≡ƒôã': '📣',
    '≡ƒôä': '📤',
    '≡ƒôå': '📥',
    '≡ƒôæ': '📦',
    '≡ƒôç': '📧',
    # Caracteres acentuados portugueses (CP1252 mojibake)
    '├⌐': 'é',
    '├ó': 'â',
    '├ñ': 'á',
    '├â': 'Â',
    '├Â': 'Â',
    '├º': 'ç',
    '├ú': 'ã',
    '├¡': 'í',
    '├│': 'ó',
    '├╡': 'õ',
    '├ê': 'Ê',
    '├ë': 'Ë',
    '├Ç': 'À',
    '├ü': 'ü',
    '├®': 'é',
    '├¬': 'ê',
    '├«': 'î',
    '├┤': 'ô',
    '├╣': 'ù',
    '├╗': 'û',
    '├ä': 'Ä',
    '├ö': 'ö',
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_size = len(content)
    replacements = 0

    # Sort by length descending to avoid partial replacements
    for corrupted, correct in sorted(EMOJI_MAP.items(), key=lambda x: -len(x[0])):
        count = content.count(corrupted)
        if count > 0:
            content = content.replace(corrupted, correct)
            replacements += count
            print(f"  {repr(corrupted)} -> {repr(correct)} ({count}x)")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nTotal replacements: {replacements}")
    print(f"File size: {original_size} -> {len(content)} chars")
    return replacements

if __name__ == '__main__':
    filepath = 'frontend/src/components/Servers.js'
    print(f"Fixing: {filepath}")
    count = fix_file(filepath)
    print(f"\nDone! {count} replacements made.")
