-- SuperBryn AI Voice Agent - Supabase Database Setup
-- Run this script in your Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USER PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    contact_number TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_contact ON user_profiles(contact_number);

-- ============================================
-- 2. APPOINTMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_number TEXT NOT NULL REFERENCES user_profiles(contact_number) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'modified')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint to prevent double-booking (only for active appointments)
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_slot 
ON appointments(appointment_date, appointment_time) 
WHERE status = 'active';

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_appointments_contact ON appointments(contact_number);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_datetime ON appointments(appointment_date, appointment_time);

-- ============================================
-- 3. CONVERSATION SUMMARIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    contact_number TEXT REFERENCES user_profiles(contact_number) ON DELETE SET NULL,
    summary TEXT NOT NULL,
    appointments_mentioned JSONB DEFAULT '[]'::jsonb,
    user_preferences TEXT,
    cost_breakdown JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for session lookups
CREATE INDEX IF NOT EXISTS idx_summaries_session ON conversation_summaries(session_id);
CREATE INDEX IF NOT EXISTS idx_summaries_contact ON conversation_summaries(contact_number);

-- ============================================
-- 4. FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for user_profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for appointments
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;
CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert a test user
INSERT INTO user_profiles (contact_number, name, email) 
VALUES ('1234567890', 'Test User', 'test@example.com')
ON CONFLICT (contact_number) DO NOTHING;

-- ============================================
-- 6. ROW LEVEL SECURITY (Optional but recommended)
-- ============================================

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_summaries ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for service role - adjust as needed)
CREATE POLICY "Enable all access for service role" ON user_profiles
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON appointments
    FOR ALL USING (true);

CREATE POLICY "Enable all access for service role" ON conversation_summaries
    FOR ALL USING (true);

-- ============================================
-- SETUP COMPLETE
-- ============================================
-- You can now use these tables in your application!
-- Next steps:
-- 1. Run this script in Supabase SQL Editor
-- 2. Verify tables were created in Table Editor
-- 3. Configure your backend with Supabase credentials
