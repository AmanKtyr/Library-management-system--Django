// Enhanced Signup Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize elements
  const form = document.getElementById('signupForm');
  const emailInput = document.getElementById('id_email');
  const firstNameInput = document.getElementById('id_first_name');
  const lastNameInput = document.getElementById('id_last_name');
  const phoneInput = document.getElementById('id_phone_number');
  const addressInput = document.getElementById('id_address');
  const libraryInput = document.getElementById('id_library');
  const password1Input = document.getElementById('id_password1');
  const password2Input = document.getElementById('id_password2');

  const emailFeedback = document.getElementById('email-feedback');
  const firstNameFeedback = document.getElementById('first-name-feedback');
  const lastNameFeedback = document.getElementById('last-name-feedback');
  const libraryFeedback = document.getElementById('library-feedback');
  const password1Feedback = document.getElementById('password1-feedback');
  const password2Feedback = document.getElementById('password2-feedback');

  const passwordStrengthMeter = document.getElementById('password-strength-meter');
  const passwordStrengthText = document.getElementById('password-strength-text');
  const passwordStrengthContainer = document.getElementById('password-strength-container');

  // Create floating particles
  createParticles();

  // Add input animations
  addInputAnimations();

  // Initialize library cards if they exist
  initLibraryCards();

  // Email validation with improved feedback
  emailInput.addEventListener('input', function() {
    validateEmail(this, emailFeedback);
  });

  // First name validation
  firstNameInput.addEventListener('input', function() {
    validateName(this, firstNameFeedback, 'First name');
  });

  // Last name validation
  lastNameInput.addEventListener('input', function() {
    validateName(this, lastNameFeedback, 'Last name');
  });

  // Phone validation (optional)
  if (phoneInput) {
    phoneInput.addEventListener('input', function() {
      formatPhoneNumber(this);
    });
  }

  // Library validation
  if (libraryInput) {
    libraryInput.addEventListener('change', function() {
      validateLibrary(this, libraryFeedback);
    });
  }

  // Password validation with strength meter
  if (password1Input && passwordStrengthContainer) {
    password1Input.addEventListener('input', function() {
      validatePassword(this, password1Feedback);
      updatePasswordStrength(this.value);

      // Check password confirmation match if both have values
      if (password2Input.value) {
        validatePasswordMatch(password1Input, password2Input, password2Feedback);
      }
    });
  } else if (password1Input) {
    password1Input.addEventListener('input', function() {
      validatePassword(this, password1Feedback);

      // Check password confirmation match if both have values
      if (password2Input.value) {
        validatePasswordMatch(password1Input, password2Input, password2Feedback);
      }
    });
  }

  // Password confirmation validation
  password2Input.addEventListener('input', function() {
    validatePasswordMatch(password1Input, password2Input, password2Feedback);
  });

  // Form submission validation
  form.addEventListener('submit', function(event) {
    let isValid = true;

    // Validate all fields
    if (!validateEmail(emailInput, emailFeedback)) isValid = false;
    if (!validateName(firstNameInput, firstNameFeedback, 'First name')) isValid = false;
    if (!validateName(lastNameInput, lastNameFeedback, 'Last name')) isValid = false;
    if (libraryInput && !validateLibrary(libraryInput, libraryFeedback)) isValid = false;
    if (!validatePassword(password1Input, password1Feedback)) isValid = false;
    if (!validatePasswordMatch(password1Input, password2Input, password2Feedback)) isValid = false;

    if (!isValid) {
      event.preventDefault();

      // Find the first error
      const firstError = document.querySelector('.signup-validation-feedback:not(:empty)');
      if (firstError) {
        // Find the column containing the error
        const errorColumn = firstError.closest('.signup-form-column');
        if (errorColumn) {
          // On mobile, scroll to the error
          if (window.innerWidth <= 1200) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else {
            // On desktop, add a highlight effect to the column
            errorColumn.classList.add('column-with-error');
            setTimeout(() => {
              errorColumn.classList.remove('column-with-error');
            }, 2000);
          }
        } else {
          // Fallback if column not found
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }

      // Shake the submit button to indicate error
      const submitButton = document.querySelector('.signup-button');
      if (submitButton) {
        submitButton.classList.add('shake-animation');
        setTimeout(() => {
          submitButton.classList.remove('shake-animation');
        }, 500);
      }
    } else {
      // Add loading state to button
      const submitButton = document.querySelector('.signup-button');
      if (submitButton) {
        const buttonText = submitButton.querySelector('.signup-button-text');
        const buttonIcon = submitButton.querySelector('.signup-button-icon');

        if (buttonText) buttonText.textContent = 'Processing...';
        if (buttonIcon) buttonIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        submitButton.disabled = true;
      }
    }
  });

  // Close message notifications
  const closeButtons = document.querySelectorAll('.signup-message-close');
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const message = this.closest('.signup-message');
      message.style.opacity = '0';
      setTimeout(() => {
        message.style.display = 'none';
      }, 300);
    });
  });

  // Toggle password visibility
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');
  togglePasswordButtons.forEach(button => {
    button.addEventListener('click', function() {
      const input = document.getElementById(this.getAttribute('data-target'));
      const icon = this.querySelector('i');

      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
  });
});

