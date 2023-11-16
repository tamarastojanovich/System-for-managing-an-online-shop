CREATE DATABASE userInfo;

USE userInfo;

CREATE TABLE IF NOT EXISTS users(
    id INTEGER NOT NULL AUTO_INCREMENT,
    email VARCHAR(256) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    forename VARCHAR(256) NOT NULL,
    surname VARCHAR(256) NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS roles(
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL,
    PRIMARY KEY(ID)
);
CREATE TABLE IF NOT EXISTS userRole(
    id INTEGER NOT NULL AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    roleId INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(id),
    FOREIGN KEY (roleId) REFERENCES roles(id),
    PRIMARY KEY (id)
);

INSERT INTO roles (name) VALUES ('owner');

INSERT INTO roles (name) VALUES ('courier');

INSERT INTO roles (name) VALUES ('customer');

INSERT INTO users (email,password,forename,surname) 
VALUES ('onlymoney@gmail.com','evenmoremoney','Scrooge','McDuck');

INSERT INTO userRole (userId,roleId)
VALUES (1,1)
