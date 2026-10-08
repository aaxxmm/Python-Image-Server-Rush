<!-- Отправка файла на Python-бэкенд -->
document.addEventListener('DOMContentLoaded', function () {
    const fileUpload = document.getElementById('file-upload');
    const imagesButton = document.getElementById('images-tab-btn');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');

    const handleAndStoreFiles = async (files) => {
        if (!files || files.length === 0) return;

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

        for (const file of files) {
            if (!allowedTypes.includes(file.type) || file.size > MAX_SIZE_BYTES) {
                alert(`Файл ${file.name} не подходит по формату или размеру.`);
                continue;
            }

            const formData = new FormData();
            formData.append('image', file);

            try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'Accept': 'application/json'
                        }
                    });

                if (response.ok) {
                    const result = await response.json();
                    // Показываем ссылку в поле ввода
                    currentUploadInput.value = result.url;
                    // Сохраняем для страницы images.html
                    const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
                    storedFiles.push({ name: result.filename, url: result.url });
                    localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                    alert(`✅ Файл ${file.name} успешно загружен!`);
                } else {
                    const errorText = await response.text();
                    alert(`❌ Ошибка: ${errorText}`);
                }
            } catch (error) {
                alert(`❌ Ошибка сети: ${error.message}`);
            }
        }
    };

    if (copyButton && currentUploadInput) {
        copyButton.addEventListener('click', () => {
            const textToCopy = currentUploadInput.value;
            if (textToCopy && textToCopy !== 'https://') {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyButton.textContent = 'COPIED!';
                    setTimeout(() => { copyButton.textContent = 'COPY'; }, 2000);
                });
            }
        });
    }

    if (imagesButton) {
        imagesButton.addEventListener('click', () => {
            window.location.href = 'images.html';
        });
    }

    if (fileUpload) {
        fileUpload.addEventListener('change', (event) => {
            handleAndStoreFiles(event.target.files);
            event.target.value = '';
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropzone.addEventListener('drop', (event) => {
            handleAndStoreFiles(event.dataTransfer.files);
        });
    }
});