import requests
import base64
import time

# === НАСТРОЙКИ ФИЛЬТРАЦИИ ===
# Скрипт оставит только те строки, где есть эти слова (регистр не важен)
KEYWORDS = ['vk', 'yandex', 'яндекс', 'timeweb', 'max']

# Источники
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Sre_Prasanna/v2ray-subscription-link/main/vless.txt"
]

def log(message):
    """Вывод лога с меткой времени"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    final_configs = []
    unique_lines = set() # Чтобы не дублировать одинаковые строки
    
    log("Запуск фильтрации серверов (VK, Яндекс, TimeWeb, Max)...")

    for url in SOURCES:
        try:
            log(f"Запрос к источнику: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            # Проверка, не зашифрован ли сам источник в base64
            if not content.strip().startswith('vless://'):
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except:
                    pass 

            lines = content.splitlines()
            count_before = len(final_configs)
            
            for line in lines:
                line = line.strip()
                if not line.startswith('vless://'):
                    continue

                # Проверяем наличие ключевых слов в оригинальной строке
                line_lower = line.lower()
                if any(key.lower() in line_lower for key in KEYWORDS):
                    if line not in unique_lines:
                        final_configs.append(line)
                        unique_lines.add(line)
            
            log(f"Добавлено {len(final_configs) - count_before} серверов из этого источника.")

        except Exception as e:
            log(f"ОШИБКА при работе с {url}: {e}")

    if not final_configs:
        log("ВНИМАНИЕ: Подходящих серверов не найдено. Файлы не будут обновлены, чтобы не затереть старые данные.")
        return

    # 1. Сохраняем как есть (текстовый список)
    try:
        with open("index.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
        log("Файл index.txt обновлен.")
    except Exception as e:
        log(f"ОШИБКА записи index.txt: {e}")

    # 2. Сохраняем в base64 для подписки
    try:
        with open("sub_base64.txt", "w", encoding="utf-8") as f:
            full_text = "\n".join(final_configs)
            encoded = base64.b64encode(full_text.encode('utf-8')).decode('utf-8')
            f.write(encoded)
        log("Файл sub_base64.txt обновлен.")
    except Exception as e:
        log(f"ОШИБКА записи sub_base64.txt: {e}")

    log(f"Итого отобрано серверов: {len(final_configs)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"КРИТИЧЕСКАЯ ОШИБКА СКРИПТА: {e}")
