#!/usr/bin/env python3
import re
import requests
import subprocess
import time
import socket
import os

# ----------- НАСТРОЙКИ -----------
OUTPUT_FILE = "working_configs.txt"
TIMEOUT = 3
USER_AGENT = "Mozilla/5.0"
# --------------------------------

# ХЕДЕР ДЛЯ ПОДПИСКИ
HEADER = """#hide-servers: true
#hide-setting : true
#skip-servers: true
#hide: true
#hide-servers: 1
#hide-setting : 1
#hide: 1
#skip-servers: 1
#profile-title: AISubCodavrix🌸
#color-profile:
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=0; expire=0
#announce: 67 крутой мэм
#support-url: https://t.me/codavrix_forum
#profile-web-page-url: https://t.me/codavrix_forum
"""

def extract_links(text):
    patterns = [
        r'(vless://[^\s]+)',
        r'(trojan://[^\s]+)',
        r'(hysteria2://[^\s]+)',
        r'(ss://[A-Za-z0-9+/=]+@[\d.]+:\d+[^\s]*)',
        r'(vmess://[A-Za-z0-9+/=]+)',
    ]
    links = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        links.extend(matches)
    return list(dict.fromkeys(links))

def extract_ip(link):
    match = re.search(r'@([\d.]+):\d+', link)
    if match:
        return match.group(1)
    match = re.search(r'([\d.]+):\d+', link)
    if match:
        return match.group(1)
    return None

def check_alive(link):
    ip = extract_ip(link)
    if not ip:
        return False
    
    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
        try:
            ip = socket.gethostbyname(ip)
        except:
            return False
    
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(TIMEOUT), ip],
            capture_output=True,
            timeout=TIMEOUT + 2
        )
        return result.returncode == 0
    except:
        return False

def get_geo(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,isp", timeout=5)
        data = r.json()
        if data.get('status') == 'success':
            return data.get('country', 'Unknown'), data.get('city', 'Unknown'), data.get('isp', '')
    except:
        pass
    return "Unknown", "Unknown", ""

def get_flag(code):
    flags = {
        'RU': '🇷🇺', 'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪',
        'FR': '🇫🇷', 'NL': '🇳🇱', 'FI': '🇫🇮', 'SE': '🇸🇪',
        'PL': '🇵🇱', 'EE': '🇪🇪', 'LV': '🇱🇻', 'LT': '🇱🇹',
        'CA': '🇨🇦', 'JP': '🇯🇵', 'KR': '🇰🇷', 'IT': '🇮🇹',
        'ES': '🇪🇸', 'PT': '🇵🇹', 'TR': '🇹🇷', 'BR': '🇧🇷',
        'CN': '🇨🇳', 'TH': '🇹🇭', 'VN': '🇻🇳', 'MY': '🇲🇾',
        'ID': '🇮🇩', 'PH': '🇵🇭', 'IN': '🇮🇳', 'PK': '🇵🇰',
        'BD': '🇧🇩', 'AZ': '🇦🇿', 'AL': '🇦🇱', 'AT': '🇦🇹',
        'UA': '🇺🇦', 'BY': '🇧🇾', 'KZ': '🇰🇿', 'KG': '🇰🇬',
        'UZ': '🇺🇿', 'GE': '🇬🇪', 'AM': '🇦🇲', 'MD': '🇲🇩',
        'IR': '🇮🇷', 'IQ': '🇮🇶', 'SY': '🇸🇾', 'LB': '🇱🇧',
        'JO': '🇯🇴', 'PS': '🇵🇸', 'SA': '🇸🇦', 'AE': '🇦🇪'
    }
    return flags.get(code.upper(), '🏳️')

def is_russia(country):
    russian = ['Россия', 'Russia', 'Russian Federation', 'RU', 'РФ']
    return any(ru in country for ru in russian)

def rename_link(link):
    ip = extract_ip(link)
    if not ip:
        return link
    
    country, city, isp = get_geo(ip)
    
    if is_russia(country):
        prefix = "🤍БС 🇷🇺"
        name = f"{prefix} Россия {city}"
    else:
        flag = get_flag(country[:2]) if len(country) >= 2 else '🏳️'
        name = f"{flag} {country} {city}"
    
    if isp and isp.strip():
        isp_clean = isp.split(',')[0].strip()
        if isp_clean and len(isp_clean) < 30:
            name = f"{name} {isp_clean}"
    
    name = f"{name} @codavrix_forum"
    encoded = name.replace(' ', '%20')
    
    return re.sub(r'#.*$', f'#{encoded}', link)

def main():
    print("=" * 70)
    print("🚀 ПАРСЕР — ТВОИ ИСТОЧНИКИ")
    print("=" * 70)
    
    # Читаем источники
    try:
        with open("sources.txt", "r", encoding="utf-8") as f:
            repos = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"❌ Ошибка чтения sources.txt: {e}")
        return
    
    if not repos:
        print("❌ Нет источников в sources.txt!")
        return
    
    print(f"\n📚 Источников: {len(repos)}")
    
    all_links = []
    seen = set()
    
    for url in repos:
        print(f"\n🔍 Парсинг: {url}")
        try:
            r = requests.get(url, timeout=15, headers={'User-Agent': USER_AGENT})
            if r.status_code == 200:
                links = extract_links(r.text)
                for link in links:
                    if link not in seen:
                        seen.add(link)
                        all_links.append(link)
                print(f"  ✅ +{len(links)} ссылок")
            else:
                print(f"  ❌ Ошибка HTTP: {r.status_code}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        time.sleep(0.5)
    
    print(f"\n📊 Всего найдено уникальных ссылок: {len(all_links)}")
    
    if not all_links:
        print("❌ Ссылок не найдено!")
        return
    
    print("\n🔍 Проверка работоспособности...")
    working = []
    total = len(all_links)
    
    for i, link in enumerate(all_links):
        print(f"  {i+1}/{total}: ", end="")
        if check_alive(link):
            renamed = rename_link(link)
            working.append(renamed)
            print("✅ ЖИВ")
        else:
            print("❌ Мертв")
        
        if (i + 1) % 10 == 0:
            time.sleep(0.3)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        f.write("\n".join(working))
    
    print("\n" + "=" * 70)
    print(f"🎯 РАБОЧИХ ССЫЛОК: {len(working)}")
    print(f"📁 Сохранено в: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
