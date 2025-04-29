// Super Admin Dashboard JavaScript - Enhanced for Indian Market

document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements
    addAnimationClasses();

    // Initialize counters with animation
    initCounters();

    // Initialize charts if they exist
    initCharts();

    // Add hover effects to cards
    initCardEffects();

    // Initialize date pickers with Indian format
    initDatePickers();

    // Add notification system
    initNotifications();

    // Initialize tooltips
    initTooltips();

    // Add quick action arrows
    addQuickActionArrows();

    // Add scroll animations
    initScrollAnimations();
});

// Animated counters for statistics
function initCounters() {
    const counters = document.querySelectorAll('.counter-value');

    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 1500; // ms
        const step = Math.ceil(target / (duration / 30)); // Update every 30ms
        let current = 0;

        const updateCounter = () => {
            current += step;
            if (current >= target) {
                counter.textContent = formatNumber(target);
                return;
            }
            counter.textContent = formatNumber(current);
            setTimeout(updateCounter, 30);
        };

        // Start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        observer.observe(counter);
    });
}

// Format numbers with commas for Indian format (e.g., 1,00,000 instead of 100,000)
function formatNumber(num) {
    return num.toLocaleString('en-IN');
}

// Initialize charts
function initCharts() {
    // Transaction Chart
    const transactionCtx = document.getElementById('transactionChart');
    if (transactionCtx) {
        const transactionChart = new Chart(transactionCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Borrows',
                        data: [65, 59, 80, 81, 56, 55, 40, 45, 60, 70, 75, 80],
                        borderColor: '#FF6B35',
                        backgroundColor: 'rgba(255, 107, 53, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Returns',
                        data: [28, 48, 40, 19, 86, 27, 90, 60, 50, 60, 65, 70],
                        borderColor: '#2E8B57',
                        backgroundColor: 'rgba(46, 139, 87, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 5
                    }
                }
            }
        });
    }

    // User Growth Chart
    const userCtx = document.getElementById('userGrowthChart');
    if (userCtx) {
        const userChart = new Chart(userCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'New Users',
                        data: [25, 30, 35, 40, 50, 60],
                        backgroundColor: 'rgba(75, 0, 130, 0.7)',
                        borderRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Library Performance Chart
    const libraryCtx = document.getElementById('libraryPerformanceChart');
    if (libraryCtx) {
        const libraryChart = new Chart(libraryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Delhi Library', 'Mumbai Central', 'Bangalore Tech', 'Chennai Library', 'Kolkata Central'],
                datasets: [
                    {
                        data: [35, 25, 20, 15, 5],
                        backgroundColor: [
                            '#FF6B35',
                            '#2E8B57',
                            '#4B0082',
                            '#F39C12',
                            '#3498DB'
                        ],
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                },
                cutout: '70%'
            }
        });
    }
}

// Add hover effects to cards
function initCardEffects() {
    const cards = document.querySelectorAll('.super-admin-stats-card, .super-admin-card, .super-admin-quick-action');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            this.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%), white`;
        });

        card.addEventListener('mouseleave', function() {
            this.style.background = 'white';
        });
    });
}

// Initialize date pickers with Indian format (DD/MM/YYYY)
function initDatePickers() {
    const datePickers = document.querySelectorAll('.date-picker');

    if (datePickers.length && typeof flatpickr !== 'undefined') {
        datePickers.forEach(picker => {
            flatpickr(picker, {
                dateFormat: "d/m/Y",
                disableMobile: true,
                locale: {
                    firstDayOfWeek: 1
                }
            });
        });
    }
}

// Notification system
function initNotifications() {
    // Check for new notifications every 30 seconds
    setInterval(checkNotifications, 30000);

    // Mark notifications as read
    const notificationLinks = document.querySelectorAll('.admin-pro-notification');
    notificationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            this.classList.remove('unread');
            updateNotificationCount();
        });
    });
}

function checkNotifications() {
    // This would typically be an AJAX call to check for new notifications
    console.log('Checking for new notifications...');
    // For demo purposes, randomly add a notification
    if (Math.random() > 0.7) {
        addNotification({
            icon: 'fas fa-bell',
            title: 'New notification',
            time: 'Just now',
            unread: true
        });
    }
}

function addNotification(notification) {
    const notificationContainer = document.querySelector('.admin-pro-dropdown-body');
    if (!notificationContainer) return;

    const notificationElement = document.createElement('a');
    notificationElement.href = '#';
    notificationElement.className = 'admin-pro-notification' + (notification.unread ? ' unread' : '');

    notificationElement.innerHTML = `
        <div class="admin-pro-notification-icon bg-primary">
            <i class="${notification.icon}"></i>
        </div>
        <div class="admin-pro-notification-content">
            <p>${notification.title}</p>
            <span>${notification.time}</span>
        </div>
    `;

    notificationContainer.prepend(notificationElement);
    updateNotificationCount();

    // Show toast notification
    showToast(notification.title, 'info');
}

function updateNotificationCount() {
    const unreadCount = document.querySelectorAll('.admin-pro-notification.unread').length;
    const badge = document.querySelector('.admin-pro-badge');

    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-${type === 'info' ? 'info-circle' : type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        </div>
        <div class="toast-content">${message}</div>
        <button class="toast-close"><i class="fas fa-times"></i></button>
    `;

    // Add to container
    toastContainer.appendChild(toast);

    // Show with animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Auto hide after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);

    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
}

