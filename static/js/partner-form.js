/**
 * Enterprise Partner Form JavaScript
 * Handles the enterprise partner form modal and submission
 * Designed for professional, modern, and industrial use
 */

// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enterprise partner form script loaded');

    // Get DOM elements
    const becomePartnerBtn = document.getElementById('becomePartnerBtn');
    const partnerModal = document.getElementById('partnerModal');
    const partnerForm = document.getElementById('partnerForm');
    const submitPartnerFormBtn = document.getElementById('submitPartnerForm');

    // Initialize modal using Bootstrap 5
    if (partnerModal) {
        console.log('Enterprise partner modal found');
        // We're using data-bs-toggle and data-bs-target attributes for modal triggering
    }

    // Form validation and submission
    if (partnerForm && submitPartnerFormBtn) {
        console.log('Enterprise partner form and submit button found');

        // Add click event listener to submit button
        submitPartnerFormBtn.addEventListener('click', function() {
            console.log('Submit button clicked');
            validateAndSubmitEnterpriseForm();
        });

        // Also add jQuery handler for better cross-browser compatibility
        $(submitPartnerFormBtn).on('click', function() {
            console.log('Submit button clicked (jQuery)');
            validateAndSubmitEnterpriseForm();
        });
    }

    // Enterprise form validation and submission function
    function validateAndSubmitEnterpriseForm() {
        let isValid = true;

        // Clear previous validation states
        $(partnerForm).find('.is-invalid').removeClass('is-invalid');
        $(partnerForm).find('.is-valid').removeClass('is-valid');

        // Validate all required fields
        $(partnerForm).find('[required]').each(function() {
            if (!this.value || (this.type === 'checkbox' && !this.checked)) {
                isValid = false;
                $(this).addClass('is-invalid');

                // If it's a select inside an input group, add the class to the parent
                if ($(this).parent().hasClass('input-group')) {
                    $(this).parent().addClass('is-invalid');
                }
            } else {
                $(this).addClass('is-valid');

                // If it's a select inside an input group, add the class to the parent
                if ($(this).parent().hasClass('input-group')) {
                    $(this).parent().addClass('is-valid');
                }
            }
        });

        // Validate interest checkboxes (at least one must be selected)
        let interestSelected = false;
        $('.interest-checkbox').each(function() {
            if (this.checked) {
                interestSelected = true;
            }
        });

        if (!interestSelected) {
            isValid = false;
            $('.interest-checkbox').addClass('is-invalid');
            $('#interestsValidationFeedback').show();
        } else {
            $('.interest-checkbox').removeClass('is-invalid');
            $('#interestsValidationFeedback').hide();
        }

        // If the form is valid, proceed with submission
        if (isValid) {
            console.log('Enterprise form is valid, submitting');

            // Show loading state on the submit button
            submitPartnerFormBtn.disabled = true;
            submitPartnerFormBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

            // Collect form data for submission
            const formData = {
                institution: {
                    name: $('#institutionName').val(),
                    type: $('#institutionType').val(),
                    city: $('#institutionLocation').val(),
                    state: $('#institutionState').val(),
                    collectionSize: $('#institutionSize').val(),
                    staffSize: $('#staffSize').val(),
                    currentSystem: $('#currentSystem').val(),
                    implementationTimeframe: $('#implementationTimeframe').val()
                },
                contact: {
                    name: $('#contactName').val(),
                    position: $('#contactPosition').val(),
                    email: $('#contactEmail').val(),
                    phone: $('#contactPhone').val()
                },
                interests: [],
                additionalInfo: $('#additionalInfo').val(),
                demoRequested: $('#demoRequest').is(':checked'),
                privacyConsent: $('#privacyConsent').is(':checked')
            };

            // Collect all selected interests
            $('.interest-checkbox:checked').each(function() {
                formData.interests.push($(this).val());
            });

            console.log('Form data collected:', formData);

            // Simulate form submission with a delay (replace with actual AJAX submission)
            setTimeout(function() {
                // Get institution name for personalized message
                const institutionName = formData.institution.name;
                const contactName = formData.contact.name;

                // Hide the modal
                $(partnerModal).modal('hide');

                // Create success message with enterprise styling
                const successAlert = $(`
                    <div class="alert-modern alert-modern-success fade-in">
                        <div class="alert-modern-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="alert-modern-content">
                            <h5 class="alert-modern-title">Enterprise Partnership Application Received!</h5>
                            <p>Thank you, ${contactName} from ${institutionName}! Your enterprise partnership application has been successfully submitted. Our India-based team will contact you within 24 hours to discuss your specific requirements and next steps.</p>
                            ${formData.demoRequested ? '<p><strong>Note:</strong> We\'ve received your request for a personalized demo and will schedule it during our initial consultation call.</p>' : ''}
                        </div>
                        <button type="button" class="alert-modern-close" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `);

                // Add the success message to the page
                const alertContainer = $('<div class="container mt-3"></div>').append(successAlert);
                $('main').prepend(alertContainer);

                // Add close button functionality
                successAlert.find('.alert-modern-close').on('click', function() {
                    successAlert.addClass('fade-out');
                    setTimeout(function() {
                        alertContainer.remove();
                    }, 500);
                });

                // Scroll to the top of the page to show the message
                $('html, body').animate({
                    scrollTop: 0
                }, 500);

                // Auto close the message after 15 seconds
                setTimeout(function() {
                    successAlert.addClass('fade-out');
                    setTimeout(function() {
                        alertContainer.remove();
                    }, 500);
                }, 15000);

                // Reset the form and restore the submit button
                partnerForm.reset();
                submitPartnerFormBtn.disabled = false;
                submitPartnerFormBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Application';

                // Remove all validation classes
                $(partnerForm).find('.is-valid, .is-invalid').removeClass('is-valid is-invalid');

            }, 2000); // 2 second delay to simulate server processing
        } else {
            // If form is invalid, scroll to the first invalid element
            const firstInvalid = $(partnerForm).find('.is-invalid:first');
            if (firstInvalid.length) {
                // Find the closest section header for better UX
                const closestHeader = firstInvalid.closest('.col-12').prev('.col-12').find('h5');

                // If there's a section header, scroll to it, otherwise scroll to the invalid field
                if (closestHeader.length) {
                    $('html, body').animate({
                        scrollTop: closestHeader.offset().top - 100
                    }, 500);
                } else {
                    $('html, body').animate({
                        scrollTop: firstInvalid.offset().top - 100
                    }, 500);
                }
            }
        }
    }

    // Add event listeners for form fields
    if (partnerForm) {
        // Handle regular inputs and selects
        $(partnerForm).find('input:not(.interest-checkbox), select, textarea').on('input change', function() {
            $(this).removeClass('is-invalid').addClass('is-valid');

            // If it's inside an input group, handle the parent too
            if ($(this).parent().hasClass('input-group')) {
                $(this).parent().removeClass('is-invalid').addClass('is-valid');
            }
        });

        // Handle interest checkboxes
        $('.interest-checkbox').on('change', function() {
            // Check if any checkbox is checked
            if ($('.interest-checkbox:checked').length > 0) {
                $('.interest-checkbox').removeClass('is-invalid');
                $('#interestsValidationFeedback').hide();
            }
        });

        // Add special handling for the demo request checkbox
        $('#demoRequest').on('change', function() {
            if ($(this).is(':checked')) {
                // Add a subtle highlight effect when demo is requested
                $(this).closest('.form-check').addClass('demo-requested');
            } else {
                $(this).closest('.form-check').removeClass('demo-requested');
            }
        });
    }

    // Add a CSS class to style the demo request when checked
    const style = document.createElement('style');
    style.textContent = `
        .demo-requested {
            background-color: rgba(37, 99, 235, 0.05);
            padding: 10px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
});
