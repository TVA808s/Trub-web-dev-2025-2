document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('createModal');
    const registrationModal = new bootstrap.Modal(modalElement);

    document.querySelectorAll('[data-bs-target="#createModal"]').forEach(button => {
        button.addEventListener('click', function() {
            const meetingId = this.getAttribute('data-meeting-id');
            const meetingTitle = this.getAttribute('data-meeting-title');
            const meetingSpan = document.getElementById('modalRegMeeting');

            if (meetingSpan) {
                meetingSpan.textContent = meetingTitle;
            }
            const form = document.getElementById('createForm');
            if (form) {
                form.action = `/users/${meetingId}/registrate`;
            }
            const contactsInput = document.getElementById('contacts');
            if (contactsInput) {
                contactsInput.value = '';
            }
            registrationModal.show();
        });
    });
});