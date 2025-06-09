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
      loadSeguimiento(familyId, adviser); // Cargar
  }
}

// async function createNewFamily() {
//   const { value: familyId } = await Swal.fire({
//       title: 'Nueva Familia',
//       input: 'text',
//       inputLabel: 'Número de documento del cabeza de familia',
//       inputPlaceholder: 'Ingrese el número de documento',
//       showCancelButton: true,
//       confirmButtonText: 'Crear Familia',
//       cancelButtonText: 'Cancelar',
//       inputValidator: (value) => {
//           if (!value) {
//               return 'Debe ingresar un número de documento'
//           }
//       }
//   });

//   if (familyId) {
//       try {
//           // Mostrar loading
//           Swal.fire({
//               title: 'Creando familia...',
//               allowOutsideClick: false,
//               didOpen: () => {
//                   Swal.showLoading();
//               }
//           });

//           const response = await fetch('/create-document', {
//               method: 'POST',
//               headers: {
//                   'Content-Type': 'application/json',
//                   'credentials': 'include',
//               },
//               body: JSON.stringify({
//                   doc_number: familyId
//               })
//           });

//           const data = await response.json();

//           if (response.ok && data.success) {
//               const result = await Swal.fire({
//                   icon: 'success',
//                   title: '¡Éxito!',
//                   text: `Nueva familia con documento ${familyId} creada exitosamente`,
//                   showCancelButton: true,
//                 //   confirmButtonText: 'Ir al documento',
//                   cancelButtonText: 'Continuar'
//               });

//               // Si el usuario quiere ir al documento, redirigir
//               if (result.isConfirmed && data.redirect_url) {
//                   window.location.href = data.redirect_url;
//               }
//           } else {
//               throw new Error(data.detail || data.message || 'Error al crear la familia');
//           }

//       } catch (error) {
//           Swal.fire({
//               icon: 'error',
//               title: 'Error',
//               text: error.message || 'Ocurrió un error al crear la familia',
//               confirmButtonText: 'Aceptar'
//           });
//       }
//   }
// }

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


// Funcion para gurdar y continuar
// async function saveAndContinue() {
//   // Validar campos requeridos
//   const requiredFields = document.querySelectorAll('input[required], textarea[required]');
//   let allValid = true;
  
//   requiredFields.forEach(field => {
//       if (!field.value.trim()) {
//           field.style.borderColor = '#ef4444';
//           allValid = false;
//       } else {
//           field.style.borderColor = '#e2e8f0';
//       }
//   });
  
//   if (allValid) {
//       try {
//         // Recoger datos del formulario
//         const formData = collectFormData();
  
//         const response = await fetch(`/save-seguimiento/documento_${currentDocId}_${currentasviserId}/seguimiento_${currentSeguimiento}`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'credentials': 'include',
//             },
//             body: JSON.stringify(formData)
//         });
  
//         if (!response.ok) {
//             throw new Error('Error al guardar los datos del seguimiento');
//         }
  
//         const result = await response.json();
  
//         // Avanzar al siguiente seguimiento si existe
//         if (result.next_seguimiento) {
//             currentSeguimiento = result.next_seguimiento;
//             await loadSeguimiento(currentDocId, currentasviserId);
//         } else {
//             Swal.fire({
//                 icon: 'success',
//                 title: '¡Todos los seguimientos completados!',
//                 text: 'Has completado todos los seguimientos para esta familia.',
//                 confirmButtonText: 'Ir al dashboard'
//             }).then(() => {
//                 window.location.href = '/dashboard';
//             });
//         }
//     } catch (error) {
//         Swal.fire({
//             icon: 'error',
//             title: 'Error',
//             text: 'Error al guardar los datos del seguimiento\n' + error,
//             confirmButtonText: 'Aceptar'
//         });
//     }
//       // Aquí iría la lógica para guardar y continuar
//   } else {
//       Swal.fire({
//           icon: 'warning',
//           title: 'Campos incompletos',
//           text: 'Por favor, completa todos los campos requeridos antes de continuar.',
//           confirmButtonText: 'Aceptar'
//       });

//   }
// }

