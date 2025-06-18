class MultiImageUpload {
    constructor() {
        this.images = [];
        this.maxFileSize = 5 * 1024 * 1024; // 5MB
        this.allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];

        this.initElements();
        this.bindEvents();
        this.updateUI();
    }

    initElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.imageInput = document.getElementById('imageInput');
        this.imagesGrid = document.getElementById('imagesGrid');
        this.imageCount = document.getElementById('imageCount');
        this.clearAllBtn = document.getElementById('clearAllBtn');
        this.errorMessage = document.getElementById('errorMessage');
        this.successMessage = document.getElementById('successMessage');
        this.emptyState = document.getElementById('emptyState');
        this.modal = document.getElementById('imageModal');
        this.modalImage = document.getElementById('modalImage');
        this.modalClose = document.getElementById('modalClose');
    }

    bindEvents() {
        // Drag and Drop
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', () => this.handleDragLeave());
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // File input
        this.imageInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Clear all button
        this.clearAllBtn.addEventListener('click', () => this.clearAllImages());

        // Modal events
        this.modalClose.addEventListener('click', () => this.closeModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });

        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave() {
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');

        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
        // Reset input to allow selecting the same files again
        e.target.value = '';
    }

    processFiles(files) {
        this.hideMessages();

        const validFiles = [];
        const errors = [];

        files.forEach(file => {
            if (!this.validateFile(file)) {
                errors.push(`${file.name}: Archivo no válido`);
                return;
            }

            // Check if file already exists
            const existingFile = this.images.find(img =>
                img.name === file.name && img.size === file.size
            );

            if (existingFile) {
                errors.push(`${file.name}: Ya está cargado`);
                return;
            }

            validFiles.push(file);
        });

        if (errors.length > 0) {
            this.showError(errors.join(', '));
        }

        if (validFiles.length > 0) {
            this.addImages(validFiles);
            this.showSuccess(`${validFiles.length} imagen(es) cargada(s) correctamente`);
        }
    }

    validateFile(file) {
        if (!this.allowedTypes.includes(file.type)) {
            return false;
        }

        if (file.size > this.maxFileSize) {
            return false;
        }

        return true;
    }

    addImages(files) {
        files.forEach(file => {
            const id = Date.now() + Math.random();
            const imageData = {
                id: id,
                file: file,
                name: file.name,
                size: file.size,
                url: null
            };

            // Create URL for preview
            const reader = new FileReader();
            reader.onload = (e) => {
                imageData.url = e.target.result;
                this.renderImageCard(imageData);
            };
            reader.readAsDataURL(file);

            this.images.push(imageData);
        });

        this.updateUI();
    }

    async loadImagesFromBackend(folderName, trackingName, imagesList, endpointGetImage) {
        try {
            const imagesNames = imagesList.split(',');

            // Cargar cada imagen
            const loadPromises = imagesNames.map(imageName =>
                this.loadSingleImageFromBackend(folderName, trackingName, imageName, endpointGetImage)
            );

            const results = await Promise.allSettled(loadPromises);

            // Procesar resultados
            const successCount = results.filter(result => result.status === 'fulfilled').length;
            const errorCount = results.filter(result => result.status === 'rejected').length;

            if (successCount > 0) {
                this.updateUI();
                this.showSuccess(`${successCount} imagen(es) cargada(s) desde el servidor`);
            }

            if (errorCount > 0) {
                console.warn(`${errorCount} imágenes no pudieron cargarse`);
            }

        } catch (error) {
            console.error('Error al cargar imágenes desde backend:', error);
            this.showError('Error al cargar imágenes desde el servidor');
        }
    }

    async loadSingleImageFromBackend(folderName, trackingName, imageName, endpointGetImage) {
        try {

            if (!imageName) {
                this.images = [];
                this.imagesGrid.innerHTML = '';
                this.updateUI();
            }else {
                this.images = [];
                this.imagesGrid.innerHTML = '';

                // const imageUrl = `${endpointGetImage}/seguimientos/${folderName}/${trackingName}/${imageName}`;

                const imageUrl = `/seguimientos${endpointGetImage}/${folderName}/${trackingName}/${imageName}`;

                const response = await fetch(imageUrl);
                if (!response.ok) {
                    throw new Error(`Error al cargar imagen ${imageName}: ${response.status}`);
                }

                const blob = await response.blob();

                // Verificar que sea una imagen válida
                if (!blob.type.startsWith('image/')) {
                    throw new Error(`El archivo ${imageName} no es una imagen válida`);
                }

                // Crear objeto de imagen para el backend
                const imageData = {
                    id: Date.now() + Math.random(),
                    file: null, // Las imágenes del backend no tienen file object
                    name: imageName,
                    size: blob.size,
                    url: URL.createObjectURL(blob),
                    // isFromBackend: true,
                    // blob: blob // Guardamos el blob para uso posterior
                };

                // Verificar si ya existe
                const existingImage = this.images.find(img =>
                    img.name === imageName && img.isFromBackend
                );

                if (!existingImage) {
                    this.images.push(imageData);
                    this.renderImageCard(imageData);
                }

                return imageData;
            }
        } catch (error) {
            throw error;
        }
    }

    renderImageCard(imageData) {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.dataset.imageId = imageData.id;

        card.innerHTML = `
          <img src="${imageData.url}" alt="${imageData.name}">
          <div class="image-info">
              <div class="image-name" title="${imageData.name}">${imageData.name}</div>
              <div class="image-size">${this.formatFileSize(imageData.size)}</div>
              <div class="image-actions">
                  <button type="button" class="btn btn-view" onclick="imageUploader.viewImage('${imageData.id}')">Ver</button>
                  <button type="button" class="btn btn-remove" onclick="imageUploader.removeImage('${imageData.id}')">Eliminar</button>
              </div>
          </div>
      `;

        this.imagesGrid.appendChild(card);
    }

    removeImage(id) {
        this.images = this.images.filter(img => img.id != id);

        const card = document.querySelector(`[data-image-id="${id}"]`);
        if (card) {
            card.style.transform = 'scale(0)';
            card.style.opacity = '0';
            setTimeout(() => card.remove(), 300);
        }

        this.updateUI();
        this.showSuccess('Imagen eliminada correctamente');
    }

    viewImage(id) {
        const image = this.images.find(img => img.id == id);
        if (image) {
            this.modalImage.src = image.url;
            this.modal.style.display = 'block';
        }
    }

    closeModal() {
        this.modal.style.display = 'none';
    }

    async clearAllImages() {
        if (this.images.length === 0) return;

        const result = await Swal.fire({
            title: '¿Eliminar todas las imágenes?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        });

        if (result.isConfirmed) {
            this.images = [];
            this.imagesGrid.innerHTML = '';
            this.updateUI();

            await Swal.fire(
                '¡Eliminadas!',
                'Todas las imágenes han sido eliminadas.',
                'success'
            );
        }
    }

    updateUI() {
        this.imageCount.textContent = this.images.length;

        if (this.images.length > 0) {
            this.clearAllBtn.style.display = 'block';
            this.emptyState.style.display = 'none';
        } else {
            this.clearAllBtn.style.display = 'none';
            this.emptyState.style.display = 'block';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.style.display = 'block';
        this.successMessage.style.display = 'none';
        setTimeout(() => this.hideMessages(), 5000);
    }

    showSuccess(message) {
        this.successMessage.textContent = message;
        this.successMessage.style.display = 'block';
        this.errorMessage.style.display = 'none';
        setTimeout(() => this.hideMessages(), 3000);
    }

    hideMessages() {
        this.errorMessage.style.display = 'none';
        this.successMessage.style.display = 'none';
    }

    // Método para obtener todas las imágenes (útil para envío de formulario)
    getImages() {
        return this.images.map(img => img.file);
    }

    // Método para obtener FormData listo para envío
    getFormData() {
        const formData = new FormData();
        this.images.forEach((img, index) => {
            formData.append(`images[]`, img.file);
        });
        return formData;
    }
}

// Inicializar el uploader
const imageUploader = new MultiImageUpload();

