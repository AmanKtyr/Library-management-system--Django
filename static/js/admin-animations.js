/**
 * Admin Panel Animations and Interactive Effects
 * Enhances the user experience with modern animations and interactive effects
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initializeAnimations();
    
    // Add event listeners
    addEventListeners();
    
    // Initialize charts if any
    initializeCharts();
});

/**
 * Initialize animations for various elements
 */
function initializeAnimations() {
    // Animate status cards on page load
    animateStatusCards();
    
    // Animate action cards on page load
    animateActionCards();
    
    // Animate staff cards on page load
    animateStaffCards();
    
    // Animate sidebar menu items
    animateSidebarMenuItems();
    
    // Add hover effects to cards
    addCardHoverEffects();
}

/**
 * Add event listeners for interactive elements
 */
function addEventListeners() {
    // Toggle sidebar
    const toggleBtn = document.querySelector('.admin-pro-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            document.querySelector('.admin-pro-wrapper').classList.toggle('toggled');
        });
    }
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.admin-pro-btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
    });
    
    // Add scroll animations
    window.addEventListener('scroll', handleScrollAnimations);
}

/**
 * Create ripple effect on button click
 * @param {Event} e - Click event
 */
function createRippleEffect(e) {
    const button = e.currentTarget;
    
    // Create ripple element
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('admin-pro-ripple');
    
    button.appendChild(ripple);
    
    // Remove ripple after animation completes
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Animate status cards with staggered delay
 */
function animateStatusCards() {
    const statusCards = document.querySelectorAll('.admin-pro-status-card');
    
    statusCards.forEach((card, index) => {
        // Add staggered animation delay
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

/**
 * Animate action cards with staggered delay
 */
function animateActionCards() {
    const actionCards = document.querySelectorAll('.admin-pro-action-card');
    
    actionCards.forEach((card, index) => {
        // Add staggered animation delay
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
        }, 100 * index);
    });
}

/**
 * Animate staff cards with staggered delay
 */
function animateStaffCards() {
    const staffCards = document.querySelectorAll('.admin-pro-staff-card');
    
    staffCards.forEach((card, index) => {
        // Add staggered animation delay
        card.style.opacity = '0';
        card.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }, 100 * index);
    });
}

/**
 * Animate sidebar menu items with staggered delay
 */
function animateSidebarMenuItems() {
    const menuItems = document.querySelectorAll('.admin-pro-menu-item');
    
    menuItems.forEach((item, index) => {
        // Add staggered animation delay
        item.style.opacity = '0';
        item.style.transform = 'translateX(-10px)';
        
        setTimeout(() => {
            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 50 * index);
    });
}

/**
 * Add hover effects to cards
 */
function addCardHoverEffects() {
    // Add 3D tilt effect to cards
    const cards = document.querySelectorAll('.admin-pro-card, .admin-pro-action-card, .admin-pro-status-card, .admin-pro-staff-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within the element
            const y = e.clientY - rect.top;  // y position within the element
            
            // Calculate rotation based on mouse position (limited to 5 degrees)
            const rotateY = ((x / rect.width) - 0.5) * 5;
            const rotateX = ((y / rect.height) - 0.5) * -5;
            
            // Apply the transform
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', function() {
            // Reset transform when mouse leaves
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

/**
 * Handle scroll animations
 */
function handleScrollAnimations() {
    // Animate elements when they come into view
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    animatedElements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('animated');
        }
    });
}

/**
 * Initialize charts if Chart.js is available
 */
function initializeCharts() {
    if (typeof Chart !== 'undefined') {
        // Initialize charts with smooth animations
        const chartCanvases = document.querySelectorAll('.admin-pro-chart');
        
        chartCanvases.forEach(canvas => {
            const ctx = canvas.getContext('2d');
            const chartType = canvas.dataset.chartType || 'line';
            const chartData = JSON.parse(canvas.dataset.chartData || '{}');
            
            new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    animation: {
                        duration: 2000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        });
    }
}

/**
 * Add CSS class for admin-pro-ripple effect
 */
function addRippleStyle() {
    // Check if style already exists
    if (!document.getElementById('admin-pro-ripple-style')) {
        const style = document.createElement('style');
        style.id = 'admin-pro-ripple-style';
        style.textContent = `
            .admin-pro-ripple {
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: admin-pro-ripple 0.6s linear;
                pointer-events: none;
                width: 100px;
                height: 100px;
                margin-top: -50px;
                margin-left: -50px;
            }
            
            @keyframes admin-pro-ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Add ripple style to document
addRippleStyle();
