DROP TABLE IF EXISTS registration_table;
DROP TABLE IF EXISTS visit_logs;
DROP TABLE IF EXISTS meetings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INT PRIMARY KEY,
    name VARCHAR(16) NOT NULL,
    description TEXT
) ENGINE INNODB;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(32) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    last_name VARCHAR(16) NOT NULL,
    first_name VARCHAR(16) NOT NULL,
    middle_name VARCHAR(16) DEFAULT NULL,
    role INT NOT NULL,
    FOREIGN KEY (role) REFERENCES roles(id)
) ENGINE INNODB;

CREATE TABLE meetings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    place VARCHAR(64) NOT NULL,
    volunteers_amount INT NOT NULL,
    image VARCHAR(128) NOT NULL,
    organizer INT NOT NULL,
    FOREIGN KEY (organizer) REFERENCES users(id)
) ENGINE INNODB;

CREATE TABLE registration_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    meeting INT NOT NULL,
    FOREIGN KEY (meeting) REFERENCES meetings(id),
    volunteer INT NOT NULL,
    FOREIGN KEY (volunteer) REFERENCES users(id),
    contacts VARCHAR(64) NOT NULL,
    date TIMESTAMP NOT NULL,
    status VARCHAR(16) NOT NULL
);


insert into roles (id, name, description) values 
    (1, 'Администратор', 'пахан'),
    (2, 'Модератор', 'валет'),
    (3, 'Пользователь', 'нормис');
    
INSERT INTO users (
    login,
    password,
    last_name,
    first_name,
    middle_name,
    role
) VALUES (
    'admin',
    '19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd',
    'АДМИН',
    'АДМИНИСТЕР',
    'АДМИНИСТЕРИСТО',
    1
),
    (
    'moder',
    '19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd',
    'МОДЕР',
    'МОДЕРЕСКО',
    'МОДЕРНЫСКИЙ',
    2
),
    (
    'user',
    '19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd',
    'ЮЗЕР',
    'ЮЗЕРАЛИ',
    'ЮЗЕРИСКНИК',
    3
);

INSERT INTO meetings (title, description, date, place, volunteers_amount, image, organizer)
VALUES
('Уборка парка', 'Генеральная уборка Центрального городского парка', '2025-05-15', 'Центральный парк', 5, 'park_cleanup.jpg', 1),
('Помощь приюту для животных', 'Кормление животных и уборка вольеров', '2025-08-02', 'Приют "Добрые руки"', 1, 'animal_shelter.jpg', 1),
('Благотворительный забег', 'Ежегодный забег в поддержку детских домов', '2025-09-21', 'Городской стадион', 3, 'charity_run.jpg', 1),
('Обучение пожилых людей', 'Базовый курс компьютерной грамотности', '2025-07-30', 'Библиотека №5', 2, 'seniors_course.jpg', 1),
('Экологическая акция', 'Сбор пластика и макулатуры в микрорайоне', '2025-06-24', 'Сквер у фонтана', 4, 'eco_action.jpg', 1);


INSERT INTO registration_table (meeting, volunteer, contacts, date, status)
VALUES
(1, 3, 'user@example.com', '2024-07-01 10:00:00', 'подтверждено'),
(1, 2, 'moder@example.com', '2024-07-02 11:30:00', 'подтверждено');

INSERT INTO registration_table (meeting, volunteer, contacts, date, status)
VALUES
(2, 1, 'user@example.com', '2024-07-10 09:45:00', 'подтверждено');

INSERT INTO registration_table (meeting, volunteer, contacts, date, status)
VALUES
(3, 1, 'admin@example.com', '2024-08-01 12:30:00', 'подтверждено'),
(3, 2, 'moder@example.com', '2024-08-02 13:45:00', 'подтверждено'),
(3, 3, 'user@example.com', '2024-08-03 10:15:00', 'подтверждено');

INSERT INTO registration_table (meeting, volunteer, contacts, date, status)
VALUES
(4, 2, 'user@example.com', '2024-07-15 14:00:00', 'подтверждено');

INSERT INTO registration_table (meeting, volunteer, contacts, date, status)
VALUES
(5, 3, 'user@example.com', '2024-07-22 09:45:00', 'подтверждено');