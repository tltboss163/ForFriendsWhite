import requests
import base64
import time
import sys

# === НАСТРОЙКИ ===
# Ключевые слова для поиска
KEYWORDS = ['vk', 'yandex', 'яндекс', 'timeweb', 'max']

# Ваши персональные источники
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
    
    log(f"Запуск фильтрации. Ключевые слова: {', '.join(KEYWORDS)}")

    for url in SOURCES:
        try:
            log(f"Запрос к ресурсу: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Декодирование, если весь файл в base64
            if not content.strip().startswith('vless://'):
                try:
                    content = base64.b64decode(content).decode('utf-8')
                    log(f"Файл {url} успешно декодирован из base64.")
                except:
                    log(f"Предупреждение: {url} не vless и не base64.")
                    continue

            lines = content.splitlines()
            log(f"Всего строк в файле: {len(lines)}")
            added_from_source = 0
            
            for line in lines:
                line = line.strip()
                if not line.startswith('vless://'):
                    continue

                # Ищем ключевое слово во всей строке для надежности
                line_lower = line.lower()
                if any(key.lower() in line_lower for key in KEYWORDS):
                    if line not in unique_lines:
                        final_configs.append(line)
                        unique_lines.add(line)
                        added_from_source += 1
            
            log(f"Из ресурса {url} отобрано: {added_from_source} серверов.")

        except Exception as e:
            log(f"ОШИБКА при обработке {url}: {e}")

    # Запись результатов (даже если список пуст)
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
