/**
 * Netflix-style Behavioral Tracking for Job Feed Personalization
 * Tracks: time spent on jobs, saves, rejections, ignores
 */

(function () {
    'use strict';

    let pageLoadTime = Date.now();
    let jobId = null;
    let trackingEnabled = false;

    // Initialize tracking
    function initTracking() {
        // Get job ID from page (assumes data-job-id attribute on body or main element)
        const jobElement = document.querySelector('[data-job-id]');
        if (jobElement) {
            jobId = jobElement.getAttribute('data-job-id');
            trackingEnabled = true;

            // Track time spent when user leaves page
            window.addEventListener('beforeunload', trackTimeSpent);

            // Track time spent on visibility change (mobile/tab switching)
            document.addEventListener('visibilitychange', handleVisibilityChange);
        }

        // Setup preference tracking buttons
        setupPreferenceButtons();
    }

    function trackTimeSpent() {
        if (!trackingEnabled || !jobId) return;

        const timeSpent = Math.floor((Date.now() - pageLoadTime) / 1000);

        // Only track if user spent at least 3 seconds
        if (timeSpent < 3) return;

        // Use sendBeacon for reliable tracking on page unload
        const data = JSON.stringify({
            job_id: jobId,
            time_spent_seconds: timeSpent,
            source: getSource()
        });

        const csrfToken = getCookie('csrftoken');
        const blob = new Blob([data], { type: 'application/json' });

        // Try sendBeacon first (more reliable), fallback to fetch
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/jobs/api/track-view/', blob);
        } else {
            fetch('/jobs/api/track-view/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: data,
                keepalive: true
            }).catch(err => console.error('Tracking failed:', err));
        }
    }

    function handleVisibilityChange() {
        if (document.hidden) {
            trackTimeSpent();
        } else {
            // Reset timer when user comes back
            pageLoadTime = Date.now();
        }
    }

    function setupPreferenceButtons() {
        // Save job button
        const saveButtons = document.querySelectorAll('[data-action="save-job"]');
        saveButtons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const jobId = this.getAttribute('data-job-id');
                trackPreference(jobId, 'saved');
            });
        });

        // Not interested / Reject button
        const rejectButtons = document.querySelectorAll('[data-action="reject-job"]');
        rejectButtons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const jobId = this.getAttribute('data-job-id');
                trackPreference(jobId, 'rejected');

                // Hide the job card
                const jobCard = this.closest('.job-card, .card');
                if (jobCard) {
                    jobCard.style.opacity = '0.5';
                    setTimeout(() => jobCard.remove(), 300);
                }
            });
        });

        // Ignore button (passive disinterest)
        const ignoreButtons = document.querySelectorAll('[data-action="ignore-job"]');
        ignoreButtons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const jobId = this.getAttribute('data-job-id');
                trackPreference(jobId, 'ignored');
            });
        });
    }

    function trackPreference(jobId, preferenceType) {
        const csrfToken = getCookie('csrftoken');

        fetch('/jobs/api/track-preference/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                job_id: jobId,
                preference_type: preferenceType
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    console.log(`Preference tracked: ${preferenceType}`);

                    // Show feedback message
                    showFeedback(preferenceType);
                }
            })
            .catch(err => console.error('Preference tracking failed:', err));
    }

    function showFeedback(preferenceType) {
        const messages = {
            'saved': 'Job saved! We\'ll show you more like this.',
            'rejected': 'Got it. We\'ll show you fewer jobs like this.',
            'ignored': 'Noted. Adjusting your recommendations.'
        };

        const message = messages[preferenceType] || 'Preference saved.';

        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'tracking-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 24px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function getSource() {
        const params = new URLSearchParams(window.location.search);
        return params.get('source') || 'direct';
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTracking);
    } else {
        initTracking();
    }
})();
