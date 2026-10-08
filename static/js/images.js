<!-- Показ списка загруженных картинок -->
document.addEventListener('DOMContentLoaded', () => {
    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    const displayFiles = () => {
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
        fileListWrapper.innerHTML = '';

        if (storedFiles.length === 0) {
            fileListWrapper.innerHTML = '<p style="text-align: center; margin-top: 50px; color: #333;">No images uploaded yet.</p>';
        } else {
            const container = document.createElement('div');
            container.className = 'file-list-container';
            const header = document.createElement('div');
            header.className = 'file-list-header';
            header.innerHTML = `
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-url">Url</div>
                <div class="file-col file-col-delete">Delete</div>
            `;
            container.appendChild(header);

            const list = document.createElement('div');
            list.id = 'file-list';

            storedFiles.forEach((fileData, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                    <div class="file-col file-col-name">
                        <span class="file-name">${fileData.name}</span>
                    </div>
                    <div class="file-col file-col-url">
                        <a href="${fileData.url}" target="_blank">${fileData.url}</a>
                    </div>
                    <div class="file-col file-col-delete">
                        <button class="delete-btn" data-index="${index}">🗑️</button>
                    </div>
                `;
                list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);

            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const indexToDelete = parseInt(event.currentTarget.dataset.index);
                    let storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
                    storedFiles.splice(indexToDelete, 1);
                    localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                    displayFiles();
                });
            });
        }
    };

    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = 'upload.html';
        });
    }

    displayFiles();
});