async function saveAndContinue() {
    console.log("Iniciando saveAndContinue...");
    
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
        console.log("Recogiendo datos del formulario...");
        const formData = collectFormData();
        
        // 1. Enviar datos del formulario
        console.log("Enviando datos principales...");
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
        console.log("Verificando imágenes...");
        const imagesToUpload = imageUploader.getImages();
        console.log("Imágenes a subir:", imagesToUpload);
        
        if (imagesToUpload.length > 0) {
            console.log(`Preparando ${imagesToUpload.length} imágenes para subir...`);
            
            const formDataImages = new FormData();
            imagesToUpload.forEach((file, index) => {
                formDataImages.append('files', file);
                console.log(`Añadida imagen ${index + 1}: ${file.name} (${file.size} bytes)`);
            });

            console.log("Enviando imágenes al servidor...");
            try {
                const uploadResponse = await fetch(`/upload-file/${currentDocId}_${currentasviserId}/${currentSeguimiento}`, {
                    method: 'POST',
                    credentials: 'include',
                    body: formDataImages
                });

                console.log("Respuesta del servidor (status):", uploadResponse.status);
                
                if (!uploadResponse.ok) {
                    const uploadError = await uploadResponse.json().catch(() => ({}));
                    throw new Error(uploadError.message || 'Error al subir las imágenes');
                }

                const uploadResult = await uploadResponse.json();
                console.log('Resultado de subida de imágenes:', uploadResult);
                
                // Mostrar feedback al usuario
                Swal.fire({
                    icon: 'success',
                    title: '¡Imágenes subidas!',
                    text: `Se han subido ${uploadResult.files.length} imágenes correctamente.`,
                    confirmButtonText: 'Aceptar'
                });
                
                // Limpiar las imágenes después de subirlas (opcional)
                //   imageUploader.clearAllImages();
                // Por esto (solo limpia la lista interna sin mostrar confirmación):
                    imageUploader.images = [];
                    imageUploader.imagesGrid.innerHTML = '';
                    imageUploader.updateUI();

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
        console.log("Resultado del guardado:", result);

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
        console.error("Error en saveAndContinue:", error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Error al guardar los datos del seguimiento',
            confirmButtonText: 'Aceptar'
        });
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
  // Obtener doc_id de la URL o de algún elemento
  // const urlParams = new URLSearchParams(window.location.search);
  // currentDocId = urlParams.get('doc_id') || '1001456000'; // Ejemplo por defecto
  
  // // Obtener seguimiento actual (si viene en la URL)
  // const seguimientoParam = urlParams.get('seguimiento');
  // currentSeguimiento = seguimientoParam ? parseInt(seguimientoParam) : 1;
  
  // Configurar botones
  document.querySelector('.btn-primary').addEventListener('click', saveAndContinue);
  document.querySelector('.btn-secondary').addEventListener('click', goBack);
  
  // Cargar datos iniciales
  // loadSeguimiento();
});

// Función para regresar
function goBack() {
  if (currentSeguimiento > 1) {
      currentSeguimiento--;
      console.log(currentDocId, currentasviserId, currentSeguimiento)
      loadSeguimiento(currentDocId, currentasviserId);

  } else {
      window.location.href = '/documentos';
  }
}

// Efecto de escritura suave en los textareas
document.querySelectorAll('textarea').forEach(textarea => {
  textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = this.scrollHeight + 'px';
  });
});

// let compromisoCount = 1;
// function addCompromiso() {
//   compromisoCount++;
//   const container = document.getElementById('compromisos');
//   const newCompromiso = document.createElement('div');
//   newCompromiso.className = 'form-group';
//   newCompromiso.innerHTML = `
//       <label>Compromiso ${compromisoCount}</label>
//       <textarea placeholder="Describe el compromiso adquirido..."></textarea>
//       <input type="date" placeholder="Fecha de cumplimiento" required>
//       <input type="text" placeholder="Responsable del compromiso" required>
//   `;
//   container.appendChild(newCompromiso);
// }

// let participanteCount = 1;
// function addParticipante() {
//   participanteCount++;
//   const container = document.getElementById('participantes');
//   const newParticipante = document.createElement('div');
//   newParticipante.className = 'form-row';
//   newParticipante.innerHTML = `
//       <div class="form-group">
//           <label>Nombre del participante</label>
//           <input type="text" placeholder="Nombre completo">
//       </div>
//       <div class="form-group">
//           <label>Rol en la familia</label>
//           <input type="text" placeholder="Padre, madre, hijo/a, etc.">
//       </div>
//   `;
//   container.appendChild(newParticipante);
// }

// function goBack() {
//   if (confirm('¿Estás seguro de que deseas regresar? Los cambios no guardados se perderán.')) {
//       window.history.back();
//   }
// }