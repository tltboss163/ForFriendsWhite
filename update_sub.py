import requests
import base64
import time
import sys
import urllib.parse

# === НАСТРОЙКИ ===
# Ищем ТОЛЬКО в названии
KEYWORDS = ['vk', 'yandex', 'яндекс', 'timeweb', 'max']

SOURCES = [
#    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"
]

def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    final_configs = []
    unique_configs = set() # Здесь храним ТОЛЬКО техническую часть, чтобы исключить дубли
    
    log(f"Запуск строгой фильтрации по названиям: {', '.join(KEYWORDS)}")

    for url in SOURCES:
        try:
            log(f"Запрос к ресурсу: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Проверка на base64
            if not content.strip().startswith('vless://'):
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except Exception as e:
                    log(f"[ОШИБКА] Контент не является base64 или vless: {e}")
                    continue

            lines = content.splitlines()
            added_from_source = 0
            
            for line in lines:
                line = line.strip()
                if not line.startswith('vless://') or '#' not in line:
                    continue

                # Разделяем строку на саму конфигурацию (до #) и оригинальное имя (после #)
                parts = line.split('#', 1)
                base_config = parts[0]
                original_name = parts[1]
                
                # Декодируем имя из URL-формата для корректного поиска ключевых слов (VK, Yandex и т.д.)
                name_part_decoded = urllib.parse.unquote(original_name)
                
                # Проверяем ключевое слово СТРОГО в декодированном названии
                if any(key.lower() in name_part_decoded.lower() for key in KEYWORDS):
                    
                    # Проверяем на дубликаты ИМЕННО по технической части (без учета имени)
                    if base_config not in unique_configs:
                        unique_configs.add(base_config)
                        
                        # Сохраняем строку в исходном виде, возвращая оригинальное имя (сохраняем нумерацию)
                        final_line = f"{base_config}#{original_name}"
                        final_configs.append(final_line)
                        added_from_source += 1
            
            log(f"Из ресурса {url} отобрано уникальных: {added_from_source}")

        except Exception as e:
            log(f"[ОШИБКА] Сбой при обработке {url}: {e}")

    # Запись результатов
    try:
        # 1. Текстовый файл
        with open("ForFriends.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
        
        # 2. Base64 файл
        with open("sub_base64.txt", "w", encoding="utf-8") as f:
            full_content = "\n".join(final_configs)
            encoded = base64.b64encode(full_content.encode('utf-8')).decode('utf-8')
            f.write(encoded)
            
        log(f"ОБНОВЛЕНИЕ ЗАВЕРШЕНО. Сохранено уникальных серверов с оригинальной нумерацией: {len(final_configs)}")
        
    except Exception as e:
        log(f"[ОШИБКА] Сбой при записи файлов: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
