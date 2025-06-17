function modalShown(event) {
    const button = event.relatedTarget;
    const meetingId = button.getAttribute('data-meeting-id');
    const meetingTitle = button.getAttribute('data-meeting-title');
    
    const modalRegMeeting = document.getElementById('modalRegMeeting');
    if (modalRegMeeting) {
        modalRegMeeting.textContent = meetingTitle;
    }
    
    const form = document.getElementById('createForm');
    form.action = `/users/${meetingId}/registrate`;
    
    const contactsInput = document.getElementById('contacts');
    if (contactsInput) {
        contactsInput.value = '';
    }
}

let modal = document.getElementById('createModal');
if (modal) {
    modal.addEventListener('show.bs.modal', modalShown);
}