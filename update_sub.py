import requests
import base64
import time
import re
import os

# Настройки
SOURCES = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt"
]

ALLOWED_PROTOCOLS = ('vless://', 'ss://', 'trojan://')

def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def main():
    unique_configs = set()
    
    for url in SOURCES:
        try:
            log(f"Загрузка: {url}")
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            
            for line in r.text.splitlines():
                line = line.strip()
                if not line.startswith(ALLOWED_PROTOCOLS):
                    continue
                
                # Очистка названия от спецсимволов для стабильности в Remnawave
                if '#' in line:
                    base, name = line.split('#', 1)
                    clean_name = re.sub(r'[^\w\s\-\[\]]', '', name).strip()
                    line = f"{base}#{clean_name}"
                
                unique_configs.add(line)
        except Exception as e:
            log(f"Ошибка при обработке {url}: {e}")

    if not unique_configs:
        log("Сервера не найдены. Выход.")
        return

    final_content = "\n".join(sorted(list(unique_configs)))
    
    # Сохраняем как обычный текст (многие современные панели любят именно это)
    with open("index.txt", "w", encoding="utf-8") as f:
        f.write(final_content)
    
    # Сохраняем как Base64 (для старых клиентов)
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        encoded = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')
        f.write(encoded)
        
    log(f"Готово. Собрано узлов: {len(unique_configs)}")

if __name__ == "__main__":
    main()
