// Dark Mode Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create dark mode toggle button
    const darkModeToggle = document.createElement('div');
    darkModeToggle.className = 'dark-mode-toggle';
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    document.body.appendChild(darkModeToggle);
    
    // Check for saved user preference
    const darkMode = localStorage.getItem('darkMode');
    
    // If dark mode was previously enabled, apply it
    if (darkMode === 'enabled') {
        enableDarkMode();
    }
    
    // Toggle dark mode on button click
    darkModeToggle.addEventListener('click', () => {
        const darkMode = localStorage.getItem('darkMode');
        
        if (darkMode !== 'enabled') {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
    });
    
    // Function to enable dark mode
    function enableDarkMode() {
        // Add dark mode class to body
        document.body.classList.add('dark-mode');
        // Update button icon
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        // Save user preference
        localStorage.setItem('darkMode', 'enabled');
    }
    
    // Function to disable dark mode
    function disableDarkMode() {
        // Remove dark mode class from body
        document.body.classList.remove('dark-mode');
        // Update button icon
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        // Save user preference
        localStorage.setItem('darkMode', null);
    }
});
