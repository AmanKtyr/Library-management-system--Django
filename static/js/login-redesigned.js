// Redesigned Login Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize RGB variables for theme colors
  const initializeRgbVariables = () => {
    // Convert hex colors to RGB for rgba usage
    const hexToRgb = (hex) => {
      if (!hex) return null;
      const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
      hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null;
    };

    // Get computed styles
    const computedStyle = getComputedStyle(document.documentElement);
    const accentColor = computedStyle.getPropertyValue('--accent-color').trim();
    const buttonColor = computedStyle.getPropertyValue('--button-color').trim();
    const backgroundColor = computedStyle.getPropertyValue('--background-color').trim();

    // Set default colors if not available
    const accentRgb = hexToRgb(accentColor) || {r: 79, g: 70, b: 229}; // Default accent color
    const buttonRgb = hexToRgb(buttonColor) || {r: 46, g: 139, b: 87}; // Default button color
    const backgroundRgb = hexToRgb(backgroundColor) || {r: 249, g: 249, b: 249}; // Default background color
    const successRgb = {r: 16, g: 185, b: 129}; // Default success color
    const warningRgb = {r: 245, g: 158, b: 11}; // Default warning color

    // Set RGB variables
    document.documentElement.style.setProperty('--accent-color-rgb', `${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}`);
    document.documentElement.style.setProperty('--button-color-rgb', `${buttonRgb.r}, ${buttonRgb.g}, ${buttonRgb.b}`);
    document.documentElement.style.setProperty('--background-color-rgb', `${backgroundRgb.r}, ${backgroundRgb.g}, ${backgroundRgb.b}`);
    document.documentElement.style.setProperty('--success-color-rgb', `${successRgb.r}, ${successRgb.g}, ${successRgb.b}`);
    document.documentElement.style.setProperty('--warning-color-rgb', `${warningRgb.r}, ${warningRgb.g}, ${warningRgb.b}`);
  };

  // Initialize RGB variables
  initializeRgbVariables();

  // Initialize branding section gradient
  const initializeBrandingGradient = () => {
    // Create a custom style element for the pseudo-element
    let styleElement = document.getElementById('brandGradientStyle');
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = 'brandGradientStyle';
      document.head.appendChild(styleElement);
    }

    // Update the style for the pseudo-element
    styleElement.textContent = `
      .login-brand::before {
        background: linear-gradient(135deg,
          rgba(var(--accent-color-rgb), 0.9) 0%,
          rgba(var(--button-color-rgb), 0.8) 100%) !important;
      }
    `;
  };

  // Initialize branding gradient
  initializeBrandingGradient();

  // Animate background particles
  const particles = document.querySelectorAll('.login-particle');
  particles.forEach((particle, index) => {
    // Set random initial positions
    const randomX = Math.random() * 100;
    const randomY = Math.random() * 100;
    particle.style.left = `${randomX}%`;
    particle.style.top = `${randomY}%`;

    // Set random sizes
    const randomSize = Math.random() * 15 + 5; // 5-20px
    particle.style.width = `${randomSize}px`;
    particle.style.height = `${randomSize}px`;

    // Set random opacity
    const randomOpacity = Math.random() * 0.15 + 0.05; // 0.05-0.2
    particle.style.opacity = randomOpacity;

    // Set random animation duration
    const randomDuration = Math.random() * 20 + 10; // 10-30s
    particle.style.animationDuration = `${randomDuration}s`;

    // Set random animation delay
    const randomDelay = Math.random() * 5; // 0-5s
    particle.style.animationDelay = `${randomDelay}s`;
  });
  // Password toggle functionality
  const togglePassword = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('id_password');

  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function() {
      // Toggle password visibility
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);

      // Toggle icon
      this.querySelector('i').classList.toggle('fa-eye');
      this.querySelector('i').classList.toggle('fa-eye-slash');
    });
  }

  // Role selector functionality
  const roleInputs = document.querySelectorAll('.role-selector-input');
  const emailInput = document.getElementById('id_login');
  const passwordInput = document.getElementById('id_password');
  const userRoleInput = document.getElementById('user_role');
  const roleLabels = document.querySelectorAll('.role-selector-label');
  const loginButton = document.getElementById('loginButton');

  // Sample emails for demonstration
  const roleEmails = {
    'member': 'member@library.com',
    'staff': 'staff@library.com',
    'library-admin': 'libraryadmin@library.com',
    'super-admin': 'superadmin@library.com'
  };

  // Role descriptions for dynamic title updates
  const roleTitles = {
    'member': {
      buttonText: 'Sign in as Member',
      formClass: 'member-form'
    },
    'staff': {
      buttonText: 'Sign in as Staff',
      formClass: 'staff-form'
    },
    'library-admin': {
      buttonText: 'Sign in as Library Admin',
      formClass: 'library-admin-form'
    },
    'super-admin': {
      buttonText: 'Sign in as Super Admin',
      formClass: 'super-admin-form'
    }
  };

  // Function to update UI based on selected role
  function updateUIForRole(roleId) {
    if (!roleTitles[roleId]) return;

    // Update button text
    if (loginButton) {
      const buttonTextElement = loginButton.querySelector('.login-button-text');
      if (buttonTextElement) {
        buttonTextElement.textContent = roleTitles[roleId].buttonText;
      }
    }

    // Update form class for styling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      // Remove all role-specific classes
      Object.values(roleTitles).forEach(role => {
        if (role.formClass) {
          loginForm.classList.remove(role.formClass);
        }
      });

      // Add the current role class
      loginForm.classList.add(roleTitles[roleId].formClass);
    }

    // Update placeholder text in email field
    if (emailInput && roleEmails[roleId]) {
      emailInput.placeholder = `Email (e.g., ${roleEmails[roleId]})`;
    }
  }

  // Initialize with the default selected role
  const initialSelectedRole = document.querySelector('.role-selector-input:checked');
  if (initialSelectedRole) {
    const roleId = initialSelectedRole.id;
    updateUIForRole(roleId);

    // Set initial user role value
    if (userRoleInput) {
      if (roleId === 'member') {
        userRoleInput.value = 'member';
      } else if (roleId === 'staff') {
        userRoleInput.value = 'staff';
      } else if (roleId === 'library-admin') {
        userRoleInput.value = 'library_admin';
      } else if (roleId === 'super-admin') {
        userRoleInput.value = 'super_admin';
      }
    }
  }

  // Add event listeners to role inputs
  roleInputs.forEach(input => {
    input.addEventListener('change', function() {
      if (this.checked) {
        const roleId = this.id;

        // Update the hidden user_role field based on selected role
        if (userRoleInput) {
          if (roleId === 'member') {
            userRoleInput.value = 'member';
          } else if (roleId === 'staff') {
            userRoleInput.value = 'staff';
          } else if (roleId === 'library-admin') {
            userRoleInput.value = 'library_admin';
          } else if (roleId === 'super-admin') {
            userRoleInput.value = 'super_admin';
          }
        }

        // Update UI elements for the selected role
        updateUIForRole(roleId);

        // Add highlight animation to input fields
        if (emailInput) {
          emailInput.classList.add('login-input-highlight');
          setTimeout(() => {
            emailInput.classList.remove('login-input-highlight');
          }, 1000);
        }

        if (passwordInput) {
          setTimeout(() => {
            passwordInput.classList.add('login-input-highlight');
            setTimeout(() => {
              passwordInput.classList.remove('login-input-highlight');
            }, 1000);
          }, 200); // Slight delay for sequential animation
        }

        // Add a subtle animation to the selected label
        const label = this.nextElementSibling;
        if (label) {
          // Remove selected class from all labels first
          roleLabels.forEach(l => l.classList.remove('role-selector-label-selected'));

          // Add selected class to current label
          label.classList.add('role-selector-label-selected');
        }
      }
    });
  });

  // Message close functionality
  const messageCloseButtons = document.querySelectorAll('.login-message-close');
  messageCloseButtons.forEach(button => {
    button.addEventListener('click', function() {
      const message = this.closest('.login-message');
      if (message) {
        message.style.opacity = '0';
        setTimeout(() => {
          message.style.display = 'none';
        }, 300);
      }
    });
  });

  // Add focus effects to input fields
  const inputFields = document.querySelectorAll('.login-input');
  inputFields.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('login-input-wrapper-focus');
    });

    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('login-input-wrapper-focus');
    });
  });

  // Form validation
  const loginForm = document.getElementById('loginForm');
  const emailFeedback = document.getElementById('email-feedback');
  const passwordFeedback = document.getElementById('password-feedback');

  if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
      let isValid = true;

      // Validate email
      if (emailInput) {
        const emailValue = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailValue) {
          isValid = false;
          emailInput.classList.add('is-invalid');
          if (emailFeedback) {
            emailFeedback.textContent = 'Email address is required';
          }
        } else if (!emailRegex.test(emailValue)) {
          isValid = false;
          emailInput.classList.add('is-invalid');
          if (emailFeedback) {
            emailFeedback.textContent = 'Please enter a valid email address';
          }
        } else {
          emailInput.classList.remove('is-invalid');
          if (emailFeedback) {
            emailFeedback.textContent = '';
          }
        }
      }

      // Validate password
      if (passwordInput) {
        const passwordValue = passwordInput.value;

        if (!passwordValue) {
          isValid = false;
          passwordInput.classList.add('is-invalid');
          if (passwordFeedback) {
            passwordFeedback.textContent = 'Password is required';
          }
        } else {
          passwordInput.classList.remove('is-invalid');
          if (passwordFeedback) {
            passwordFeedback.textContent = '';
          }
        }
      }

      if (!isValid) {
        event.preventDefault();

        // Find the first error
        const firstError = document.querySelector('.login-validation-feedback:not(:empty)');
        if (firstError) {
          // Find the column containing the error
          const errorColumn = firstError.closest('.login-form-column');
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
      } else {
        // Show loading state on button
        if (loginButton) {
          loginButton.disabled = true;
          const buttonText = loginButton.querySelector('.login-button-text');
          const buttonIcon = loginButton.querySelector('.login-button-icon');

          if (buttonText) buttonText.textContent = 'Signing In...';
          if (buttonIcon) buttonIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
      }
    });

    // Real-time validation
    if (emailInput) {
      emailInput.addEventListener('input', function() {
        const emailValue = this.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (emailValue && emailRegex.test(emailValue)) {
          this.classList.remove('is-invalid');
          if (emailFeedback) {
            emailFeedback.textContent = '';
          }
        }
      });
    }

    if (passwordInput) {
      passwordInput.addEventListener('input', function() {
        const passwordValue = this.value;

        if (passwordValue) {
          this.classList.remove('is-invalid');
          if (passwordFeedback) {
            passwordFeedback.textContent = '';
          }
        }
      });
    }
  }

  // Add animation to social login buttons
  const socialButtons = document.querySelectorAll('.login-social-button');
  socialButtons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-3px)';
      this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
    });

    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    });
  });

  // Listen for theme changes
  document.addEventListener('themeChanged', function(e) {
    // Get the theme details
    const themeKey = e.detail.theme;
    const colors = e.detail.colors;

    // Convert hex colors to RGB for rgba usage
    const hexToRgb = (hex) => {
      const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
      hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null;
    };

    // Set RGB variables for rgba usage
    const accentRgb = hexToRgb(colors.accent);
    const buttonRgb = hexToRgb(colors.button);
    const successRgb = hexToRgb('#10b981'); // Default success color
    const warningRgb = hexToRgb('#f59e0b'); // Default warning color

    if (accentRgb) {
      document.documentElement.style.setProperty('--accent-color-rgb', `${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}`);
    }

    if (buttonRgb) {
      document.documentElement.style.setProperty('--button-color-rgb', `${buttonRgb.r}, ${buttonRgb.g}, ${buttonRgb.b}`);
    }

    if (successRgb) {
      document.documentElement.style.setProperty('--success-color-rgb', `${successRgb.r}, ${successRgb.g}, ${successRgb.b}`);
    }

    if (warningRgb) {
      document.documentElement.style.setProperty('--warning-color-rgb', `${warningRgb.r}, ${warningRgb.g}, ${warningRgb.b}`);
    }

    // Set background color RGB
    const backgroundRgb = hexToRgb(colors.background);
    if (backgroundRgb) {
      document.documentElement.style.setProperty('--background-color-rgb', `${backgroundRgb.r}, ${backgroundRgb.g}, ${backgroundRgb.b}`);
    }

    // Update login card background particles for dark themes
    if (themeKey === 'elegant-dark') {
      document.querySelectorAll('.login-bg-circle').forEach(circle => {
        circle.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
      });

      document.querySelectorAll('.login-particle').forEach(particle => {
        particle.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
      });

      // Update text color in branding section for dark theme
      const brandingContent = document.querySelector('.login-brand-content');
      if (brandingContent) {
        brandingContent.style.color = 'white';
      }

      // Update feature text color
      document.querySelectorAll('.login-feature-text h3, .login-feature-text p').forEach(el => {
        el.style.color = 'rgba(255, 255, 255, 0.9)';
      });
    } else {
      document.querySelectorAll('.login-bg-circle').forEach(circle => {
        circle.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
      });

      document.querySelectorAll('.login-particle').forEach(particle => {
        particle.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
      });

      // Update text color in branding section for light theme
      const brandingContent = document.querySelector('.login-brand-content');
      if (brandingContent) {
        brandingContent.style.color = 'white';
      }

      // Update feature text color
      document.querySelectorAll('.login-feature-text h3').forEach(el => {
        el.style.color = 'white';
      });

      document.querySelectorAll('.login-feature-text p').forEach(el => {
        el.style.color = 'rgba(255, 255, 255, 0.8)';
      });
    }

    // Update the branding section gradient based on theme colors
    const loginBrand = document.getElementById('loginBrand');
    if (loginBrand) {
      // Create a custom style element for the pseudo-element
      let styleElement = document.getElementById('brandGradientStyle');
      if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'brandGradientStyle';
        document.head.appendChild(styleElement);
      }

      // Update the style for the pseudo-element
      styleElement.textContent = `
        .login-brand::before {
          background: linear-gradient(135deg,
            rgba(var(--accent-color-rgb), 0.9) 0%,
            rgba(var(--button-color-rgb), 0.8) 100%) !important;
        }
      `;
    }
  });

  // Add subtle hover effect to the login card
  const loginCard = document.querySelector('.login-card');
  if (loginCard) {
    loginCard.addEventListener('mousemove', function(e) {
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left; // x position within the element
      const y = e.clientY - rect.top;  // y position within the element

      // Calculate rotation based on mouse position (limited to 2 degrees)
      const rotateY = ((x / rect.width) - 0.5) * 2;
      const rotateX = ((y / rect.height) - 0.5) * -2;

      // Apply the transform
      this.style.transform = `perspective(1500px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

      // Add parallax effect to background circles
      const circles = document.querySelectorAll('.login-bg-circle');
      circles.forEach((circle, index) => {
        const factor = (index + 1) * 0.03;
        const translateX = rotateY * 20 * factor;
        const translateY = rotateX * -20 * factor;
        circle.style.transform = `translate(${translateX}px, ${translateY}px)`;
      });
    });

    // Reset transform when mouse leaves
    loginCard.addEventListener('mouseleave', function() {
      this.style.transform = 'perspective(1500px) rotateX(0) rotateY(0)';

      // Reset background circles
      const circles = document.querySelectorAll('.login-bg-circle');
      circles.forEach(circle => {
        circle.style.transform = 'translate(0, 0)';
      });
    });
  }
});
