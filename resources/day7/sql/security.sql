CREATE TABLE IF NOT EXISTS parcel_users (
    username VARCHAR(100) PRIMARY KEY,
    role VARCHAR(50) NOT NULL
);

-- Unsafe pattern (do not use):
-- SELECT * FROM parcel_users WHERE username = '<user_input>';
-- Input such as ' OR '1'='1 can alter the SQL logic.

-- Safe parameterized query:
PREPARE find_user(TEXT) AS
    SELECT username, role
    FROM parcel_users
    WHERE username = $1;

INSERT INTO parcel_users VALUES ('masthan', 'admin')
ON CONFLICT (username)
DO UPDATE SET role = EXCLUDED.role;

-- Normal input
EXECUTE find_user('masthan');

-- Injection-like input is treated as a literal value
EXECUTE find_user($$' OR '1'='1$$);

DEALLOCATE find_user;

-- Verify UPSERT
SELECT * FROM parcel_users;
