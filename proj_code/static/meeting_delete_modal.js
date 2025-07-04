document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteModal');
    const deleteModal = new bootstrap.Modal(modal);
    
    modal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const meetingId = button.getAttribute('data-meeting-id');
        const meetingTitle = button.getAttribute('data-meeting-title');
        const nameSpan = document.getElementById('modalMeetingName');

        if (nameSpan) {
            nameSpan.textContent = meetingTitle;
        }
        const form = document.getElementById('deleteModalForm');
        if (form) {
            form.action = `/meetings/${meetingId}/delete`;
        }
    });
});