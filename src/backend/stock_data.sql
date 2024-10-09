CREATE DATABASE IF NOT EXISTS stock_info;

USE stock_info;

CREATE TABLE IF NOT EXISTS stock_exchange (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    date DATE,
    low FLOAT,
    open FLOAT,
    volume BIGINT,
    high FLOAT,
    close FLOAT,
    adjusted_close FLOAT,
    stock_exchange_id INT,
    FOREIGN KEY (stock_exchange_id) REFERENCES stock_exchange(id)
);

INSERT INTO stock_exchange (name)
VALUES ('forbes2000');
INSERT INTO stock_exchange (name)
VALUES ('nasdaq');
INSERT INTO stock_exchange (name)
VALUES ('nyse');
INSERT INTO stock_exchange (name)
VALUES ('sp500');


-- SELECT *
-- FROM stock_exchange;

-- SELECT *
-- FROM stock_data;


-- SHOW DATABASES;

-- DROP DATABASE stock_info
