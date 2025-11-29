-- Lab Tests Table Schema
CREATE TABLE IF NOT EXISTS lab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    date_slot VARCHAR(50) NOT NULL, -- Format: 'DD-MM-YYYY HH24:MI'
    is_available BOOLEAN DEFAULT TRUE,
    patient_to_attend VARCHAR(20),
    price DECIMAL(10, 2) NOT NULL,
    prerequisites TEXT,
    estimated_duration_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_lab_tests_date_slot ON lab_tests(date_slot);
CREATE INDEX IF NOT EXISTS idx_lab_tests_availability ON lab_tests(is_available, date_slot);
CREATE INDEX IF NOT EXISTS idx_lab_tests_patient ON lab_tests(patient_to_attend);

-- Bookings table to track confirmed bookings with payment status
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    booking_type VARCHAR(50) NOT NULL, -- 'doctor_appointment' or 'lab_test'
    booking_reference VARCHAR(100) UNIQUE NOT NULL,
    patient_id VARCHAR(20) NOT NULL,
    doctor_name VARCHAR(255), -- NULL for lab tests
    test_name VARCHAR(255), -- NULL for doctor appointments
    date_slot VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_confirmation', -- 'pending_confirmation', 'confirmed', 'payment_pending', 'paid', 'completed', 'cancelled'
    amount DECIMAL(10, 2),
    payment_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    payment_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    paid_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bookings_patient ON bookings(patient_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_reference ON bookings(booking_reference);

