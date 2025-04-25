// Theme Selector Functionality
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
            hindiDescription: 'ये थीम पारंपरिक और पढ़ने में आसान होती है, लाइब्रेरी जैसा फील देता है।',
            colors: {
                background: '#F9F9F9',
                text: '#333333',
                accent: '#2C3E50',
                button: '#2E8B57',
                buttonHover: '#267349',
                cardBackground: '#FFFFFF',
                border: '#E0E0E0'
            }
        },
        'elegant-dark': {
            name: 'Elegant Dark Theme',
            description: 'Modern and premium touch, popular with students.',
            hindiDescription: 'इस थीम से मॉडर्न और प्रीमियम टच मिलता है, स्टूडेंट्स को भी पसंद आता है।',
            colors: {
                background: '#121212',
                text: '#E0E0E0',
                accent: '#00BCD4',
                button: '#00BCD4',
                buttonHover: '#0097A7',
                cardBackground: '#1E1E1E',
                border: '#333333'
            }
        },
        'earthy': {
            name: 'Earthy Theme',
            description: 'Nature-inspired colors for a warm, inviting experience.',
            hindiDescription: 'प्रकृति से प्रेरित रंग, गर्म और आमंत्रित करने वाला अनुभव।',
            colors: {
                background: '#FAF3E0',
                text: '#333333',
                accent: '#228B22',
                button: '#228B22',
                buttonHover: '#1B6B1B',
                cardBackground: '#FFF8E8',
                border: '#D9C9A3'
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
                    <h2>Choose a Theme <span class="hindi-text">थीम चुनें</span></h2>
                    <button class="theme-selector-close">&times;</button>
                </div>
                <div class="theme-selector-body">
                    <p class="theme-selector-description">Select a color theme for the library management system: <span class="hindi-text">लाइब्रेरी मैनेजमेंट सिस्टम के लिए एक रंग थीम चुनें:</span></p>
                    <div class="theme-options">
                        ${Object.keys(themes).map(themeKey => `
                            <div class="theme-option" data-theme="${themeKey}">
                                <div class="theme-preview">
                                    <div class="theme-preview-header" style="background-color: ${themes[themeKey].colors.accent}"></div>
                                    <div class="theme-preview-body" style="background-color: ${themes[themeKey].colors.background}">
                                        <div class="theme-preview-card" style="background-color: ${themes[themeKey].colors.cardBackground}; border-color: ${themes[themeKey].colors.border}"></div>
                                        <div class="theme-preview-button" style="background-color: ${themes[themeKey].colors.button}"></div>
                                    </div>
                                </div>
                                <div class="theme-info">
                                    <h3>${themes[themeKey].name}</h3>
                                    <p>${themes[themeKey].description}</p>
                                    <p class="hindi-description">${themes[themeKey].hindiDescription}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        // Add modal to body
        document.body.appendChild(modal);

        // Add event listeners
        const closeButton = modal.querySelector('.theme-selector-close');
        closeButton.addEventListener('click', function() {
            modal.classList.remove('show');
        });

        // Theme selection event listeners
        const themeOptions = modal.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', function() {
                const themeKey = this.getAttribute('data-theme');
                applyTheme(themeKey);

                // Update active state
                themeOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');

                // Save theme preference
                localStorage.setItem('selectedTheme', themeKey);

                // Close modal after selection
                setTimeout(() => {
                    modal.classList.remove('show');
                }, 500);
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
        themeButton.innerHTML = '<i class="fas fa-palette"></i>';
        themeButton.title = 'Change Theme';

        themeButton.addEventListener('click', function() {
            const modal = document.getElementById('themeSelectorModal');
            if (modal) {
                modal.classList.add('show');
            }
        });

        document.body.appendChild(themeButton);
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
    }

    // Initialize theme selector
    function initThemeSelector() {
        createThemeSelector();
        createThemeButton();

        // Apply saved theme or default
        const savedTheme = localStorage.getItem('selectedTheme') || 'classic-light';
        applyTheme(savedTheme);
    }

    // Initialize
    initThemeSelector();
});