// Create animated background particles
function createParticles() {
  const container = document.querySelector('.signup-particles');
  if (!container) return;

  const particleCount = 8;

  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.classList.add('signup-particle');

    // Random size
    const size = Math.floor(Math.random() * 6) + 3;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;

    // Random position
    particle.style.top = `${Math.random() * 100}%`;
    particle.style.left = `${Math.random() * 100}%`;

    // Random animation
    particle.style.animationDuration = `${Math.random() * 15 + 10}s`;
    particle.style.animationDelay = `${Math.random() * 5}s`;

    container.appendChild(particle);
  }
}

// Add animations to input fields
function addInputAnimations() {
  const inputs = document.querySelectorAll('.signup-input');

  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.classList.add('input-focus-animation');
    });

    input.addEventListener('blur', function() {
      this.classList.remove('input-focus-animation');
    });
  });
}

// Initialize library cards if they exist
function initLibraryCards() {
  const libraryCards = document.querySelectorAll('.library-card');
  const libraryInput = document.getElementById('id_library');

  if (libraryCards.length === 0 || !libraryInput) return;

  libraryCards.forEach(card => {
    card.addEventListener('click', function() {
      // Remove selected class from all cards
      libraryCards.forEach(c => c.classList.remove('selected'));

      // Add selected class to clicked card
      this.classList.add('selected');

      // Update hidden input value
      libraryInput.value = this.getAttribute('data-library-id');

      // Trigger change event to validate
      const event = new Event('change');
      libraryInput.dispatchEvent(event);
    });
  });
}

// Email validation
function validateEmail(input, feedback) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!input.value) {
    feedback.textContent = 'Email is required';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else if (!emailRegex.test(input.value)) {
    feedback.textContent = 'Please enter a valid email address';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else {
    feedback.textContent = '';
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    return true;
  }
}

// Name validation
function validateName(input, feedback, fieldName) {
  if (!input.value) {
    feedback.textContent = `${fieldName} is required`;
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else if (input.value.length < 2) {
    feedback.textContent = `${fieldName} must be at least 2 characters`;
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else {
    feedback.textContent = '';
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    return true;
  }
}

// Format phone number as user types
function formatPhoneNumber(input) {
  // Remove all non-digits
  let value = input.value.replace(/\D/g, '');

  // Format the number as (XXX) XXX-XXXX
  if (value.length > 0) {
    if (value.length <= 3) {
      value = value;
    } else if (value.length <= 6) {
      value = `${value.slice(0, 3)}-${value.slice(3)}`;
    } else {
      value = `${value.slice(0, 3)}-${value.slice(3, 6)}-${value.slice(6, 10)}`;
    }
  }

  // Update the input value
  input.value = value;
}

// Library validation
function validateLibrary(input, feedback) {
  if (!input.value) {
    feedback.textContent = 'Please select a library';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else {
    feedback.textContent = '';
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    return true;
  }
}

// Password validation
function validatePassword(input, feedback) {
  if (!input.value) {
    feedback.textContent = 'Password is required';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else if (input.value.length < 8) {
    feedback.textContent = 'Password must be at least 8 characters long';
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    return false;
  } else {
    feedback.textContent = '';
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    return true;
  }
}

// Password match validation
function validatePasswordMatch(password1, password2, feedback) {
  if (!password2.value) {
    feedback.textContent = 'Password confirmation is required';
    password2.classList.add('is-invalid');
    password2.classList.remove('is-valid');
    return false;
  } else if (password1.value !== password2.value) {
    feedback.textContent = 'Passwords do not match';
    password2.classList.add('is-invalid');
    password2.classList.remove('is-valid');
    return false;
  } else {
    feedback.textContent = '';
    password2.classList.remove('is-invalid');
    password2.classList.add('is-valid');
    return true;
  }
}

// Update password strength meter
function updatePasswordStrength(password) {
  const strengthMeter = document.getElementById('password-strength-meter');
  const strengthText = document.getElementById('password-strength-text');
  const strengthContainer = document.getElementById('password-strength-container');

  if (!strengthMeter || !strengthText || !strengthContainer) return;

  // Remove all classes
  strengthContainer.classList.remove('password-strength-weak', 'password-strength-fair', 'password-strength-good', 'password-strength-strong');

  if (!password) {
    strengthMeter.style.width = '0';
    strengthText.textContent = '';
    return;
  }

  // Calculate password strength
  let strength = 0;

  // Length check
  if (password.length >= 8) strength += 1;
  if (password.length >= 12) strength += 1;

  // Character type checks
  if (/[A-Z]/.test(password)) strength += 1;
  if (/[a-z]/.test(password)) strength += 1;
  if (/[0-9]/.test(password)) strength += 1;
  if (/[^A-Za-z0-9]/.test(password)) strength += 1;

  // Update UI based on strength
  if (strength <= 2) {
    strengthContainer.classList.add('password-strength-weak');
    strengthText.textContent = 'Weak';
  } else if (strength <= 4) {
    strengthContainer.classList.add('password-strength-fair');
    strengthText.textContent = 'Fair';
  } else if (strength <= 5) {
    strengthContainer.classList.add('password-strength-good');
    strengthText.textContent = 'Good';
  } else {
    strengthContainer.classList.add('password-strength-strong');
    strengthText.textContent = 'Strong';
  }
}
