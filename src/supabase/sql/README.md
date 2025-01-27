# Supabase SQL Changes

This directory contains SQL files that need to be executed in the Supabase SQL Editor. Each file is prefixed with a number to indicate the order in which they should be run.

## File Naming Convention

- Files are prefixed with a number (e.g., `01_`, `02_`) to indicate execution order
- Use descriptive names after the prefix (e.g., `01_initial_setup.sql`, `02_add_categories.sql`)
- Include the creation date in the file header

## Making Changes

When you need to make database changes:

1. Create a new SQL file with the next available number prefix
2. Add a header comment with the date and description
3. Include both the changes and any necessary RLS policies
4. Test the changes in a development environment first
5. Run the SQL in the Supabase SQL Editor

## Common Operations

### Adding a New Table

```sql
-- Create the table
CREATE TABLE IF NOT EXISTS new_table (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Add your columns here
    user_id uuid REFERENCES auth.users(id) NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Enable RLS
ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;

-- Add updated_at trigger
CREATE OR REPLACE TRIGGER update_new_table_updated_at
    BEFORE UPDATE ON new_table
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Create RLS policies
CREATE POLICY "Users can view their own rows"
    ON new_table FOR SELECT
    USING (auth.uid() = user_id);
-- Add other policies as needed
```

### Modifying Tables

```sql
-- Add a column
ALTER TABLE table_name 
ADD COLUMN IF NOT EXISTS column_name data_type;

-- Rename a column
ALTER TABLE table_name 
RENAME COLUMN old_name TO new_name;

-- Modify a column
ALTER TABLE table_name 
ALTER COLUMN column_name TYPE new_data_type;
```

### Removing Tables or Columns

```sql
-- Remove a column
ALTER TABLE table_name 
DROP COLUMN IF EXISTS column_name;

-- Remove a table
DROP TABLE IF EXISTS table_name;
```
