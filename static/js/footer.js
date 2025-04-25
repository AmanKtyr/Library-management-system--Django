/**
 * Modern Professional Footer Enhancements
 * Adds interactive features to the footer
 */

document.addEventListener('DOMContentLoaded', function() {
    // Newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('.newsletter-input');
            const email = emailInput.value.trim();
            
            if (email) {
                // Show success message
                const formContainer = this.parentElement;
                const originalContent = formContainer.innerHTML;
                
                formContainer.innerHTML = `
                    <div class="newsletter-success">
                        <div class="newsletter-success-icon">
                            <i class="fas fa-check-circle fa-3x mb-3 text-success"></i>
                        </div>
                        <h5 class="text-white">Thank you for subscribing!</h5>
                        <p class="text-white-50">We've sent a confirmation email to <strong>${email}</strong>.</p>
                    </div>
                `;
                
                // Reset form after 5 seconds
                setTimeout(() => {
                    formContainer.innerHTML = originalContent;
                    initNewsletterForm(); // Re-initialize the form
                }, 5000);
                
                // In a real application, you would send the email to the server here
                console.log('Newsletter subscription for:', email);
            }
        });
    }
    
    // Function to re-initialize the newsletter form
    function initNewsletterForm() {
        const newsletterForm = document.querySelector('.newsletter-form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const emailInput = this.querySelector('.newsletter-input');
                const email = emailInput.value.trim();
                
                if (email) {
                    // Show success message
                    const formContainer = this.parentElement;
                    const originalContent = formContainer.innerHTML;
                    
                    formContainer.innerHTML = `
                        <div class="newsletter-success">
                            <div class="newsletter-success-icon">
                                <i class="fas fa-check-circle fa-3x mb-3 text-success"></i>
                            </div>
                            <h5 class="text-white">Thank you for subscribing!</h5>
                            <p class="text-white-50">We've sent a confirmation email to <strong>${email}</strong>.</p>
                        </div>
                    `;
                    
                    // Reset form after 5 seconds
                    setTimeout(() => {
                        formContainer.innerHTML = originalContent;
                        initNewsletterForm(); // Re-initialize the form
                    }, 5000);
                    
                    // In a real application, you would send the email to the server here
                    console.log('Newsletter subscription for:', email);
                }
            });
        }
    }
    
    // Social media hover effects
    const socialIcons = document.querySelectorAll('.social-icon');
    socialIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.1)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Footer links hover animation
    const footerLinks = document.querySelectorAll('.footer-links a');
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'translateX(3px)';
            }
        });
        
        link.addEventListener('mouseleave', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = '';
            }
        });
    });
    
    // Contact items hover effect
    const contactItems = document.querySelectorAll('.contact-item');
    contactItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.backgroundColor = 'var(--primary-color)';
                icon.style.color = 'white';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.backgroundColor = '';
                icon.style.color = '';
            }
        });
    });
    
    // Add year to copyright text
    const copyrightYear = document.querySelector('.copyright');
    if (copyrightYear) {
        const year = new Date().getFullYear();
        copyrightYear.innerHTML = copyrightYear.innerHTML.replace('{YEAR}', year);
    }
});
