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

  // Role selector functionality
  const roleInputs = document.querySelectorAll('.role-selector-input');
  const emailInput = document.getElementById('id_login');

  // Sample emails for demonstration
  const roleEmails = {
    'member': 'member@library.com',
    'library-admin': 'libraryadmin@library.com',
    'super-admin': 'superadmin@library.com'
  };

  roleInputs.forEach(input => {
    input.addEventListener('change', function() {
      if (this.checked) {
        // Update the email placeholder based on role
        if (emailInput) {
          // Add highlight animation
          emailInput.classList.add('login-input-highlight');
          setTimeout(() => {
            emailInput.classList.remove('login-input-highlight');
          }, 1000);
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
