-- Initialize database and documents table for rag_app

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS rag_app;

-- Switch to the database
USE rag_app;

-- Create documents table if not exists
CREATE TABLE IF NOT EXISTS documents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL,
    embedding JSON NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optional: basic index to help lookups by id (primary key already covers it)
-- CREATE INDEX idx_documents_created_at ON documents(created_at);