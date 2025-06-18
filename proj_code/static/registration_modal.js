document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('createModal');
    
    const registrationModal = new bootstrap.Modal(modalElement);
    
    // Обработчик для кнопок регистрации
    document.querySelectorAll('[data-bs-target="#createModal"]').forEach(button => {
        button.addEventListener('click', function() {
            const meetingId = this.getAttribute('data-meeting-id');
            const meetingTitle = this.getAttribute('data-meeting-title');
            
            // Обновляем содержимое модального окна
            const meetingSpan = document.getElementById('modalRegMeeting');
            if (meetingSpan) {
                meetingSpan.textContent = meetingTitle;
            }
            
            // Обновляем действие формы
            const form = document.getElementById('createForm');
            if (form) {
                form.action = `/users/${meetingId}/registrate`;
            }
            
            // Очищаем поле контактов
            const contactsInput = document.getElementById('contacts');
            if (contactsInput) {
                contactsInput.value = '';
            }
            
            // Показываем модальное окно
            registrationModal.show();
        });
    });
});