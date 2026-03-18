#!/usr/bin/env python3
import re

with open('frontend/src/components/Servers.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all unique Gamma sequences
gamma_matches = {}
for m in re.finditer(r'Γ[\S]{1,8}', content):
    s = m.group()
    gamma_matches[s] = gamma_matches.get(s, 0) + 1

print('Gamma sequences:')
for s, count in sorted(gamma_matches.items()):
    idx = content.find(s)
    ctx = content[max(0,idx-15):idx+len(s)+15].replace('\n','\\n')
    print(f'  {repr(s)} ({count}x) ctx: {repr(ctx)}')

print()
# Find box sequences
box_matches = {}
for m in re.finditer(r'[\u2500-\u257F\u2580-\u259F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF][\S]{1,8}', content):
    s = m.group()
    box_matches[s] = box_matches.get(s, 0) + 1

print('Box/special sequences:')
for s, count in sorted(box_matches.items()):
    idx = content.find(s)
    ctx = content[max(0,idx-15):idx+len(s)+15].replace('\n','\\n')
    print(f'  {repr(s)} ({count}x) ctx: {repr(ctx)}')

print()
# Find remaining accented chars (├ sequences)
accent_matches = {}
for m in re.finditer(r'\u251C[\S]{1,3}', content):
    s = m.group()
    accent_matches[s] = accent_matches.get(s, 0) + 1

print('Accent sequences (├...):')
for s, count in sorted(accent_matches.items()):
    print(f'  {repr(s)} ({count}x)')
