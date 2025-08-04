// Vision Hub Tanzania - JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Initialize components
    initMobileMenu();
    initTabSystem();
    initSkillsSystem();
    initChatSystem();
    initWorkExperience();
    initFormValidation();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function () {
            mobileMenu.classList.toggle('show');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (event) {
            if (!mobileMenuToggle.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.remove('show');
            }
        });

        // Close menu when window is resized to desktop
        window.addEventListener('resize', function () {
            if (window.innerWidth >= 768) {
                mobileMenu.classList.remove('show');
            }
        });
    }
}

// Tab System for Join Form
function initTabSystem() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const nextButtons = document.querySelectorAll('[data-next]');
    const prevButtons = document.querySelectorAll('[data-prev]');

    let currentTab = 'personal';

    // Tab click handlers
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const tabId = this.getAttribute('data-tab');
            if (tabId) {
                showTab(tabId);
            }
        });
    });

    // Next button handlers
    nextButtons.forEach(button => {
        button.addEventListener('click', function () {
            const nextTab = this.getAttribute('data-next');
            if (validateCurrentTab(currentTab)) {
                showTab(nextTab);
            }
        });
    });

    // Previous button handlers
    prevButtons.forEach(button => {
        button.addEventListener('click', function () {
            const prevTab = this.getAttribute('data-prev');
            showTab(prevTab);
        });
    });

    function showTab(tabId) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.classList.remove('active');
        });

        // Deactivate all tabs
        tabs.forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab content
        const selectedContent = document.getElementById(`${tabId}-tab`);
        const selectedTab = document.querySelector(`[data-tab="${tabId}"]`);

        if (selectedContent && selectedTab) {
            selectedContent.classList.add('active');
            selectedTab.classList.add('active');
            currentTab = tabId;
            updateProgressBar(tabId);
        }
    }

    function updateProgressBar(tabId) {
        const tabs = ['personal', 'background', 'experience', 'motivation'];
        const currentIndex = tabs.indexOf(tabId);
        const progress = ((currentIndex + 1) / tabs.length) * 100;
        const progressBar = document.getElementById('form-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    function validateCurrentTab(tabId) {
        const tabContent = document.getElementById(`${tabId}-tab`);
        if (!tabContent) return true;

        const requiredFields = tabContent.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });

        if (!isValid) {
            showNotification('Please fill in all required fields before proceeding.', 'error');
        }

        return isValid;
    }
}

// Skills System
function initSkillsSystem() {
    const addSkillBtn = document.getElementById('add-skill');
    const newSkillInput = document.getElementById('new-skill-input');
    const skillsContainer = document.getElementById('skills-container');
    const skillsHidden = document.getElementById('skills-hidden');

    if (!addSkillBtn || !newSkillInput || !skillsContainer) return;

    let skills = [];

    addSkillBtn.addEventListener('click', addSkill);
    newSkillInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSkill();
        }
    });

    function addSkill() {
        const skillText = newSkillInput.value.trim();
        if (skillText && !skills.includes(skillText)) {
            skills.push(skillText);
            renderSkill(skillText);
            updateHiddenField();
            newSkillInput.value = '';
        }
    }

    function renderSkill(skillText) {
        const skillElement = document.createElement('div');
        skillElement.className = 'skill-tag';
        skillElement.innerHTML = `
            ${skillText}
            <button type="button" onclick="removeSkill('${skillText}', this)">×</button>
        `;
        skillsContainer.appendChild(skillElement);
    }

    function updateHiddenField() {
        if (skillsHidden) {
            skillsHidden.value = skills.join(',');
        }
    }

    // Global function for removing skills
    window.removeSkill = function (skillText, buttonElement) {
        skills = skills.filter(skill => skill !== skillText);
        buttonElement.parentElement.remove();
        updateHiddenField();
    };
}

