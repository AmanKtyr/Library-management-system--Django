// Theme Selector Functionality
let cycleToNextTheme; // Declare globally so it can be accessed from other scripts

document.addEventListener('DOMContentLoaded', function() {
    // Helper function to convert hex to RGB
    function hexToRgb(hex) {
        // Remove the hash if it exists
        hex = hex.replace('#', '');

        // Parse the hex values
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        return `${r}, ${g}, ${b}`;
    }

    // Theme definitions
    const themes = {
        'classic-light': {
            name: 'Classic Light Theme',
            description: 'Traditional and easy to read, gives a library-like feel.',

            colors: {
                background: '#F9F9F9',
                text: '#333333',
                accent: '#2C3E50',
                button: '#2E8B57',
                buttonHover: '#267349',
                cardBackground: '#FFFFFF',
                border: '#E0E0E0',
                // Footer specific colors
                footerBackground: 'linear-gradient(135deg, #2C3E50 0%, #1A252F 100%)',
                footerText: '#FFFFFF',
                footerAccent: '#2E8B57',
                footerBorder: '#2E8B57'
            }
        },
        'elegant-dark': {
            name: 'Elegant Dark Theme',
            description: 'Modern and premium touch, popular with students.',

            colors: {
                background: '#121212',
                text: '#E0E0E0',
                accent: '#333333',
                button: '#333333',
                buttonHover: '#1A1A1A',
                cardBackground: '#1E1E1E',
                border: '#333333',
                // Footer specific colors
                footerBackground: 'linear-gradient(135deg, #000000 0%, #1A1A1A 100%)',
                footerText: '#E0E0E0',
                footerAccent: '#444444',
                footerBorder: '#333333'
            }
        },
        'earthy': {
            name: 'Earthy Theme',
            description: 'Nature-inspired colors for a warm, inviting experience.',

            colors: {
                background: '#FAF3E0',
                text: '#333333',
                accent: '#228B22',
                button: '#228B22',
                buttonHover: '#1B6B1B',
                cardBackground: '#FFF8E8',
                border: '#D9C9A3',
                // Footer specific colors
                footerBackground: 'linear-gradient(135deg, #2F4F4F 0%, #1B3030 100%)',
                footerText: '#FFFFFF',
                footerAccent: '#228B22',
                footerBorder: '#228B22'
            }
        },
        'royal-purple': {
            name: 'Royal Purple Theme',
            description: 'Elegant and sophisticated with royal purple accents.',

            colors: {
                background: '#F8F7FC',
                text: '#333333',
                accent: '#5E35B1',
                button: '#5E35B1',
                buttonHover: '#4527A0',
                cardBackground: '#FFFFFF',
                border: '#E0E0E0',
                // Footer specific colors
                footerBackground: 'linear-gradient(135deg, #5E35B1 0%, #3F1F7A 100%)',
                footerText: '#FFFFFF',
                footerAccent: '#9575CD',
                footerBorder: '#5E35B1'
            }
        },
        'ocean-blue': {
            name: 'Ocean Blue Theme',
            description: 'Calm and refreshing blue tones inspired by the ocean.',

            colors: {
                background: '#F0F8FF',
                text: '#333333',
                accent: '#1565C0',
                button: '#1565C0',
                buttonHover: '#0D47A1',
                cardBackground: '#FFFFFF',
                border: '#E3F2FD',
                // Footer specific colors
                footerBackground: 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)',
                footerText: '#FFFFFF',
                footerAccent: '#64B5F6',
                footerBorder: '#1565C0'
            }
        }
    };

    // Create theme selector modal
    function createThemeSelector() {
        // Create modal container
        const modal = document.createElement('div');
        modal.className = 'theme-selector-modal';
        modal.id = 'themeSelectorModal';
        modal.innerHTML = `
            <div class="theme-selector-content">
                <div class="theme-selector-header">
                    <h2><i class="fas fa-palette me-2"></i>Choose a Theme</h2>
                    <button class="theme-selector-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="theme-selector-body">
                    <p class="theme-selector-description">Select a color theme for the library management system</p>

                    <!-- Theme Swatches -->
                    <div class="theme-swatches">
                        ${Object.keys(themes).map(themeKey => `
                            <div class="theme-swatch" data-theme="${themeKey}" style="background: linear-gradient(135deg, ${themes[themeKey].colors.accent} 0%, ${themes[themeKey].colors.button} 100%)" title="${themes[themeKey].name}"></div>
                        `).join('')}
                    </div>

                    <div class="theme-options">
                        ${Object.keys(themes).map(themeKey => `
                            <div class="theme-option" data-theme="${themeKey}">
                                <div class="theme-preview">
                                    <div class="theme-preview-header" style="background-color: ${themes[themeKey].colors.accent}"></div>
                                    <div class="theme-preview-body" style="background-color: ${themes[themeKey].colors.background}">
                                        <div class="theme-preview-card" style="background-color: ${themes[themeKey].colors.cardBackground}; border-color: ${themes[themeKey].colors.border}"></div>
                                        <div class="theme-preview-button" style="background-color: ${themes[themeKey].colors.button}"></div>
                                        <div class="theme-preview-footer" style="background: ${themes[themeKey].colors.footerBackground}"></div>
                                    </div>
                                </div>
                                <div class="theme-info">
                                    <h3>${themes[themeKey].name}</h3>
                                    <p>${themes[themeKey].description}</p>
                                    <button class="theme-apply-btn" style="background-color: ${themes[themeKey].colors.button}; color: white;">
                                        Apply Theme <i class="fas fa-check ms-1"></i>
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="theme-selector-footer">
                    <p>Themes will affect the entire website including the footer.</p>
                    <button class="theme-selector-close-btn">Close</button>
                </div>
            </div>
        `;

        // Add modal to body
        document.body.appendChild(modal);

        // Add event listeners for close buttons
        const closeButtons = modal.querySelectorAll('.theme-selector-close, .theme-selector-close-btn');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Add closing animation
                modal.classList.add('closing');

                // Remove show class after animation completes
                setTimeout(() => {
                    modal.classList.remove('show');
                    modal.classList.remove('closing');

                    // Reset animations on theme options
                    const themeOptions = modal.querySelectorAll('.theme-option');
                    themeOptions.forEach(option => {
                        option.classList.remove('animate-in');
                    });
                }, 300);
            });
        });

        // Theme swatch selection listeners
        const themeSwatches = modal.querySelectorAll('.theme-swatch');
        themeSwatches.forEach(swatch => {
            swatch.addEventListener('click', function() {
                const themeKey = this.getAttribute('data-theme');

                // Apply theme immediately
                applyTheme(themeKey);

                // Update active states
                themeSwatches.forEach(s => s.classList.remove('active'));
                this.classList.add('active');

                // Update theme options active state
                const themeOptions = modal.querySelectorAll('.theme-option');
                themeOptions.forEach(opt => {
                    opt.classList.remove('active');
                    if (opt.getAttribute('data-theme') === themeKey) {
                        opt.classList.add('active');
                    }
                });

                // Save theme preference
                localStorage.setItem('selectedTheme', themeKey);

                // Show success indicator
                this.insertAdjacentHTML('beforeend', '<span class="swatch-check"><i class="fas fa-check"></i></span>');

                // Remove check icon after animation
                setTimeout(() => {
                    const checkIcon = this.querySelector('.swatch-check');
                    if (checkIcon) checkIcon.remove();
                }, 1500);
            });
        });

        // Theme option selection event listeners
        const themeOptions = modal.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            // Apply button click event
            const applyButton = option.querySelector('.theme-apply-btn');
            if (applyButton) {
                applyButton.addEventListener('click', function(e) {
                    e.stopPropagation(); // Prevent the option click event from firing
                    const themeKey = option.getAttribute('data-theme');
                    applyTheme(themeKey);

                    // Update active state for options
                    themeOptions.forEach(opt => opt.classList.remove('active'));
                    option.classList.add('active');

                    // Update active state for swatches
                    themeSwatches.forEach(swatch => {
                        swatch.classList.remove('active');
                        if (swatch.getAttribute('data-theme') === themeKey) {
                            swatch.classList.add('active');
                        }
                    });

                    // Save theme preference
                    localStorage.setItem('selectedTheme', themeKey);

                    // Show success message
                    applyButton.innerHTML = '<i class="fas fa-check me-1"></i> Applied!';
                    applyButton.classList.add('applied');

                    // Reset button text after 2 seconds
                    setTimeout(() => {
                        applyButton.innerHTML = 'Apply Theme <i class="fas fa-check ms-1"></i>';
                        applyButton.classList.remove('applied');
                    }, 2000);

                    // Add closing animation
                    modal.classList.add('closing');

                    // Close modal after animation
                    setTimeout(() => {
                        modal.classList.remove('show');
                        modal.classList.remove('closing');

                        // Reset animations on theme options
                        themeOptions.forEach(opt => {
                            opt.classList.remove('animate-in');
                        });
                    }, 500);
                });
            }

            // Option click event (preview)
            option.addEventListener('click', function() {
                // Preview the theme without applying it
                const themeKey = this.getAttribute('data-theme');

                // Update active state for visual feedback
                themeOptions.forEach(opt => opt.classList.remove('preview-active'));
                this.classList.add('preview-active');
            });
        });

        // Mark current theme as active
        const currentTheme = localStorage.getItem('selectedTheme') || 'classic-light';
        const currentThemeOption = modal.querySelector(`.theme-option[data-theme="${currentTheme}"]`);
        if (currentThemeOption) {
            currentThemeOption.classList.add('active');
        }

        return modal;
    }

    // Create theme toggle button
    function createThemeButton() {
        const themeButton = document.createElement('button');
        themeButton.className = 'theme-selector-toggle';

        // Get current theme name
        const currentThemeKey = localStorage.getItem('selectedTheme') || 'classic-light';
        const currentTheme = themes[currentThemeKey];

        // Create button with tooltip showing current theme
        themeButton.innerHTML = `
            <i class="fas fa-palette"></i>
            <span class="theme-tooltip">
                Current: <span class="current-theme-name">${currentTheme.name}</span>
                <span class="tooltip-arrow"></span>
            </span>
        `;

        themeButton.title = 'Change Theme';

        // Set initial button gradient based on theme
        themeButton.style.background = `linear-gradient(135deg, ${currentTheme.colors.accent} 0%, ${currentTheme.colors.button} 100%)`;

        themeButton.addEventListener('click', function() {
            const modal = document.getElementById('themeSelectorModal');
            if (modal) {
                modal.classList.add('show');

                // Add animation to theme options
                const themeOptions = modal.querySelectorAll('.theme-option');
                themeOptions.forEach((option, index) => {
                    option.style.animationDelay = `${index * 0.1}s`;
                    option.classList.add('animate-in');
                });
            }
        });

        document.body.appendChild(themeButton);
    }

    // Create theme cycle button
    function createThemeCycleButton() {
        const themeCycleButton = document.createElement('button');
        themeCycleButton.className = 'theme-cycle-button';
        themeCycleButton.id = 'themeCycleButton';

        // Get current theme name
        const currentThemeKey = localStorage.getItem('selectedTheme') || 'classic-light';
        const currentTheme = themes[currentThemeKey];

        // Create button with tooltip showing current theme
        themeCycleButton.innerHTML = `
            <i class="fas fa-sync-alt"></i>
            <span class="theme-tooltip">
                Cycle Themes (Current: <span class="current-theme-name">${currentTheme.name}</span>)
                <span class="tooltip-arrow"></span>
            </span>
        `;

        themeCycleButton.title = 'Cycle Through Themes';

        // Set initial button gradient based on theme
        themeCycleButton.style.background = `linear-gradient(135deg, ${currentTheme.colors.accent} 0%, ${currentTheme.colors.button} 100%)`;

        // Add click event to cycle through themes
        themeCycleButton.addEventListener('click', function() {
            cycleThroughThemes();
        });

        document.body.appendChild(themeCycleButton);
    }

    // Function to cycle to the next theme
    function cycleThroughThemes() {
        // Get all theme keys
        const themeKeys = Object.keys(themes);

        // Get current theme
        const currentThemeKey = localStorage.getItem('selectedTheme') || 'classic-light';

        // Find the index of the current theme
        const currentIndex = themeKeys.indexOf(currentThemeKey);

        // Calculate the next theme index (loop back to 0 if at the end)
        const nextIndex = (currentIndex + 1) % themeKeys.length;

        // Get the next theme key
        const nextThemeKey = themeKeys[nextIndex];

        // Apply the next theme
        applyTheme(nextThemeKey);

        // Save the new theme preference
        localStorage.setItem('selectedTheme', nextThemeKey);

        // Show notification
        showThemeChangeNotification(themes[nextThemeKey].name);

        // Update active states in UI
        updateThemeActiveStates(nextThemeKey);
    }

    // Assign to global variable for access from other scripts
    cycleToNextTheme = cycleThroughThemes;

    // Show a notification when theme changes
    function showThemeChangeNotification(themeName) {
        // Remove any existing notifications
        const existingNotification = document.querySelector('.theme-change-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'theme-change-notification';
        notification.innerHTML = `
            <i class="fas fa-palette"></i>
            Theme changed to: ${themeName}
        `;

        // Add to body
        document.body.appendChild(notification);

        // Show notification with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Remove notification after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 3000);
    }

    // Update active states in UI elements
    function updateThemeActiveStates(themeKey) {
        // Update theme swatches
        document.querySelectorAll('.theme-swatch').forEach(swatch => {
            swatch.classList.remove('active');
            if (swatch.getAttribute('data-theme') === themeKey) {
                swatch.classList.add('active');
            }
        });

        // Update theme options
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-theme') === themeKey) {
                option.classList.add('active');
            }
        });

        // Update theme slider dots
        document.querySelectorAll('.theme-slider-dot').forEach(dot => {
            dot.classList.remove('active');
            if (dot.getAttribute('data-theme') === themeKey) {
                dot.classList.add('active');
            }
        });
    }

    // Apply theme function
    function applyTheme(themeKey) {
        const theme = themes[themeKey];
        if (!theme) return;

        // Create or update CSS variables
        const root = document.documentElement;

        // Set CSS variables
        root.style.setProperty('--background-color', theme.colors.background);
        root.style.setProperty('--text-color', theme.colors.text);
        root.style.setProperty('--accent-color', theme.colors.accent);
        root.style.setProperty('--button-color', theme.colors.button);
        root.style.setProperty('--button-hover-color', theme.colors.buttonHover);
        root.style.setProperty('--card-background', theme.colors.cardBackground);
        root.style.setProperty('--border-color', theme.colors.border);

        // Set footer-specific variables
        root.style.setProperty('--footer-background', theme.colors.footerBackground);
        root.style.setProperty('--footer-text', theme.colors.footerText);
        root.style.setProperty('--footer-accent', theme.colors.footerAccent);
        root.style.setProperty('--footer-border', theme.colors.footerBorder);

        // Set RGB versions of colors for rgba usage
        root.style.setProperty('--background-color-rgb', hexToRgb(theme.colors.background));
        root.style.setProperty('--text-color-rgb', hexToRgb(theme.colors.text));
        root.style.setProperty('--accent-color-rgb', hexToRgb(theme.colors.accent));
        root.style.setProperty('--button-color-rgb', hexToRgb(theme.colors.button));
        root.style.setProperty('--button-hover-color-rgb', hexToRgb(theme.colors.buttonHover));
        root.style.setProperty('--card-background-rgb', hexToRgb(theme.colors.cardBackground));
        root.style.setProperty('--border-color-rgb', hexToRgb(theme.colors.border));

        // Add theme class to body
        document.body.className = document.body.className.replace(/theme-\w+/g, '').trim();
        document.body.classList.add(`theme-${themeKey}`);

        // Update dark mode status based on theme
        if (themeKey === 'elegant-dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            document.body.classList.add('dark-mode');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            document.body.classList.remove('dark-mode');
        }

        // Update theme selector button color
        const themeButton = document.querySelector('.theme-selector-toggle');
        if (themeButton) {
            themeButton.style.background = `linear-gradient(135deg, ${theme.colors.accent} 0%, ${theme.colors.button} 100%)`;
        }

        // Update current theme name in tooltip
        const themeTooltip = document.querySelector('.current-theme-name');
        if (themeTooltip) {
            themeTooltip.textContent = theme.name;
        }

        // Dispatch custom event for theme change
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: {
                theme: themeKey,
                colors: theme.colors
            }
        }));
    }

    // Create theme slider
    function createThemeSlider() {
        const sliderContainer = document.createElement('div');
        sliderContainer.className = 'theme-slider-container';

        // Get current theme
        const currentThemeKey = localStorage.getItem('selectedTheme') || 'classic-light';

        // Create dots for each theme
        Object.keys(themes).forEach(themeKey => {
            const dot = document.createElement('div');
            dot.className = 'theme-slider-dot';
            dot.setAttribute('data-theme', themeKey);
            dot.style.background = `linear-gradient(135deg, ${themes[themeKey].colors.accent} 0%, ${themes[themeKey].colors.button} 100%)`;
            dot.title = themes[themeKey].name;

            // Mark current theme as active
            if (themeKey === currentThemeKey) {
                dot.classList.add('active');
            }

            // Add click event
            dot.addEventListener('click', function() {
                const themeKey = this.getAttribute('data-theme');

                // Apply theme
                applyTheme(themeKey);

                // Update active state
                document.querySelectorAll('.theme-slider-dot').forEach(d => d.classList.remove('active'));
                this.classList.add('active');

                // Save theme preference
                localStorage.setItem('selectedTheme', themeKey);
            });

            sliderContainer.appendChild(dot);
        });

        document.body.appendChild(sliderContainer);
    }

    // Initialize theme selector
    function initThemeSelector() {
        createThemeSelector();
        createThemeButton();
        createThemeCycleButton(); // Add the theme cycle button
        createThemeSlider();

        // Apply saved theme or default
        const savedTheme = localStorage.getItem('selectedTheme') || 'classic-light';
        applyTheme(savedTheme);
    }

    // Initialize
    initThemeSelector();
});
