SELECT 'User: test_user';
CREATE USER IF NOT EXISTS test_user;
SELECT 'Database: tx';
CREATE DATABASE tx;
GRANT ALL ON DATABASE tx TO test_user;
SELECT 'Table for fraud: txn';
CREATE TABLE tx.txn
(
    isfraud        INTEGER,
    istransfer     VARCHAR,
    amount         FLOAT,
    oldbalanceorg  FLOAT,
    newbalanceorig FLOAT,
    oldbalancedest FLOAT,
    newbalancedest FLOAT
);
SELECT 'Table for kickstarter: kickstart';
CREATE TABLE tx.kickstart
(
    category VARCHAR,
    main_category VARCHAR,
    deadline DATE,
    launched TIMESTAMP,
    state VARCHAR,
    backers INTEGER,
    country VARCHAR,
    usd_pledged FLOAT,
    usd_goal_real FLOAT
);
\q
