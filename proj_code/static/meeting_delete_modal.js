
document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('deleteModal');
    
    if (!modalElement) {
        return 1;
    }
    
    // Инициализируем модальное окно через Bootstrap
    const deleteModal = new bootstrap.Modal(modalElement);
    
    // Обработчик для кнопки удаления
    document.querySelectorAll('[data-bs-target="#deleteModal"]').forEach(button => {
        button.addEventListener('click', function() {
            const meetingId = this.getAttribute('data-meeting-id');
            const meetingTitle = this.getAttribute('data-meeting-title');
            
            // Обновляем содержимое модального окна
            const nameSpan = document.getElementById('modalMeetingName');
            if (nameSpan) {
                nameSpan.textContent = meetingTitle;
            }
            
            // Обновляем действие формы
            const form = document.getElementById('deleteModalForm');
            if (form) {
                form.action = `/users/${meetingId}/delete`;
            }
            
            // Показываем модальное окно
            deleteModal.show();
        });
    });
});