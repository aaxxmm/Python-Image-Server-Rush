#!/usr/bin/env python3
"""
Сервер картинок - бэкенд на Python
Обрабатывает загрузку изображений, валидацию и логирование
"""

import os
import sys
import json
import time
import uuid
import logging
import mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

# Конфигурация
UPLOAD_DIR = '/images'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

# Настройка логирования
LOG_DIR = '/logs'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Создаем директории, если их нет
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Настройка логгера
logger = logging.getLogger('ImageServer')
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# Хендлер для файла
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Хендлер для консоли (для отладки)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def generate_unique_filename(original_filename):
    """Генерирует уникальное имя для файла"""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}{ext}"


def validate_file(content_type, content_length, filename):
    """
    Проверяет файл на соответствие требованиям
    Возвращает (is_valid, error_message)
    """
    # Проверка размера
    if content_length > MAX_FILE_SIZE:
        return False, f"Файл слишком большой. Максимальный размер: 5 МБ (текущий: {content_length / 1024 / 1024:.2f} МБ)"

    # Проверка MIME типа
    if content_type not in ALLOWED_MIME_TYPES:
        return False, f"Неподдерживаемый MIME-тип: {content_type}. Поддерживаются: image/jpeg, image/png, image/gif"

    # Проверка расширения файла
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Неподдерживаемое расширение файла: {ext}. Поддерживаются: .jpg, .jpeg, .png, .gif"

    return True, ""


class ImageHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов для сервера картинок"""

    server_version = "ImageServer/1.0"

    def log_message(self, format, *args):
        """Переопределяем для использования нашего логгера"""
        logger.info(f"Request: {format % args}")

    def do_GET(self):
        """Обработка GET-запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            self.serve_home()
        elif path == '/upload':
            self.serve_upload_page()
        elif path == '/images/help':
            self.serve_images_help()
        else:
            self.send_error(404, "Страница не найдена")
            logger.warning(f"404 Not Found: {path}")

    def do_POST(self):
        """Обработка POST-запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/upload':
            self.handle_upload()
        else:
            self.send_error(404, "Страница не найдена")
            logger.warning(f"404 Not Found (POST): {path}")

    def serve_home(self):
        """Главная страница"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Сервер Картинок</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                    color: #333;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                .card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin: 20px 0;
                }
                .menu {
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                }
                .menu a {
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }
                .menu a:hover {
                    background: #2980b9;
                }
                .features {
                    list-style: none;
                    padding: 0;
                }
                .features li {
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                }
                .features li:last-child {
                    border-bottom: none;
                }
                .features li::before {
                    content: "✓ ";
                    color: #27ae60;
                    font-weight: bold;
                }
                .footer {
                    margin-top: 30px;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <h1>🖼️ Сервер Картинок</h1>

            <div class="card">
                <h2>Добро пожаловать!</h2>
                <p>Этот сервис позволяет загружать изображения и получать прямые ссылки на них.</p>
                <p>Поддерживаются форматы: <strong>JPG, PNG, GIF</strong></p>
                <p>Максимальный размер файла: <strong>5 МБ</strong></p>
            </div>

            <div class="card">
                <h3>📋 Возможности:</h3>
                <ul class="features">
                    <li>Загрузка изображений в популярных форматах</li>
                    <li>Автоматическая генерация уникальных ссылок</li>
                    <li>Надежное хранение ваших файлов</li>
                    <li>Быстрая раздача через Nginx</li>
                    <li>Подробное логирование всех действий</li>
                </ul>
            </div>

            <div class="card">
                <h3>🚀 Быстрый старт:</h3>
                <div class="menu">
                    <a href="/upload">📤 Загрузить изображение</a>
                    <a href="/images/help">📁 Как посмотреть изображения</a>
                </div>
            </div>

            <div class="card">
                <h3>📖 Как использовать:</h3>
                <ol>
                    <li>Нажмите <strong>"Загрузить изображение"</strong></li>
                    <li>Выберите файл и отправьте</li>
                    <li>Получите прямую ссылку на ваше изображение</li>
                    <li>Используйте ссылку где угодно!</li>
                </ol>
            </div>

            <div class="footer">
                <p>Сервер картинок v1.0 | Работает на Python + Nginx + Docker</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_upload_page(self):
        """Страница загрузки"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Загрузка изображения - Сервер Картинок</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                    color: #333;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                .card {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin: 20px 0;
                }
                .upload-form {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                .file-input {
                    padding: 15px;
                    border: 2px dashed #bdc3c7;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: border-color 0.3s;
                }
                .file-input:hover {
                    border-color: #3498db;
                }
                .file-input input[type="file"] {
                    width: 100%;
                    padding: 10px 0;
                }
                .submit-btn {
                    background: #2ecc71;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 5px;
                    font-size: 1.1em;
                    cursor: pointer;
                    transition: background 0.3s;
                }
                .submit-btn:hover {
                    background: #27ae60;
                }
                .back-link {
                    display: inline-block;
                    margin-top: 20px;
                    color: #3498db;
                    text-decoration: none;
                }
                .back-link:hover {
                    text-decoration: underline;
                }
                .info {
                    background: #ecf0f1;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 0.9em;
                    color: #7f8c8d;
                }
                .result {
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 5px;
                    display: none;
                }
                .result.success {
                    display: block;
                    background: #d5f5e3;
                    border: 1px solid #27ae60;
                    color: #1a7a42;
                }
                .result.error {
                    display: block;
                    background: #fadbd8;
                    border: 1px solid #e74c3c;
                    color: #922b21;
                }
            </style>
        </head>
        <body>
            <h1>📤 Загрузка изображения</h1>

            <div class="card">
                <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                    <div class="file-input">
                        <input type="file" name="image" accept=".jpg,.jpeg,.png,.gif" required>
                    </div>

                    <div class="info">
                        <strong>Требования:</strong><br>
                        • Форматы: JPG, PNG, GIF<br>
                        • Максимальный размер: 5 МБ
                    </div>

                    <button type="submit" class="submit-btn">📤 Загрузить</button>
                </form>

                <div id="result" class="result"></div>

                <a href="/" class="back-link">← На главную</a>
            </div>

            <script>
                // Обработка ответа от сервера при загрузке через fetch
                document.querySelector('.upload-form').addEventListener('submit', async function(e) {
                    e.preventDefault();

                    const formData = new FormData(this);
                    const resultDiv = document.getElementById('result');

                    try {
                        const response = await fetch('/upload', {
                            method: 'POST',
                            body: formData
                        });

                        const text = await response.text();

                        if (response.ok) {
                            resultDiv.className = 'result success';

                            // Парсим ответ от сервера
                            try {
                                const data = JSON.parse(text);
                                resultDiv.innerHTML = `
                                    <strong>✅ Успешно загружено!</strong><br>
                                    Ссылка: <a href="${data.url}" target="_blank">${data.url}</a>
                                `;
                            } catch {
                                resultDiv.textContent = text;
                            }
                        } else {
                            resultDiv.className = 'result error';
                            resultDiv.textContent = '❌ ' + text;
                        }
                    } catch (error) {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = '❌ Ошибка при загрузке: ' + error.message;
                    }
                });
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_upload(self):
        """Обработка загрузки файла"""
        content_type = self.headers.get('Content-Type', '')

        # Проверка на multipart/form-data
        if not content_type.startswith('multipart/form-data'):
            logger.warning("Неверный Content-Type")
            self.send_error(400, "Неверный Content-Type. Ожидается multipart/form-data")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "Пустой запрос")
            return

        try:
            # Чтение данных
            data = self.rfile.read(content_length)

            # Парсинг multipart данных (простая реализация)
            boundary = content_type.split('boundary=')[1].encode()
            parts = data.split(boundary)

            file_data = None
            filename = None

            for part in parts:
                if b'Content-Disposition: form-data' in part:
                    # Извлекаем имя файла
                    filename_match = re.search(rb'filename="([^"]+)"', part)
                    if filename_match:
                        filename = filename_match.group(1).decode('utf-8', errors='ignore')
                        # Находим начало данных файла (после двух переводов строк)
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            file_data = part[header_end + 4:].strip()
                            break

            if not file_data or not filename:
                logger.warning("Файл не найден в запросе")
                self.send_error(400, "Файл не найден в запросе")
                return

            # Валидация файла
            is_valid, error_msg = validate_file(
                self.guess_content_type(filename, file_data),
                len(file_data),
                filename
            )

            if not is_valid:
                logger.error(f"Ошибка валидации: {error_msg}")
                self.send_error(400, error_msg)
                return

            # Генерация уникального имени
            unique_filename = generate_unique_filename(filename)
            filepath = os.path.join(UPLOAD_DIR, unique_filename)

            # Сохранение файла
            with open(filepath, 'wb') as f:
                f.write(file_data)

            # Создание ссылки
            url = f"/images/{unique_filename}"

            # Логирование успеха
            logger.info(f"Успех: изображение {unique_filename} загружено (оригинал: {filename})")

            # Определяем, хочет ли клиент HTML или JSON
            accept_header = self.headers.get('Accept', '')

            # Возвращаем JSON
            response = {
                "success": True,
                "filename": unique_filename,
                "url": url,
                "message": "Изображение успешно загружено"
            }
            response_json = json.dumps(response, ensure_ascii=False)

            response_bytes = response_json.encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)

        except Exception as e:
            logger.error(f"Ошибка при загрузке файла: {str(e)}")
            self.send_error(500, f"Внутренняя ошибка сервера: {str(e)}")

    def send_upload_success_html(self, filename, original_name):
        """Красивая HTML-страница после успешной загрузки"""
        full_url = f"http://localhost:8080/images/{filename}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Изображение загружено</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                h1 {{ color: #27ae60; }}
                .card {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin: 20px 0;
                }}
                .success-icon {{
                    font-size: 4em;
                    text-align: center;
                    margin: 20px 0;
                }}
                .preview {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .preview img {{
                    max-width: 100%;
                    max-height: 400px;
                    border-radius: 5px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }}
                .link-box {{
                    background: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    word-break: break-all;
                    font-family: Consolas, monospace;
                }}
                .link-box a {{
                    color: #2980b9;
                    text-decoration: none;
                }}
                .link-box a:hover {{
                    text-decoration: underline;
                }}
                .copy-btn {{
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1em;
                    margin-top: 10px;
                }}
                .copy-btn:hover {{
                    background: #2980b9;
                }}
                .info {{
                    background: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #3498db;
                }}
                .actions {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 20px;
                }}
                .actions a {{
                    display: inline-block;
                    background: #2ecc71;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                .actions a:hover {{
                    background: #27ae60;
                }}
                .actions a.secondary {{
                    background: #95a5a6;
                }}
                .actions a.secondary:hover {{
                    background: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="success-icon">✅</div>
                <h1 style="text-align: center;">Изображение успешно загружено!</h1>
    
                <div class="preview">
                    <img src="/images/{filename}" alt="Загруженное изображение">
                </div>
    
                <div class="info">
                    <strong>📄 Оригинальное имя:</strong> {original_name}<br>
                    <strong>💾 Новое имя:</strong> {filename}
                </div>
    
                <h3>🔗 Прямая ссылка:</h3>
                <div class="link-box">
                    <a href="{full_url}" target="_blank">{full_url}</a>
                </div>
    
                <button class="copy-btn" onclick="copyLink()">
                    📋 Скопировать ссылку
                </button>
    
                <div class="actions">
                    <a href="/upload">📤 Загрузить ещё</a>
                    <a href="/" class="secondary">🏠 На главную</a>
                </div>
            </div>
    
            <script>
                function copyLink() {{
                    const url = "{full_url}";
                    navigator.clipboard.writeText(url).then(() => {{
                        alert('✅ Ссылка скопирована в буфер обмена!');
                    }}).catch(() => {{
                        // Fallback для старых браузеров
                        const input = document.createElement('input');
                        input.value = url;
                        document.body.appendChild(input);
                        input.select();
                        document.execCommand('copy');
                        document.body.removeChild(input);
                        alert('✅ Ссылка скопирована!');
                    }});
                }}
            </script>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def guess_content_type(self, filename, data):
        """Угадывает MIME-тип файла"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        return mime_types.get(ext, 'application/octet-stream')

    def send_error(self, code, message=None):
        """Отправка ошибки с логированием"""
        if message is None:
            message = self.responses.get(code, ('', ''))[1]

        # Добавляем HTML-формат для ошибок
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Ошибка {code}</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                h1 {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>⚠️ Ошибка {code}</h1>
            <p>{message}</p>
            <a href="/">← На главную</a>
        </body>
        </html>
        """

        html_bytes = html.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_bytes)))
        self.end_headers()
        self.wfile.write(html_bytes)


def run_server(host='0.0.0.0', port=8000):
    """Запуск HTTP-сервера"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, ImageHandler)

    logger.info(f"Сервер запущен на http://{host}:{port}")
    logger.info(f"Директория загрузки: {UPLOAD_DIR}")
    logger.info(f"Директория логов: {LOG_DIR}")
    logger.info("Нажмите Ctrl+C для остановки")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
        httpd.server_close()


if __name__ == '__main__':
    # Проверка аргументов командной строки
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    run_server(host, port)