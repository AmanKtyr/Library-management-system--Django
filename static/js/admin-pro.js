/**
 * Professional Admin Panel JavaScript
 * Library Management System
 *
 * Consolidated admin.js and admin-pro.js into a single file
 */

document.addEventListener('DOMContentLoaded', function() {
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

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.admin-pro-alert, .alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add active class to current menu item
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.admin-pro-menu-item');

    menuItems.forEach(function(item) {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active');
        }
    });

    // Add user initials if not available
    const userImgPlaceholders = document.querySelectorAll('.admin-pro-user-avatar-placeholder, .admin-pro-user-img-placeholder');
    userImgPlaceholders.forEach(function(placeholder) {
        if (!placeholder.textContent.trim()) {
            const userName = document.querySelector('.admin-pro-user-name').textContent.trim();
            const initials = userName.split(' ').map(name => name[0]).join('').toUpperCase();
            placeholder.textContent = initials || 'U';
        }
    });

    // Responsive tables
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        if (!table.parentElement.classList.contains('table-responsive') &&
            !table.parentElement.classList.contains('admin-pro-table-container')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('admin-pro-table-container');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm, [data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-message') || 'Are you sure you want to delete this item? This action cannot be undone.';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Toggle user status
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Search form validation
    const searchForms = document.querySelectorAll('.search-form, form[role="search"]');
    searchForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[type="search"], input[type="text"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.classList.add('is-invalid');

                // Create or update feedback message
                let feedback = searchInput.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.classList.add('invalid-feedback');
                    searchInput.parentNode.insertBefore(feedback, searchInput.nextSibling);
                }
                feedback.textContent = 'Please enter a search term';
            }
        });
    });

    // Filter form auto-submit
    const filterSelects = document.querySelectorAll('.filter-select, select[data-autosubmit]');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Date range picker for reports
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');

    if (startDate && endDate) {
        startDate.addEventListener('change', function() {
            endDate.min = this.value;
        });

        endDate.addEventListener('change', function() {
            startDate.max = this.value;
        });
    }

    // Date range picker initialization if available
    if (typeof daterangepicker !== 'undefined') {
        const dateRangePickers = document.querySelectorAll('.daterangepicker-input');
        dateRangePickers.forEach(function(picker) {
            new daterangepicker(picker, {
                autoUpdateInput: false,
                locale: {
                    cancelLabel: 'Clear',
                    applyLabel: 'Apply',
                    format: 'YYYY-MM-DD'
                }
            });

            picker.addEventListener('apply.daterangepicker', function(ev, picker) {
                this.value = picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD');

                // Update hidden inputs if they exist
                const startInput = document.querySelector(this.getAttribute('data-start-input'));
                const endInput = document.querySelector(this.getAttribute('data-end-input'));

                if (startInput) startInput.value = picker.startDate.format('YYYY-MM-DD');
                if (endInput) endInput.value = picker.endDate.format('YYYY-MM-DD');
            });

            picker.addEventListener('cancel.daterangepicker', function() {
                this.value = '';

                // Clear hidden inputs if they exist
                const startInput = document.querySelector(this.getAttribute('data-start-input'));
                const endInput = document.querySelector(this.getAttribute('data-end-input'));

                if (startInput) startInput.value = '';
                if (endInput) endInput.value = '';
            });
        });
    }

    // Initialize Select2 if available
    if (typeof Select2 !== 'undefined') {
        const select2Elements = document.querySelectorAll('.select2-input');
        select2Elements.forEach(function(element) {
            new Select2(element, {
                placeholder: element.getAttribute('placeholder') || 'Select an option',
                allowClear: element.hasAttribute('data-allow-clear')
            });
        });
    }

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    fileInputs.forEach(function(input) {
        const previewElement = document.querySelector(input.getAttribute('data-preview'));
        if (previewElement) {
            input.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        if (previewElement.tagName === 'IMG') {
                            previewElement.src = e.target.result;
                        } else {
                            previewElement.style.backgroundImage = `url(${e.target.result})`;
                        }
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    });

    // Bulk actions
    const bulkActionSelects = document.querySelectorAll('.bulk-action-select');
    bulkActionSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            if (this.value) {
                const form = this.closest('form');
                if (form) {
                    // Check if any items are selected
                    const checkboxes = form.querySelectorAll('input[type="checkbox"][name="selected_items"]:checked');
                    if (checkboxes.length === 0) {
                        alert('Please select at least one item.');
                        this.value = '';
                        return;
                    }

                    // Confirm dangerous actions
                    if (this.value === 'delete' && !confirm('Are you sure you want to delete the selected items? This action cannot be undone.')) {
                        this.value = '';
                        return;
                    }

                    form.submit();
                }
            }
        });
    });

    // Select all checkboxes
    const selectAllCheckboxes = document.querySelectorAll('.select-all, #select-all');
    selectAllCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const form = this.closest('form') || this.closest('table').closest('form') || document;
            const checkboxes = form.querySelectorAll('input[type="checkbox"][name="selected_items"]');
            checkboxes.forEach(function(item) {
                item.checked = checkbox.checked;
            });
        });
    });

    // Auto-update select-all checkbox state
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[type="checkbox"][name="selected_items"]')) {
            const form = e.target.closest('form') || e.target.closest('table').closest('form') || document;
            const selectAll = form.querySelector('.select-all, #select-all');
            const checkboxes = form.querySelectorAll('input[type="checkbox"][name="selected_items"]');
            const checkedBoxes = form.querySelectorAll('input[type="checkbox"][name="selected_items"]:checked');

            if (selectAll) {
                selectAll.checked = checkboxes.length === checkedBoxes.length;
                selectAll.indeterminate = checkedBoxes.length > 0 && checkboxes.length !== checkedBoxes.length;
            }
        }
    });

    // Initialize charts if Chart.js is available and there are charts to render
    if (typeof Chart !== 'undefined') {
        // Set default Chart.js options
        Chart.defaults.font.family = "'Poppins', 'Helvetica', 'Arial', sans-serif";
        Chart.defaults.color = '#6c757d';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        Chart.defaults.plugins.legend.position = 'bottom';

        // Apply dark mode to charts if needed
        if (document.body.classList.contains('dark-mode')) {
            Chart.defaults.color = '#e0e0e0';
            Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.1)';
        }
    }
});
