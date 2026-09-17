CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    hash_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(100)
);

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description VARCHAR(255),
    priority INT,
    completed BOOLEAN DEFAULT FALSE,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);