-- Example changes
-- Created: 2025-01-27

-- Example: Adding a new column
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS description TEXT;

-- Example: Renaming a column (if needed)
-- ALTER TABLE items 
-- RENAME COLUMN old_name TO new_name;

-- Example: Creating a new table
CREATE TABLE IF NOT EXISTS categories (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    user_id uuid REFERENCES auth.users(id) NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Enable RLS for new table
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Add updated_at trigger for new table
CREATE OR REPLACE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Create RLS policies for new table
CREATE POLICY "Users can view their own categories"
    ON categories
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own categories"
    ON categories
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own categories"
    ON categories
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own categories"
    ON categories
    FOR DELETE
    USING (auth.uid() = user_id);