// Work Experience System
function initWorkExperience() {
    const addExperienceBtn = document.getElementById('add-experience');
    const workExperienceContainer = document.getElementById('work-experience-container');

    if (!addExperienceBtn || !workExperienceContainer) return;

    let experienceCount = 1;

    addExperienceBtn.addEventListener('click', function () {
        experienceCount++;
        const newExperienceHtml = `
            <div class="work-experience-item mb-4 p-4 border border-gray-200 rounded">
                <div class="flex justify-between items-center mb-4">
                    <h4 class="font-medium">Experience ${experienceCount}</h4>
                    <button type="button" class="text-red-500 hover:text-red-700" onclick="removeExperience(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label for="job_title_${experienceCount}" class="block mb-1">Job Title</label>
                        <input type="text" id="job_title_${experienceCount}" name="job_title_${experienceCount}" class="form-control w-full">
                    </div>
                    <div>
                        <label for="company_${experienceCount}" class="block mb-1">Company/Organization</label>
                        <input type="text" id="company_${experienceCount}" name="company_${experienceCount}" class="form-control w-full">
                    </div>
                </div>
                <div class="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label for="start_date_${experienceCount}" class="block mb-1">Start Date</label>
                        <input type="date" id="start_date_${experienceCount}" name="start_date_${experienceCount}" class="form-control w-full">
                    </div>
                    <div>
                        <label for="end_date_${experienceCount}" class="block mb-1">End Date</label>
                        <input type="date" id="end_date_${experienceCount}" name="end_date_${experienceCount}" class="form-control w-full">
                    </div>
                </div>
                <div>
                    <label for="responsibilities_${experienceCount}" class="block mb-1">Responsibilities</label>
                    <textarea id="responsibilities_${experienceCount}" name="responsibilities_${experienceCount}" class="form-control w-full" rows="3"></textarea>
                </div>
            </div>
        `;
        workExperienceContainer.insertAdjacentHTML('beforeend', newExperienceHtml);
    });

    // Global function for removing work experience
    window.removeExperience = function (buttonElement) {
        buttonElement.closest('.work-experience-item').remove();
    };
}

// Chat System
function initChatSystem() {
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (!sendChatBtn || !chatInput || !chatMessages) return;

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText) {
            const messageElement = document.createElement('div');
            messageElement.className = 'message sent';
            messageElement.innerHTML = `<strong>You:</strong> ${messageText}`;
            chatMessages.appendChild(messageElement);
            chatInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Simulate a response (in real app, this would be handled by backend)
            setTimeout(() => {
                const responses = [
                    "Thanks for your message! A community moderator will respond soon.",
                    "Great question! Feel free to join our upcoming events for more discussions.",
                    "Welcome to the community chat! Don't forget to check out our events section."
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];

                const responseElement = document.createElement('div');
                responseElement.className = 'message received';
                responseElement.innerHTML = `<strong>Community Bot:</strong> ${randomResponse}`;
                chatMessages.appendChild(responseElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 1000);
        }
    }
}

// Form Validation
function initFormValidation() {
    const membershipForm = document.getElementById('membership-form');

    if (!membershipForm) return;

    // Real-time validation
    const inputs = membershipForm.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function () {
            validateField(this);
        });

        input.addEventListener('input', function () {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');

        // Remove previous validation classes
        field.classList.remove('error', 'success');

        if (isRequired && !value) {
            field.classList.add('error');
            return false;
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('error');
                return false;
            }
        }

        // Phone validation (basic)
        if (field.type === 'tel' && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                field.classList.add('error');
                return false;
            }
        }

        if (value) {
            field.classList.add('success');
        }

        return true;
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;

    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#27ae60';
            break;
        case 'error':
            notification.style.backgroundColor = '#e74c3c';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f39c12';
            break;
        default:
            notification.style.backgroundColor = '#3498db';
    }

    notification.textContent = message;

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        margin-left: 10px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    `;
    closeBtn.addEventListener('click', () => removeNotification(notification));
    notification.appendChild(closeBtn);

    // Add to DOM
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 5 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}

function removeNotification(notification) {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states to buttons
function addButtonLoading(button, text = 'Loading...') {
    const originalText = button.innerHTML;
    button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${text}`;
    button.disabled = true;

    return function () {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Event booking functionality (for community page)
document.addEventListener('click', function (e) {
    if (e.target.matches('.btn') && e.target.textContent.includes('Book Now')) {
        e.preventDefault();
        const removeLoading = addButtonLoading(e.target, 'Booking...');

        // Simulate booking process
        setTimeout(() => {
            removeLoading();
            showNotification('Event booking successful! Check your email for confirmation.', 'success');
        }, 2000);
    }
});

// Form submission with loading state
document.addEventListener('submit', function (e) {
    if (e.target.id === 'membership-form') {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            addButtonLoading(submitBtn, 'Submitting...');
        }
    }
});

// Card hover effects
function initCardEffects() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Initialize card effects after DOM is loaded
document.addEventListener('DOMContentLoaded', initCardEffects);

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if supported
if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', initLazyLoading);
}