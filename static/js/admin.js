// Custom JavaScript for Admin Panel

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
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Toggle user status
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            const form = this.closest('form');
            form.submit();
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
    
    // Search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
            } else {
                searchInput.classList.remove('is-invalid');
            }
        });
    }
    
    // Filter form auto-submit
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            form.submit();
        });
    });
    
    // Bulk actions
    const bulkActionSelect = document.getElementById('bulk-action');
    const bulkActionForm = document.getElementById('bulk-action-form');
    
    if (bulkActionSelect && bulkActionForm) {
        bulkActionSelect.addEventListener('change', function() {
            if (this.value) {
                // Check if any items are selected
                const checkboxes = document.querySelectorAll('input[name="selected_items"]:checked');
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
                
                bulkActionForm.submit();
            }
        });
    }
    
    // Select all checkboxes
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('input[name="selected_items"]');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }
});
