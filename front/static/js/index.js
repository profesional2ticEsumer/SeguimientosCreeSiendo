// variables globales
let currentDocId = null;
let currentasviserId = null;
let currentSeguimiento = 1;
const MAX_SEGUIMIENTOS = 8; // Número total de seguimientos

// Funcion para cargar el formulario con datos
async function loadSeguimiento(familyId, adviserId) {
  try {
    const response = await fetch(`/get-seguimiento/documento_${familyId}_${adviserId}/seguimiento_${currentSeguimiento}`);
    if (!response.ok) {
      throw new Error(!response.ok ? `Error al cargar el seguimiento ${currentSeguimiento}` : 'Error de red');
    }

    const data = await response.json();

    updateFormWithData(data);
    updateProgressIndicator();
    updateFormTitle();

    // Cargar las imágenes asociadas
    if (imageUploader) {
      await imageUploader.loadImagesFromBackend(
        `documento_${familyId}_${adviserId}`,
        `seguimiento_${currentSeguimiento}`,
        `${data.imagenes}`,
        '/image'           
      );
    }
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.message || 'Ocurrió un error al cargar el seguimiento',
      confirmButtonText: 'Aceptar'
    });
  }
}

function toggleFollowUps(familyId, adviser) {
  const followUpList = document.getElementById(familyId);
  const isActive = followUpList.classList.contains('active');

  currentDocId = familyId; // Actualizar el doc_id actual
  currentasviserId = adviser; // Actualizar el asesor actual

  // Cerrar todas las listas
  document.querySelectorAll('.follow-up-list').forEach(list => {
    list.classList.remove('active');
  });

  // Alternar la lista seleccionada
  if (!isActive) {
    followUpList.classList.add('active');
    document.querySelector('.form-container').style.display = 'block'; // Mostrar el formulario
    loadSeguimiento(familyId, adviser); // Cargar
  }
}

async function createNewFamily() {
  const { value: result } = await Swal.fire({
    title: 'Nueva Familia',
    html:
      '<input id="swal-doc" class="swal2-input" placeholder="Número de documento">' +
      '<input id="swal-lastname" class="swal2-input" placeholder="Apellido de la familia">',
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Crear Familia',
    cancelButtonText: 'Cancelar',
    preConfirm: () => {
      const doc = document.getElementById('swal-doc').value.trim();
      const lastname = document.getElementById('swal-lastname').value.trim();
      if (!doc || !lastname) {
        Swal.showValidationMessage('Debe completar ambos campos');
        return;
      }
      return { doc_number: doc, apellido: lastname };
    }
  });

  if (result) {
    // Enviar al backend
    const response = await fetch('/create-document', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(result)
    });

    const data = await response.json();
    if (data.success) {
      Swal.fire('¡Familia creada!', 'La carpeta y el archivo JSON fueron generados correctamente.', 'success');
      // Puedes redirigir si quieres: window.location.href = data.redirect_url;
      setTimeout(() => window.location.reload(), 2000); // Espera 1.5 segundos y refresca

    } else {
      Swal.fire('Error', data.detail || 'Hubo un error al crear la familia.', 'error');
    }
  }
}

