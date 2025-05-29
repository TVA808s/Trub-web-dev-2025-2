'use strict';

function modalShown(event) {
    const button = event.relatedTarget;
    const userId = button.getAttribute('data-user-id');
    const newUrl = `/users/${userId}/delete`;
    const form = document.getElementById('deleteModalForm');
    
    // данные пользователя из data-атрибутов
    const lastName = button.getAttribute('data-last-name');
    const firstName = button.getAttribute('data-first-name');
    const middleName = button.getAttribute('data-middle-name');
    
    const modalUserName = document.getElementById('modalUserName');
    modalUserName.textContent = `${lastName} ${firstName} ${middleName}`;
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);