import requests
import base64
import time
import sys

# === НАСТРОЙКИ ===
# Ищем только в названии (после символа #)
KEYWORDS = ['vk', 'yandex', 'яндекс', 'timeweb', 'max']

# Ваши персональные источники
SOURCES = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"
]

def log(message):
    """Логирование в консоль с отметкой времени"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    final_configs = []
    unique_lines = set()
    
    log(f"Запуск фильтрации по вашим ресурсам. Ключевые слова: {', '.join(KEYWORDS)}")

    for url in SOURCES:
        try:
            log(f"Запрос к ресурсу: {url}")
            # Увеличил таймаут до 30 секунд для стабильности
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Проверка на base64 (если файл зашифрован целиком)
            if not content.strip().startswith('vless://'):
                try:
                    content = base64.b64decode(content).decode('utf-8')
                    log(f"Файл {url} успешно декодирован из base64.")
                except Exception:
                    log(f"Предупреждение: {url} не является прямой ссылкой и не base64. Пропускаю.")
                    continue

            lines = content.splitlines()
            added_from_source = 0
            
            for line in lines:
                line = line.strip()
                if not line.startswith('vless://'):
                    continue

                # Фильтрация строго по названию после знака #
                if '#' in line:
                    # Берем всё, что после первого знака #
                    name_part = line.split('#', 1)[1].lower()
                    
                    # Проверяем наличие ключевых слов
                    if any(key.lower() in name_part for key in KEYWORDS):
                        if line not in unique_lines:
                            final_configs.append(line)
                            unique_lines.add(line)
                            added_from_source += 1
            
            log(f"Из ресурса {url} отобрано: {added_from_source} серверов.")

        except requests.exceptions.RequestException as e:
            log(f"ОШИБКА СЕТИ при обращении к {url}: {e}")
        except Exception as e:
            log(f"НЕПРЕДВИДЕННАЯ ОШИБКА при обработке {url}: {e}")

    if not final_configs:
        log("РЕЗУЛЬТАТ: Подходящих серверов не найдено. Файлы обновлены не будут.")
        return

    # Запись результатов
    try:
        # 1. Текстовый файл (index.txt)
        with open("ForFriends.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
        
        # 2. Base64 файл для подписки (sub_base64.txt)
        with open("sub_base64.txt", "w", encoding="utf-8") as f:
            full_content = "\n".join(final_configs)
            encoded = base64.b64encode(full_content.encode('utf-8')).decode('utf-8')
            f.write(encoded)
            
        log(f"ОБНОВЛЕНИЕ ЗАВЕРШЕНО. Всего сохранено: {len(final_configs)} серверов.")
        
    except IOError as e:
        log(f"ОШИБКА ЗАПИСИ ФАЙЛА: {e}")
        sys.exit(1)
    except Exception as e:
        log(f"ОШИБКА при сохранении данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"КРИТИЧЕСКАЯ ОШИБКА ВЫПОЛНЕНИЯ: {e}")
        sys.exit(1)
