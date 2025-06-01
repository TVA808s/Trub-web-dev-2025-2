DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INT PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    description TEXT
) ENGINE INNODB;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(25) UNIQUE NOT NULL,
    first_name VARCHAR(25) NOT NULL,
    last_name VARCHAR(25) DEFAULT NULL,
    middle_name VARCHAR(25) NOT NULL,
    password VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE INNODB;


insert into roles (id, name, description) values 
    (1, 'Администратор', 'папачка'),
    (2, 'Пользователь', 'нормис');
    
INSERT INTO users (
    username,
    password,
    first_name,
    last_name,
    middle_name,
    role_id
) VALUES (
    'admin_user',
    '19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd',
    'awaw',
    'rer',
    'xx',
    1
),
    (
    'simple_user',
    '19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd',
    'pwq',
    'awd',
    'ppp',
    2
);
