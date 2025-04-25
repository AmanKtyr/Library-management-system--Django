/**
 * Modern Components JavaScript for Library Management System
 * Adds interactivity to modern UI components
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modern components
    initModernDropdowns();
    initModernTabs();
    initModernTooltips();
    initModernAlerts();
    initCustomCheckboxes();
    initCustomRadios();
    initSkeletonLoaders();
    initAnimatedCounters();
    initSmoothScrolling();
    initNavbarScrollEffect();
    initCardHoverEffects();
    initFilterToggle();
});

/**
 * Initialize Modern Dropdowns
 */
function initModernDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-modern-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.closest('.dropdown-modern');
            
            // Close all other dropdowns
            document.querySelectorAll('.dropdown-modern.show').forEach(openDropdown => {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('show');
                }
            });
            
            // Toggle current dropdown
            dropdown.classList.toggle('show');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-modern')) {
            document.querySelectorAll('.dropdown-modern.show').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
}

/**
 * Initialize Modern Tabs
 */
function initModernTabs() {
    const tabItems = document.querySelectorAll('.tabs-modern-item');
    
    tabItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            const tabContainer = this.closest('.tabs-modern');
            
            // Remove active class from all tabs and content
            tabContainer.querySelectorAll('.tabs-modern-item').forEach(tab => {
                tab.classList.remove('active');
            });
            
            tabContainer.querySelectorAll('.tabs-modern-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to current tab and content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

/**
 * Initialize Modern Tooltips
 */
function initModernTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        const tooltipText = tooltip.getAttribute('data-tooltip');
        const tooltipPosition = tooltip.getAttribute('data-tooltip-position') || 'top';
        
        // Create tooltip element
        const tooltipElement = document.createElement('div');
        tooltipElement.className = 'tooltip-modern-content tooltip-' + tooltipPosition;
        tooltipElement.textContent = tooltipText;
        
        // Add tooltip to element
        tooltip.classList.add('tooltip-modern');
        tooltip.appendChild(tooltipElement);
    });
}

/**
 * Initialize Modern Alerts
 */
function initModernAlerts() {
    const alertCloseButtons = document.querySelectorAll('.alert-modern-close');
    
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert-modern');
            
            // Add closing animation
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            
            // Remove alert after animation
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });
    
    // Auto-close alerts after 5 seconds
    document.querySelectorAll('.alert-modern[data-auto-close="true"]').forEach(alert => {
        setTimeout(() => {
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

/**
 * Initialize Custom Checkboxes
 */
function initCustomCheckboxes() {
    const customCheckboxes = document.querySelectorAll('.custom-checkbox');
    
    customCheckboxes.forEach(checkbox => {
        const input = checkbox.querySelector('input[type="checkbox"]');
        const icon = checkbox.querySelector('.checkbox-icon');
        
        // Add icon element if not present
        if (!icon && input) {
            const newIcon = document.createElement('div');
            newIcon.className = 'checkbox-icon';
            newIcon.innerHTML = '<i class="fas fa-check" style="font-size: 12px;"></i>';
            checkbox.insertBefore(newIcon, input.nextSibling);
        }
        
        // Add click event to label
        checkbox.addEventListener('click', function(e) {
            if (e.target !== input) {
                input.checked = !input.checked;
                
                // Trigger change event
                const event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    });
}

/**
 * Initialize Custom Radio Buttons
 */
function initCustomRadios() {
    const customRadios = document.querySelectorAll('.custom-radio');
    
    customRadios.forEach(radio => {
        const input = radio.querySelector('input[type="radio"]');
        const icon = radio.querySelector('.radio-icon');
        
        // Add icon element if not present
        if (!icon && input) {
            const newIcon = document.createElement('div');
            newIcon.className = 'radio-icon';
            radio.insertBefore(newIcon, input.nextSibling);
        }
        
        // Add click event to label
        radio.addEventListener('click', function(e) {
            if (e.target !== input) {
                input.checked = true;
                
                // Trigger change event
                const event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    });
}

/**
 * Initialize Skeleton Loaders
 * Replaces skeleton loaders with actual content when loaded
 */
function initSkeletonLoaders() {
    // This function will be called when content is loaded
    window.replaceSkeleton = function(skeletonId, content) {
        const skeleton = document.getElementById(skeletonId);
        if (skeleton) {
            // Create temporary element to parse HTML content
            const temp = document.createElement('div');
            temp.innerHTML = content;
            
            // Replace skeleton with actual content
            skeleton.parentNode.replaceChild(temp.firstChild, skeleton);
        }
    };
    
    // Auto-remove skeletons after 2 seconds (for demo purposes)
    document.querySelectorAll('.skeleton-auto-remove').forEach(skeleton => {
        setTimeout(() => {
            skeleton.classList.add('loaded');
            
            setTimeout(() => {
                skeleton.style.display = 'none';
                const content = skeleton.nextElementSibling;
                if (content && content.classList.contains('skeleton-content')) {
                    content.style.display = 'block';
                }
            }, 300);
        }, 2000);
    });
}

/**
 * Initialize Animated Counters
 * Animates counting up to the target number
 */
function initAnimatedCounters() {
    const counters = document.querySelectorAll('.counter-animated');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = parseInt(counter.getAttribute('data-duration') || '2000');
        const countTo = parseInt(counter.innerText) || 0;
        
        const range = target - countTo;
        const minCount = 50;
        const stepTime = Math.abs(Math.floor(duration / Math.max(minCount, range)));
        
        let current = countTo;
        const step = Math.sign(range) * Math.ceil(Math.abs(range) / minCount);
        
        const timer = setInterval(() => {
            current += step;
            counter.innerText = current.toLocaleString();
            
            if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
                counter.innerText = target.toLocaleString();
                clearInterval(timer);
            }
        }, stepTime);
    });
}

/**
 * Initialize Smooth Scrolling
 * Adds smooth scrolling to anchor links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Update URL hash without scrolling
                history.pushState(null, null, targetId);
            }
        });
    });
}

/**
 * Initialize Navbar Scroll Effect
 * Adds class to navbar when scrolling down
 */
function initNavbarScrollEffect() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
        
        // Check on initial load
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        }
    }
}

/**
 * Initialize Card Hover Effects
 * Adds hover effects to cards
 */
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.card-hover');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover-active');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover-active');
        });
    });
}

/**
 * Initialize Filter Toggle
 * Toggles filter container visibility
 */
function initFilterToggle() {
    const filterToggles = document.querySelectorAll('.filter-toggle');
    
    filterToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('data-target');
            const filterContainer = document.getElementById(targetId);
            
            if (filterContainer) {
                filterContainer.classList.toggle('show');
                
                // Update toggle icon
                const icon = this.querySelector('i');
                if (icon) {
                    if (filterContainer.classList.contains('show')) {
                        icon.className = icon.className.replace('fa-filter', 'fa-times');
                    } else {
                        icon.className = icon.className.replace('fa-times', 'fa-filter');
                    }
                }
            }
        });
    });
}
