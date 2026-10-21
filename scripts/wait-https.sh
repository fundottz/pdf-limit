#!/usr/bin/env bash
# Ждёт, пока podlimit.ru начнёт отдаваться по HTTPS через GitHub Pages с валидным сертификатом.
set -u
for i in $(seq 1 24); do
  ips=$(curl -s "https://cloudflare-dns.com/dns-query?name=podlimit.ru&type=A" -H 'accept: application/dns-json' \
        | python3 -c "import sys,json;print(' '.join(a['data'] for a in json.load(sys.stdin).get('Answer',[]) if a.get('type')==1))" 2>/dev/null)
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' https://podlimit.ru/ 2>/dev/null)
  cn=$(echo | timeout 10 openssl s_client -connect podlimit.ru:443 -servername podlimit.ru 2>/dev/null \
        | openssl x509 -noout -subject 2>/dev/null | tr -d '\n')
  echo "[$(date +%H:%M)] dns=[$ips] https=$code cert=[$cn]"
  if [ "$code" = "200" ] && echo "$cn" | grep -q "podlimit.ru"; then
     echo "CERT_OK: podlimit.ru отдаёт 200 с валидным сертификатом"
     exit 0
  fi
  sleep 300
done
echo "CERT_TIMEOUT: за 2 часа сертификат не появился"
