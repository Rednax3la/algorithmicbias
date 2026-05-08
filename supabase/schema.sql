-- ============================================================
-- Digital Credit Bias Audit + Personal Credit Health Tool
-- Supabase Schema
-- Run this in the Supabase SQL editor
-- ============================================================

-- Users are handled by Supabase Auth (auth.users table built-in)

-- User profiles (financial information)
CREATE TABLE profiles (
    id uuid REFERENCES auth.users(id) PRIMARY KEY,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    -- Demographics
    age int,
    gender text CHECK (gender IN ('M', 'F', 'Other')),
    county text,
    location_type text CHECK (location_type IN ('Urban', 'Rural')),
    education text,
    employment_status text,
    -- Financial
    monthly_income float,
    mpesa_transactions_monthly int,
    avg_transaction_amount float,
    account_age_months int,
    previous_loans int,
    repayment_rate float,
    -- Device
    device_type text,
    app_usage_days int,
    platform_connections int,
    -- Consent
    data_anonymized_consent boolean DEFAULT false
);

-- Credit assessments (history of scores for each user)
CREATE TABLE assessments (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id),
    created_at timestamptz DEFAULT now(),
    credit_score float,
    approval_probability float,
    approved boolean,
    -- Score breakdown
    income_contribution float,
    repayment_contribution float,
    account_age_contribution float,
    transaction_contribution float,
    location_penalty float,
    device_penalty float,
    gender_penalty float,
    score_without_bias float,
    -- Model outputs
    model_used text DEFAULT 'random_forest',
    top_features jsonb
);

-- Anonymized aggregate data for research dashboard
-- Populated from profiles where data_anonymized_consent = true
CREATE TABLE anonymized_data (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamptz DEFAULT now(),
    -- Demographic buckets (not exact values for privacy)
    age_group text,      -- '18-25', '26-35', '36-45', '46-55', '56-65'
    gender text,
    county text,
    location_type text,
    education text,
    employment_status text,
    income_bracket text, -- 'below_20k', '20k-50k', '50k-100k', 'above_100k'
    device_tier text,    -- 'feature', 'budget', 'mid', 'high'
    -- Assessment results
    credit_score float,
    approved boolean,
    bias_total float
);

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read/write own profile"
    ON profiles FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can only read/write own assessments"
    ON assessments FOR ALL USING (auth.uid() = user_id);

-- anonymized_data is readable by everyone (it's aggregate/anonymous)
ALTER TABLE anonymized_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read anonymized data"
    ON anonymized_data FOR SELECT USING (true);

-- Allow service role to insert into anonymized_data
CREATE POLICY "Service role can insert anonymized data"
    ON anonymized_data FOR INSERT WITH CHECK (true);

-- Trigger to auto-update updated_at on profiles
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
