async function exportToPDF(button) {
	try {
		console.log('Iniciando generación de PDF...');

		// 1. Obtener el elemento a convertir
		const seguimientoDiv = button.closest('.seguimiento');
		if (!seguimientoDiv) {
			console.error('No se encontró el div de seguimiento');
			return;
		}

		// 2. Clonar el elemento
		const element = seguimientoDiv.cloneNode(true);
		console.log('Elemento clonado:', element);

		// 3. Preparar el contenido para PDF
		prepareForPDF(element);
		console.log('Contenido preparado para PDF');

		// 4. Configuración de html2pdf
		const opt = {
			margin: 10,
			filename: `Seguimiento_${seguimientoDiv
				.querySelector('h2')
				.textContent.trim()
				.replace('Seguimiento ', '')}.pdf`,
			image: { type: 'jpeg', quality: 0.98 },
			html2canvas: {
				scale: 2,
				scrollY: 0,
				windowWidth: 1200,
				width: 1200,
				logging: true,
				useCORS: true,
			},
			jsPDF: {
				unit: 'mm',
				format: 'a4',
				orientation: 'portrait',
			},
		};
		console.log('Opciones configuradas:', opt);

		// 5. Crear contenedor temporal
		const tempContainer = document.createElement('div');
		tempContainer.style.position = 'fixed';
		tempContainer.style.left = '-9999px';
		tempContainer.style.width = '800px';
		tempContainer.appendChild(element);
		document.body.appendChild(tempContainer);
		console.log('Contenedor temporal creado');

		// 6. Generar PDF
		console.log('Iniciando generación del PDF...');
		await html2pdf().set(opt).from(element).save();
		console.log('PDF generado con éxito');

		// 7. Limpiar
		document.body.removeChild(tempContainer);
		console.log('Contenedor temporal eliminado');
	} catch (error) {
		console.error('Error al generar PDF:', error);
		alert(
			'Ocurrió un error al generar el PDF. Por favor verifica la consola para más detalles.'
		);
	}
}

function prepareForPDF(element) {
	// Asegurar que el elemento sea visible para html2canvas
	element.style.opacity = '1';
	element.style.visibility = 'visible';
	element.style.display = 'block';
	element.style.width = '100%';
	element.style.padding = '20px';
	element.style.boxSizing = 'border-box';
	element.style.backgroundColor = '#fff';

	// Ocultar elementos no deseados
	element
		.querySelectorAll('button, input[type="file"]')
		.forEach((el) => el.remove());

	// Procesar checkboxes de dimensiones
	const dimensionesContainer = element.querySelector('.filter-options');
	if (dimensionesContainer) {
		let html =
			'<ul style="list-style-type: none; padding-left: 0; margin: 10px 0;">';
		dimensionesContainer
			.querySelectorAll('input[type="checkbox"]')
			.forEach((checkbox) => {
				if (checkbox.checked) {
					const label =
						checkbox.nextElementSibling.textContent.trim();
					html += `<li>✓ ${label}</li>`;
				}
			});
		html += '</ul>';
		dimensionesContainer.innerHTML = html;
	}

	// Convertir inputs a texto
	element
		.querySelectorAll('input:not([type="checkbox"]), textarea')
		.forEach((input) => {
			const span = document.createElement('span');
			span.textContent = input.value || '';
			span.style.display = 'inline-block';
			span.style.margin = '2px 0';
			span.style.padding = '2px 5px';
			span.style.width = '100%';
			input.parentNode.replaceChild(span, input);
		});

	// Ajustar estilos de compromisos y participantes
	element
		.querySelectorAll('.compromiso-row, .participante-row')
		.forEach((row) => {
			row.style.display = 'flex';
			row.style.flexWrap = 'wrap';
			row.style.gap = '10px';
			row.style.marginBottom = '10px';
		});
}

// Validación antes de enviar el formulario
document.querySelectorAll('form[id^="form-seguimiento-"]').forEach((form) => {
	form.addEventListener('submit', function (e) {
		// Validar que al menos una dimensión esté seleccionada
		const checkboxes = this.querySelectorAll(
			'input[name="dimensiones"]:checked'
		);
		if (checkboxes.length === 0) {
			alert('Por favor seleccione al menos una dimensión a intervenir');
			e.preventDefault();
			return false;
		}
		return true;
	});
});

document.getElementById('generarPDF').addEventListener('click', function (e) {
	if (this.classList.contains('disabled')) {
		e.preventDefault();
		alert('Por favor, complete el formulario antes de generar el PDF.');
		return;
	}
	exportToPDF(this);
}
);
