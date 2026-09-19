@echo off
chcp 65001 > nul
title AutoTagger RYM (GUI)
cd /d "%~dp0"
python main.py --gui
