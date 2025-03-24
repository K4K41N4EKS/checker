CREATE DATABASE authdb;

\c authdb

CREATE TABLE users (
    username varchar(100) NOT NULL,
    password_hash varchar(255) NOT NULL,
    access_token varchar(250),
    refresh_token varchar(250),
    PRIMARY KEY(username)
);

CREATE UNIQUE INDEX users_username_key ON users USING btree ("username");
