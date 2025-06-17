// Referencias a elementos
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');
const loginForm = document.getElementById('loginForm');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const usernameSuccess = document.getElementById('usernameSuccess');
const passwordSuccess = document.getElementById('passwordSuccess');

// Toggle para mostrar/ocultar contraseña
togglePassword.addEventListener('click', function () {
  const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
  passwordInput.setAttribute('type', type);
  console.log(this.lastChild.getAttribute('src'));
  this.lastChild.getAttribute('src') === '/seguimientos/static/img/icons/ojo.png' ? this.lastChild.setAttribute('src', '/seguimientos/static/img/icons/cerrar-ojo.png') : this.lastChild.setAttribute('src', '/seguimientos/static/img/icons/ojo.png');
});

// Validación en tiempo real para usuario
// usernameInput.addEventListener('input', function () {
//   const value = this.value.trim();

//   if (value.length === 0) {
//     showError(usernameError, '');
//     hideSuccess(usernameSuccess);
//   } else if (value.length < 3) {
//     showError(usernameError, 'El usuario debe tener al menos 3 caracteres');
//     hideSuccess(usernameSuccess);
//   } else if (value.includes('@') && !isValidEmail(value)) {
//     showError(usernameError, 'Formato de email inválido');
//     hideSuccess(usernameSuccess);
//   } else {
//     hideError(usernameError);
//     showSuccess(usernameSuccess, 'Usuario válido ✓');
//   }
// });

// Validación en tiempo real para contraseña
// passwordInput.addEventListener('input', function () {
//   const value = this.value;

//   if (value.length === 0) {
//     showError(passwordError, '');
//     hideSuccess(passwordSuccess);
//   } else if (value.length < 6) {
//     showError(passwordError, 'La contraseña debe tener al menos 6 caracteres');
//     hideSuccess(passwordSuccess);
//   } else if (!hasUpperCase(value)) {
//     showError(passwordError, 'Debe incluir al menos una mayúscula');
//     hideSuccess(passwordSuccess);
//   } else if (!hasNumber(value)) {
//     showError(passwordError, 'Debe incluir al menos un número');
//     hideSuccess(passwordSuccess);
//   } else {
//     hideError(passwordError);
//     showSuccess(passwordSuccess, 'Contraseña segura ✓');
//   }
// });

// Envío del formulario
loginForm.addEventListener('submit', function (e) {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  if (validateForm(username, password)) {
    async function login() {
      try {
        // Crear los datos en formato URL-encoded
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/seguimientos/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData.toString(),
        });

        if (!response.ok) {
          // Si hay error HTTP, obtener el mensaje del servidor
          const errorText = await response.text();
          throw new Error(errorText || 'Error en la autenticación');
        }

        // Si la respuesta es exitosa (200), redirigir
        window.location.href = '/seguimientos/dashboard';

      } catch (error) {
        showError(usernameError, error.message);
      }
    }

    login();
  } else {
    // Animación de error
    loginForm.classList.add('shake');
    setTimeout(() => loginForm.classList.remove('shake'), 500);
  }
});

// Funciones de utilidad
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function hasUpperCase(str) {
  return /[A-Z]/.test(str);
}

function hasNumber(str) {
  return /\d/.test(str);
}

function showError(element, message) {
  element.textContent = message;
  element.classList.add('show');
}

function hideError(element) {
  element.classList.remove('show');
}

function showSuccess(element, message) {
  element.textContent = message;
  element.classList.add('show');
}

function hideSuccess(element) {
  element.classList.remove('show');
}

function validateForm(username, password) {
  let isValid = true;

  // Validar usuario
  if (username.length < 3) {
    showError(usernameError, 'El usuario debe tener al menos 3 caracteres');
    isValid = false;
  } else if (username.includes('@') && !isValidEmail(username)) {
    showError(usernameError, 'Formato de email inválido');
    isValid = false;
  }

  // Validar contraseña
  if (password.length < 6) {
    showError(passwordError, 'La contraseña debe tener al menos 6 caracteres');
    isValid = false;
  } else if (!hasUpperCase(password)) {
    showError(passwordError, 'Debe incluir al menos una mayúscula');
    isValid = false;
  } else if (!hasNumber(password)) {
    showError(passwordError, 'Debe incluir al menos un número');
    isValid = false;
  }

  return isValid;
}

// Efecto de focus mejorado
document.querySelectorAll('.input-field').forEach(input => {
  input.addEventListener('focus', function () {
    this.parentElement.style.transform = 'scale(1.02)';
  });

  input.addEventListener('blur', function () {
    this.parentElement.style.transform = 'scale(1)';
  });
});