CREATE DATABASE IF NOT EXISTS hotel_db;

USE hotel_db;

CREATE TABLE IF NOT EXISTS guests (
    guest_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number INT UNIQUE NOT NULL,
    room_type VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status ENUM('Available', 'Booked') DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('Booked', 'Checked Out') DEFAULT 'Booked',

    FOREIGN KEY (guest_id)
        REFERENCES guests(guest_id),

    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)
);

INSERT INTO rooms
(room_number, room_type, price, status)
VALUES
(101, 'Single', 1500.00, 'Available'),
(102, 'Double', 2500.00, 'Available'),
(103, 'Deluxe', 4000.00, 'Available'),
(104, 'Single', 1500.00, 'Available'),
(105, 'Double', 2500.00, 'Available');
