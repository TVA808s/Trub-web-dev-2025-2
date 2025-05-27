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
    last_name VARCHAR(25) NOT NULL,
    middle_name VARCHAR(25) DEFAULT NULL,
    password VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE INNODB;


insert into roles (id, name, description) values 
    (1, 'admin', 'papachka');
    
INSERT INTO users (
    username,
    password,
    first_name,
    last_name,
    middle_name,
    role_id
) VALUES (
    'test_user',
    'password',
    'test',
    'tes',
    'te',
    1
);
