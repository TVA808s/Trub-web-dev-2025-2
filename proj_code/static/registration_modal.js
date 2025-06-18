document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('createModal');
    
    if (!modalElement) {
        console.error('Registration modal element not found');
        return;
    }
    
    // Инициализируем модальное окно через Bootstrap
    const registrationModal = new bootstrap.Modal(modalElement);
    
    // Обработчик для кнопки регистрации
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