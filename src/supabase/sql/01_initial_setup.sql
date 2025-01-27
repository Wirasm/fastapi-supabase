-- Initial database setup
-- Created: 2025-01-27

-- Enable RLS
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- Create items table if it doesn't exist
CREATE TABLE IF NOT EXISTS items (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    test_data jsonb NOT NULL,
    user_id uuid REFERENCES auth.users(id) NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Create RLS policies
CREATE POLICY "Users can view their own items"
    ON items
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own items"
    ON items
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own items"
    ON items
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own items"
    ON items
    FOR DELETE
    USING (auth.uid() = user_id);
