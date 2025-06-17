function modalShown(event) {
    const button = event.relatedTarget;
    const meetingId = button.getAttribute('data-meeting-id');
    const newUrl = `/users/${meetingId}/registrate`;
    const form = document.getElementById('deleteModalForm');
    
    // данные пользователя из data-атрибутов
    const meetingTitle = button.getAttribute('data-meeting-title');

    
    const modalRegMeeting = document.getElementById('modalRegMeeting');
    modalRegMeeting.textContent = `${meetingTitle}`;
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);