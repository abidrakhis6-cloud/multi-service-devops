-- Initialization script for PostgreSQL
-- This script runs on first container startup

-- Create additional databases if needed
-- CREATE DATABASE multiserve_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search

-- Note: Django migrations will create tables
-- This script can be used for:
-- 1. Creating extensions
-- 2. Setting up initial users/roles
-- 3. Creating additional databases
