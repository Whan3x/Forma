#!/bin/sh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "FORMA potřebuje Python 3.9 nebo novější."
  echo "Návod najdeš v souboru NAVOD.html."
  exit 1
fi
echo "Otevři v prohlížeči http://127.0.0.1:8765"
echo "Toto okno nech otevřené. Ukončení: Ctrl+C."
exec python3 server.py
