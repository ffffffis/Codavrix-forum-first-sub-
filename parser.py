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
MAX_REPOS = 500
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
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

SEARCH_QUERIES = [
    'vless reality',
    'trojan config',
    'v2ray free',
    'vless config',
    'hysteria2 config',
    'free vpn config',
    'v2ray reality',
    'vmess config',
]

def search_github(query):
    headers = {'User-Agent': USER_AGENT}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    all_files = []
    
    params = {
        'q': f'{query} extension:txt OR extension:json OR extension:conf OR extension:list',
        'per_page': 100,
        'sort': 'updated'
    }
    
    try:
        r = requests.get(
            'https://api.github.com/search/code',
            params=params,
            headers=headers,
            timeout=15
        )
        
        if r.status_code == 200:
            data = r.json()
            for item in data.get('items', []):
                raw_url = f"https://raw.githubusercontent.com{item['path']}"
                all_files.append({
                    'name': item['name'],
                    'path': item['path'],
                    'repo': item['repository']['full_name'],
                    'url': raw_url,
                })
    except:
        pass
    
    return all_files

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
    print("🚀 GitHub PARSER — ВЕСЬ GITHUB КАЖДЫЙ ЧАС")
    print("=" * 70)
    
    all_links = []
    seen = set()
    
    for query in SEARCH_QUERIES:
        print(f"\n🔍 Поиск: {query}")
        files = search_github(query)
        print(f"  📄 Найдено файлов: {len(files)}")
        
        for file_info in files[:MAX_REPOS]:
            try:
                r = requests.get(file_info['url'], timeout=10, headers={'User-Agent': USER_AGENT})
                if r.status_code == 200:
                    links = extract_links(r.text)
                    for link in links:
                        if link not in seen:
                            seen.add(link)
                            all_links.append(link)
                    if links:
                        print(f"    ✅ +{len(links)} ссылок из {file_info['name']}")
            except:
                pass
            time.sleep(0.1)
        
        time.sleep(1)
    
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
  
