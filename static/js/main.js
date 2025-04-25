// Modern JavaScript for LibraryHub

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds with fade effect
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Book search form with enhanced validation
    const searchForm = document.getElementById('book-search-form');
    if (searchForm) {
        const searchInput = document.getElementById('search-input');
        const searchFeedback = document.createElement('div');
        searchFeedback.className = 'invalid-feedback';
        searchFeedback.textContent = 'Please enter a search term';
        searchInput.parentNode.appendChild(searchFeedback);

        // Add input event for real-time validation
        searchInput.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
            }
        });

        searchForm.addEventListener('submit', function(e) {
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
                searchInput.focus();

                // Shake animation for invalid input
                searchInput.classList.add('shake');
                setTimeout(() => {
                    searchInput.classList.remove('shake');
                }, 500);
            }
        });
    }

    // Book copy status update with confirmation
    const statusSelects = document.querySelectorAll('.book-status-select');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            const newStatus = this.options[this.selectedIndex].text;

            if (confirm(`Are you sure you want to change the status to "${newStatus}"?`)) {
                // Show loading spinner
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
                    submitBtn.disabled = true;

                    // Submit after a small delay to show the spinner
                    setTimeout(() => {
                        form.submit();
                    }, 300);
                } else {
                    form.submit();
                }
            } else {
                // Reset to previous value if canceled
                this.value = this.dataset.originalValue;
            }
        });

        // Store original value for cancellation
        select.dataset.originalValue = select.value;
    });

    // Enhanced date range picker for reports
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');

    if (startDate && endDate) {
        // Set default date range (last 30 days)
        if (!startDate.value) {
            const today = new Date();
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(today.getDate() - 30);

            endDate.valueAsDate = today;
            startDate.valueAsDate = thirtyDaysAgo;
        }

        startDate.addEventListener('change', function() {
            endDate.min = this.value;
            validateDateRange();
        });

        endDate.addEventListener('change', function() {
            startDate.max = this.value;
            validateDateRange();
        });

        function validateDateRange() {
            const start = new Date(startDate.value);
            const end = new Date(endDate.value);
            const rangeInfo = document.getElementById('date-range-info');

            if (rangeInfo) {
                const diffTime = Math.abs(end - start);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                rangeInfo.textContent = `Selected range: ${diffDays} days`;
            }
        }

        // Initialize validation
        validateDateRange();
    }

    // Lazy loading for images
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const lazyLoadScript = document.createElement('script');
        lazyLoadScript.src = 'https://cdn.jsdelivr.net/npm/lozad/dist/lozad.min.js';
        document.head.appendChild(lazyLoadScript);

        lazyLoadScript.onload = function() {
            const observer = lozad();
            observer.observe();
        };
    }

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && document.querySelector(targetId)) {
                e.preventDefault();
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation class to elements when they come into view
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    if (animatedElements.length > 0) {
        const animateOnScroll = function() {
            animatedElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;

                if (elementPosition < windowHeight - 50) {
                    element.classList.add('animated');
                }
            });
        };

        window.addEventListener('scroll', animateOnScroll);
        animateOnScroll(); // Check on initial load
    }

    // Mobile menu enhancement
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('mobile-menu-open');
        });
    }

    // Add CSS class for shake animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        .shake {
            animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
        }
    `;
    document.head.appendChild(style);
});
