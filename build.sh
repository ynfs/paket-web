#!/bin/sh
# Bungkus file artifact (tanpa <html>/<head>) menjadi public/index.html lengkap
set -e
SRC="$1"; OUT="$(dirname "$0")/public/index.html"
{
cat <<'H'
<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Interlude Media, partner kreatif Anda: website & sistem, aplikasi Android, dan IoT. Permanent atau langganan.">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
H
awk '/^<\/style>/{print; exit} {print}' "$SRC"
echo "</head>"; echo "<body>"
awk 'f{print} /^<\/style>/{f=1}' "$SRC"
echo "</body>"; echo "</html>"
} > "$OUT"
