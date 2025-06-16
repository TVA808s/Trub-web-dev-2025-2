'use strict';

function modalShown(event) {
    const button = event.relatedTarget;
    const meetingId = button.getAttribute('data-meeting-id');
    const newUrl = `/users/${meetingId}/delete`;
    const form = document.getElementById('deleteModalForm');
    
    // данные пользователя из data-атрибутов
    const meetingTitle = button.getAttribute('data-meeting-title');

    
    const modalUserName = document.getElementById('modalMeetingName');
    modalUserName.textContent = `${meetingTitle}`;
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);