// Filter functionality for analytics
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('super-admin-analytics-filter')) {
        const filterButtons = document.querySelectorAll('.super-admin-analytics-filter');
        filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        const period = e.target.getAttribute('data-period');
        updateChartData(period);
    }
});

function updateChartData(period) {
    // This would typically update the chart with new data based on the selected period
    console.log(`Updating chart data for period: ${period}`);

    // For demo purposes, show a loading state
    const chartContainer = document.querySelector('.super-admin-chart-container');
    if (chartContainer) {
        chartContainer.classList.add('loading');
        setTimeout(() => {
            chartContainer.classList.remove('loading');
            showToast('Chart data updated', 'success');
        }, 800);
    }
}

// Add a pulse effect to important elements
function addPulseEffect() {
    const elements = document.querySelectorAll('.pulse-effect');
    elements.forEach(el => {
        el.classList.add('pulsing');
        setTimeout(() => {
            el.classList.remove('pulsing');
        }, 2000);
    });
}

// Call this periodically to draw attention to important elements
setInterval(addPulseEffect, 10000);

// Add animation classes to elements
function addAnimationClasses() {
    // Add fadeIn animation to welcome section
    const welcomeSection = document.querySelector('.super-admin-welcome');
    if (welcomeSection) {
        welcomeSection.classList.add('animate-fadeIn');
    }

    // Add staggered fadeIn animations to stats cards
    const statsCards = document.querySelectorAll('.super-admin-stats-card');
    statsCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fadeIn');
    });

    // Add fadeInRight animation to recent activity cards
    const activityCards = document.querySelectorAll('.super-admin-card');
    activityCards.forEach((card, index) => {
        card.style.animationDelay = `${0.3 + (index * 0.1)}s`;
        card.classList.add('animate-fadeInRight');
    });

    // Add pulse animation to notification badges
    const badges = document.querySelectorAll('.menu-badge');
    badges.forEach(badge => {
        badge.classList.add('animate-pulse');
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');

    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');

            const tooltip = document.createElement('div');
            tooltip.className = 'super-admin-tooltip';
            tooltip.textContent = tooltipText;

            document.body.appendChild(tooltip);

            const triggerRect = this.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();

            tooltip.style.top = `${triggerRect.top - tooltipRect.height - 10}px`;
            tooltip.style.left = `${triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2)}px`;

            setTimeout(() => {
                tooltip.classList.add('show');
            }, 10);

            this.addEventListener('mouseleave', function onMouseLeave() {
                tooltip.classList.remove('show');
                setTimeout(() => {
                    tooltip.remove();
                }, 300);
                this.removeEventListener('mouseleave', onMouseLeave);
            });
        });
    });
}

// Add quick action arrows
function addQuickActionArrows() {
    const quickActions = document.querySelectorAll('.super-admin-quick-action');

    quickActions.forEach(action => {
        const arrow = document.createElement('div');
        arrow.className = 'super-admin-quick-action-arrow';
        arrow.innerHTML = '<i class="fas fa-arrow-right"></i>';

        action.appendChild(arrow);
    });
}

// Initialize scroll animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.scroll-animate');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const animation = element.getAttribute('data-animation') || 'fadeIn';

                element.classList.add(`animate-${animation}`);
                observer.unobserve(element);
            }
        });
    }, { threshold: 0.2 });

    animatedElements.forEach(element => {
        observer.observe(element);
    });
}
