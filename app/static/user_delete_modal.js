'use strict';

function modalShown(event) {
    let button = event.relatedTarget;
    let userId = button.dataset.userId;
    let newUrl = `/users/${userId}/delete`;
    let form = document.getElementById('deleteModalForm');
    let row = button.closest('tr');
    let lastName = row.querySelector('td:nth-child(3)').textContent;
    let Name = row.querySelector('td:nth-child(4)').textContent;
    let middleName = row.querySelector('td:nth-child(5)').textContent;
    let modalUserName = document.getElementById('modalUserName');
    modalUserName.textContent = lastName + " " + Name + " " + middleName;
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);