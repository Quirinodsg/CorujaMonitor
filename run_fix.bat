@echo off
python fix_servers_encoding.py > fix_output.txt 2>&1
type fix_output.txt
