import requests
import base64
import time
import sys

# === НАСТРОЙКИ ===
# Ищем ТОЛЬКО в названии (после символа #)
KEYWORDS = ['vk', 'yandex', 'яндекс', 'timeweb', 'max']

SOURCES = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"
]

def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    final_configs = []
    unique_lines = set()
    
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
                except:
                    continue

            lines = content.splitlines()
            added_from_source = 0
            
            for line in lines:
                line = line.strip()
                if not line.startswith('vless://') or '#' not in line:
                    continue

                # Извлекаем ТОЛЬКО название (всё, что после ПЕРВОГО знака #)
                name_part = line.split('#', 1)[1].lower()
                
                # Проверяем ключевое слово СТРОГО в названии
                if any(key.lower() in name_part for key in KEYWORDS):
                    if line not in unique_lines:
                        final_configs.append(line)
                        unique_lines.add(line)
                        added_from_source += 1
            
            log(f"Из ресурса {url} отобрано по названию: {added_from_source}")

        except Exception as e:
            log(f"Ошибка при обработке {url}: {e}")

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
            
        log(f"ОБНОВЛЕНИЕ ЗАВЕРШЕНО. Сохранено серверов: {len(final_configs)}")
        
    except Exception as e:
        log(f"ОШИБКА ЗАПИСИ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
