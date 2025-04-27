// Modern and Professional Login Card JavaScript

document.addEventListener('DOMContentLoaded', function() {
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

  // Role selector functionality - Enhanced Design
  const roleInputs = document.querySelectorAll('.role-selector-input');
  const emailInput = document.getElementById('id_login');
  const passwordInput = document.getElementById('id_password');
  const userRoleInput = document.getElementById('user_role');
  const roleLabels = document.querySelectorAll('.role-selector-label');
  const roleTitle = document.querySelector('.role-selector-title h3');
  const roleSubtitle = document.querySelector('.role-selector-title p');
  const loginForm = document.getElementById('loginForm');
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
      title: 'Sign in as Member',
      subtitle: 'Access your library account and manage your books',
      buttonText: 'Sign in as Member',
      formClass: 'member-form'
    },
    'staff': {
      title: 'Sign in as Staff',
      subtitle: 'Access library operations and assist members',
      buttonText: 'Sign in as Staff',
      formClass: 'staff-form'
    },
    'library-admin': {
      title: 'Sign in as Library Admin',
      subtitle: 'Manage your library and staff accounts',
      buttonText: 'Sign in as Library Admin',
      formClass: 'library-admin-form'
    },
    'super-admin': {
      title: 'Sign in as Super Admin',
      subtitle: 'Manage all libraries in the system',
      buttonText: 'Sign in as Super Admin',
      formClass: 'super-admin-form'
    }
  };

  // Function to update UI based on selected role
  function updateUIForRole(roleId) {
    if (!roleTitles[roleId]) return;

    // Update the title and subtitle with fade effect
    if (roleTitle && roleSubtitle) {
      // Fade out
      roleTitle.style.opacity = 0;
      roleSubtitle.style.opacity = 0;

      // Update text and fade in after a short delay
      setTimeout(() => {
        roleTitle.textContent = roleTitles[roleId].title;
        roleSubtitle.textContent = roleTitles[roleId].subtitle;
        roleTitle.style.opacity = 1;
        roleSubtitle.style.opacity = 1;
      }, 200);
    }

    // Update button text
    if (loginButton) {
      const buttonTextElement = loginButton.querySelector('.login-button-text');
      if (buttonTextElement) {
        buttonTextElement.textContent = roleTitles[roleId].buttonText;
      }
    }

    // Update form class for styling
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

  // Create and add particles to role cards for visual effect
  roleLabels.forEach(label => {
    // Create particles for decoration
    for (let i = 0; i < 3; i++) {
      const particle = document.createElement('span');
      particle.classList.add('role-particle');
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.top = `${Math.random() * 100}%`;
      particle.style.animationDelay = `${Math.random() * 2}s`;
      particle.style.width = `${Math.random() * 6 + 2}px`;
      particle.style.height = particle.style.width;
      label.appendChild(particle);
    }

    // Add hover effects
    label.addEventListener('mouseenter', function() {
      const iconWrapper = this.querySelector('.role-icon-wrapper');
      if (iconWrapper) {
        iconWrapper.style.transform = 'scale(1.1) rotate(5deg)';
      }

      // Animate particles on hover
      const particles = this.querySelectorAll('.role-particle');
      particles.forEach(particle => {
        particle.style.animationDuration = '1s';
      });
    });

    label.addEventListener('mouseleave', function() {
      const iconWrapper = this.querySelector('.role-icon-wrapper');
      if (iconWrapper) {
        iconWrapper.style.transform = '';
      }

      // Reset particle animation
      const particles = this.querySelectorAll('.role-particle');
      particles.forEach(particle => {
        particle.style.animationDuration = '3s';
      });
    });
  });

  // Function to handle role selection
  function selectRole(roleId) {
    const input = document.getElementById(roleId);
    if (input) {
      input.checked = true;

      // Trigger the change event
      const event = new Event('change');
      input.dispatchEvent(event);
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

          // Add a ripple effect
          const ripple = document.createElement('span');
          ripple.classList.add('role-selector-ripple');
          label.appendChild(ripple);

          // Remove the ripple after animation completes
          setTimeout(() => {
            ripple.remove();
          }, 800);

          // Animate particles more intensely on selection
          const particles = label.querySelectorAll('.role-particle');
          particles.forEach(particle => {
            particle.classList.add('role-particle-active');
            setTimeout(() => {
              particle.classList.remove('role-particle-active');
            }, 1000);
          });
        }
      }
    });

    // Add click event to labels for better touch device support
    const label = input.nextElementSibling;
    if (label) {
      label.addEventListener('click', function(e) {
        // Prevent default to avoid double triggering with the label's native behavior
        e.preventDefault();
        input.checked = true;

        // Manually trigger change event
        const event = new Event('change');
        input.dispatchEvent(event);
      });
    }
  });

  // Add keyboard navigation for accessibility
  document.addEventListener('keydown', function(e) {
    // Only handle arrow keys if role selector is in focus
    const roleSelector = document.querySelector('.role-selector-tabs');
    const activeElement = document.activeElement;
    const isRoleSelectorFocused = roleSelector.contains(activeElement) ||
                                 activeElement.classList.contains('role-selector-label') ||
                                 activeElement.classList.contains('role-selector-input');

    if (!isRoleSelectorFocused && e.key !== 'Tab') {
      return;
    }

    const currentRole = document.querySelector('.role-selector-input:checked');
    if (!currentRole) return;

    const roleIds = ['member', 'staff', 'library-admin', 'super-admin'];
    const currentIndex = roleIds.indexOf(currentRole.id);

    if (currentIndex === -1) return;

    let newIndex;

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        newIndex = (currentIndex + 1) % roleIds.length;
        selectRole(roleIds[newIndex]);
        break;

      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        newIndex = (currentIndex - 1 + roleIds.length) % roleIds.length;
        selectRole(roleIds[newIndex]);
        break;

      case '1':
        e.preventDefault();
        selectRole('member');
        break;

      case '2':
        e.preventDefault();
        selectRole('staff');
        break;

      case '3':
        e.preventDefault();
        selectRole('library-admin');
        break;

      case '4':
        e.preventDefault();
        selectRole('super-admin');
        break;
    }
  });

  // Add focus indicators for accessibility
  roleLabels.forEach(label => {
    label.setAttribute('tabindex', '0');

    label.addEventListener('focus', function() {
      this.style.outline = '2px solid rgba(79, 70, 229, 0.5)';
      this.style.outlineOffset = '2px';
    });

    label.addEventListener('blur', function() {
      this.style.outline = 'none';
      this.style.outlineOffset = '0';
    });

    // Handle Enter and Space key presses
    label.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const input = document.getElementById(this.getAttribute('for'));
        if (input) {
          input.checked = true;
          const event = new Event('change');
          input.dispatchEvent(event);
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
        message.classList.add('login-message-hiding');
        setTimeout(() => {
          message.remove();
        }, 300);
      }
    });
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

  // Add button press effect
  const loginButton = document.querySelector('.login-button');
  if (loginButton) {
    loginButton.addEventListener('mousedown', function() {
      this.classList.add('login-button-pressed');
    });

    loginButton.addEventListener('mouseup', function() {
      this.classList.remove('login-button-pressed');
    });

    loginButton.addEventListener('mouseleave', function() {
      this.classList.remove('login-button-pressed');
    });
  }

  // Form validation
  const loginForm = document.getElementById('loginForm');
  const emailFeedback = document.getElementById('email-feedback');
  const passwordFeedback = document.getElementById('password-feedback');

  if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
      let isValid = true;

      // Validate email
      const emailInput = document.getElementById('id_login');
      if (emailInput) {
        const emailValue = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailValue) {
          isValid = false;
          emailInput.classList.add('login-input-error');
          if (emailFeedback) {
            emailFeedback.textContent = 'Email address is required';
            emailFeedback.classList.add('login-validation-error');
          }
        } else if (!emailRegex.test(emailValue)) {
          isValid = false;
          emailInput.classList.add('login-input-error');
          if (emailFeedback) {
            emailFeedback.textContent = 'Please enter a valid email address';
            emailFeedback.classList.add('login-validation-error');
          }
        } else {
          emailInput.classList.remove('login-input-error');
          if (emailFeedback) {
            emailFeedback.textContent = '';
            emailFeedback.classList.remove('login-validation-error');
          }
        }
      }

      // Validate password
      const passwordInput = document.getElementById('id_password');
      if (passwordInput) {
        const passwordValue = passwordInput.value;

        if (!passwordValue) {
          isValid = false;
          passwordInput.classList.add('login-input-error');
          if (passwordFeedback) {
            passwordFeedback.textContent = 'Password is required';
            passwordFeedback.classList.add('login-validation-error');
          }
        } else if (passwordValue.length < 6) {
          isValid = false;
          passwordInput.classList.add('login-input-error');
          if (passwordFeedback) {
            passwordFeedback.textContent = 'Password must be at least 6 characters';
            passwordFeedback.classList.add('login-validation-error');
          }
        } else {
          passwordInput.classList.remove('login-input-error');
          if (passwordFeedback) {
            passwordFeedback.textContent = '';
            passwordFeedback.classList.remove('login-validation-error');
          }
        }
      }

      if (!isValid) {
        event.preventDefault();
      } else {
        // Show loading state on button
        const loginButton = document.getElementById('loginButton');
        if (loginButton) {
          loginButton.disabled = true;
          loginButton.querySelector('.login-button-text').textContent = 'Signing In...';
        }
      }
    });

    // Real-time validation
    const emailInput = document.getElementById('id_login');
    if (emailInput) {
      emailInput.addEventListener('input', function() {
        const emailValue = this.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (emailValue && emailRegex.test(emailValue)) {
          this.classList.remove('login-input-error');
          if (emailFeedback) {
            emailFeedback.textContent = '';
            emailFeedback.classList.remove('login-validation-error');
          }
        }
      });
    }

    const passwordInput = document.getElementById('id_password');
    if (passwordInput) {
      passwordInput.addEventListener('input', function() {
        const passwordValue = this.value;

        if (passwordValue && passwordValue.length >= 6) {
          this.classList.remove('login-input-error');
          if (passwordFeedback) {
            passwordFeedback.textContent = '';
            passwordFeedback.classList.remove('login-validation-error');
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
});