async function saveAndContinue() {
  // Validar campos requeridos
  const requiredFields = document.querySelectorAll('input[required], textarea[required]');
  let allValid = true;

  requiredFields.forEach(field => {
    if (!field.value.trim()) {
      field.style.borderColor = '#ef4444';
      allValid = false;
    } else {
      field.style.borderColor = '#e2e8f0';
    }
  });

  if (!allValid) {
    Swal.fire({
      icon: 'warning',
      title: 'Campos incompletos',
      text: 'Por favor, completa todos los campos requeridos antes de continuar.',
      confirmButtonText: 'Aceptar'
    });
    return;
  }

  try {
    const formData = collectFormData();

    // 1. Enviar datos del formulario
    const response = await fetch(`/save-seguimiento/documento_${currentDocId}_${currentasviserId}/seguimiento_${currentSeguimiento}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'credentials': 'include',
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Error al guardar los datos del seguimiento');
    }

    // 2. Enviar imágenes usando el imageUploader
    const imagesToUpload = imageUploader.getImages();

    if (imagesToUpload.length > 0) {

      const formDataImages = new FormData();
      imagesToUpload.forEach((file, index) => {
        formDataImages.append('files', file);
        console.log(`Añadida imagen ${index + 1}: ${file.name} (${file.size} bytes)`);
      });

      try {
        const uploadResponse = await fetch(`/upload-file/${currentDocId}_${currentasviserId}/${currentSeguimiento}`, {
          method: 'POST',
          credentials: 'include',
          body: formDataImages
        });


        if (!uploadResponse.ok) {
          const uploadError = await uploadResponse.json().catch(() => ({}));
          throw new Error(uploadError.message || 'Error al subir las imágenes');
        }

        const uploadResult = await uploadResponse.json();

        imageUploader.images = [];
        imageUploader.imagesGrid.innerHTML = '';
        // imageUploader.updateUI();

        Swal.fire({
          icon: 'success',
          title: '¡Datos guardados!',
          text: `Seguimiento ${currentSeguimiento} guardado correctamente. Se han subido ${uploadResult.files.length} imágenes.`,
          confirmButtonText: 'Aceptar'
        });

      } catch (uploadError) {
        console.error("Error al subir imágenes:", uploadError);
        Swal.fire({
          icon: 'error',
          title: 'Error con las imágenes',
          text: 'Los datos se guardaron pero hubo un problema subiendo las imágenes: ' + uploadError.message,
          confirmButtonText: 'Aceptar'
        });
      }
    } else {
      console.log("No hay imágenes para subir");
    }

    const result = await response.json();

    // Manejar siguiente seguimiento
    if (result.next_seguimiento) {
      currentSeguimiento = result.next_seguimiento;
      await loadSeguimiento(currentDocId, currentasviserId);
    } else {
      Swal.fire({
        icon: 'success',
        title: '¡Todos los seguimientos completados!',
        text: 'Has completado todos los seguimientos para esta familia.',
        confirmButtonText: 'Ir al dashboard'
      }).then(() => {
        window.location.href = '/dashboard';
      });
    }
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.message || 'Error al guardar los datos del seguimiento',
      confirmButtonText: 'Aceptar'
    });
  }
}

// Funcion para cargar seguimiento de listado
function loadFollowUpList(familyId, adviserId, seguimiento) {
  const followUpList = document.getElementById(familyId);
  const isActive = followUpList.classList.contains('pending');

  if (!isActive) {
    currentDocId = familyId;
    currentasviserId = adviserId;
    currentSeguimiento = seguimiento;
    loadSeguimiento(familyId, adviserId);
  }
}


// Función para recoger los datos del formulario
function collectFormData() {
  // Dimensiones
  const formData = {
    dimensiones: Array.from(document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked')).map(checkbox => checkbox.id),
    fecha: document.getElementById('fecha').value,
    hora: document.getElementById('hora').value,
    objetivo: document.getElementById('objetivo').value,
    aspectos: document.getElementById('aspectos').value,
    avances: document.getElementById('avances').value,
    retos: document.getElementById('retos').value,
    oportunidades: document.getElementById('oportunidades').value,
    compromisos: [],
    participantes: []
  }

  // Recolectar compromisos
  const compromisosElements = document.querySelectorAll('#compromisos .form-group');
  compromisosElements.forEach(compromiso => {
    const inputs = compromiso.querySelectorAll('input, textarea');
    formData.compromisos.push({
      descripcion: inputs[0].value,      // textarea
      fecha_cumplimiento: inputs[1].value, // date
      responsable: inputs[2].value        // text
    });
  });

  // Recolectar participantes
  const participantesElements = document.querySelectorAll('#participantes .form-row');
  participantesElements.forEach(participante => {
    const inputs = participante.querySelectorAll('input');
    formData.participantes.push({
      nombre: inputs[0].value,
      rol: inputs[1].value
    });
  });

  return formData;
}

// Funcion para actualizar el formulario condatos
function updateFormWithData(data) {
  // Dimensiones
  document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(checkbox => {
    checkbox.checked = data.dimensiones.includes(checkbox.id);
  });

  // Información básica
  document.getElementById('fecha').value = data.fecha || '';
  document.getElementById('hora').value = data.hora || '';
  document.getElementById('objetivo').value = data.objetivo || '';
  document.getElementById('aspectos').value = data.aspectos || '';
  document.getElementById('avances').value = data.avances || '';
  document.getElementById('retos').value = data.retos || '';
  document.getElementById('oportunidades').value = data.oportunidades || '';

  // Compromisos
  const compromisoContainer = document.getElementById('compromisos');
  compromisoContainer.innerHTML = ''; // Limpiar compromisos existentes
  data.compromisos.forEach((compromiso, index) => {
    const newCompromiso = document.createElement('div');
    newCompromiso.className = 'form-group';
    newCompromiso.innerHTML = `
          <label>Compromiso ${index + 1}</label>
          <textarea placeholder="Describe el compromiso adquirido...">${compromiso.descripcion}</textarea>
          <input type="date" value="${compromiso.fecha_cumplimiento}" required>
          <input type="text" value="${compromiso.responsable}" placeholder="Responsable del compromiso" required>
      `;
    compromisoContainer.appendChild(newCompromiso);
  });

  // Participantes
  const participanteContainer = document.getElementById('participantes');
  participanteContainer.innerHTML = ''; // Limpiar participantes existentes
  data.participantes.forEach((participante, index) => {
    const newParticipante = document.createElement('div');
    newParticipante.className = 'form-row';
    newParticipante.innerHTML = `
          <div class="form-group">
              <label>Nombre del participante</label>
              <input type="text" value="${participante.nombre}" placeholder="Nombre completo">
          </div>
          <div class="form-group">
              <label>Rol en la familia</label>
              <input type="text" value="${participante.rol}" placeholder="Padre, madre, hijo/a, etc.">
          </div>
      `;
    participanteContainer.appendChild(newParticipante);
  });

  Swal.fire({
    icon: 'success',
    title: 'Datos cargados',
    text: `Seguimiento ${currentSeguimiento} cargado correctamente.`,
    confirmButtonText: 'Aceptar'
  });
}

// Funcion para actualizar el indicador de progreso
function updateProgressIndicator() {
  const indicators = document.querySelectorAll('.progress-step');
  indicators.forEach((step, index) => {
    step.classList.toggle('active', index < currentSeguimiento);
  });

  // Actualizar texto "Paso X de X"
  const progressText = document.querySelectorAll('.progress-indicator span');
  if (progressText.length > 0) {
    progressText[0].textContent = `Paso ${currentSeguimiento} de ${MAX_SEGUIMIENTOS}`;
  }
}

// Funcion para actualizar el titulo del formulario
function updateFormTitle() {
  const titleElement = document.querySelector('.form-subtitle');
  if (titleElement) {
    titleElement.textContent = `Seguimiento ${currentSeguimiento} - Familia ${currentDocId}`;
  }
}

// Funciones para añadir elementos dinamicos
function addCompromiso() {
  const container = document.getElementById('compromisos');
  const count = container.children.length + 1;

  const group = document.createElement('div');
  group.className = 'form-group';
  group.innerHTML = `
      <label>Compromiso ${count}</label>
      <textarea placeholder="Describe el compromiso adquirido..."></textarea>
      <input type="date" placeholder="Fecha de cumplimiento" required>
      <input type="text" placeholder="Responsable del compromiso" required>
  `;
  container.appendChild(group);
}

function addParticipante() {
  const container = document.getElementById('participantes');

  const row = document.createElement('div');
  row.className = 'form-row';
  row.innerHTML = `
      <div class="form-group">
          <label>Nombre del participante</label>
          <input type="text" placeholder="Nombre completo">
      </div>
      <div class="form-group">
          <label>Rol en la familia</label>
          <input type="text" placeholder="Padre, madre, hijo/a, etc.">
      </div>
  `;
  container.appendChild(row);
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  // Configurar botones
  document.querySelector('.btn-primary').addEventListener('click', saveAndContinue);
  document.querySelector('.btn-secondary').addEventListener('click', goBack);
});

// Función para regresar
function goBack() {
  if (currentSeguimiento > 1) {
    currentSeguimiento--;
    loadSeguimiento(currentDocId, currentasviserId);
  }
}

// Efecto de escritura suave en los textareas
document.querySelectorAll('textarea').forEach(textarea => {
  textarea.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
  });
});