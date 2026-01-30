-- Clean up script for Avocarbon Pricing App Database

-- Option 1: Delete all data (COMPLETE RESET)
-- This will delete in the correct order to avoid foreign key conflicts:

-- 1. Delete all notifications first (if any)
DELETE FROM notifications;

-- 2. Delete all comments
DELETE FROM comments;

-- 3. Delete all pricing requests
DELETE FROM pricing_requests;

-- Reset auto-increment counters (PostgreSQL):
ALTER SEQUENCE comments_id_seq RESTART WITH 1;
ALTER SEQUENCE pricing_requests_id_seq RESTART WITH 1;
ALTER SEQUENCE notifications_id_seq RESTART WITH 1;

-- Verify tables are empty
SELECT COUNT(*) as notifications_count FROM notifications;
SELECT COUNT(*) as comments_count FROM comments;
SELECT COUNT(*) as requests_count FROM pricing_requests;

-- ============================================================

-- Option 2: Delete SPECIFIC REQUEST and its comments
-- Replace 13 with the actual request ID:

-- DELETE FROM comments WHERE request_id = 13;
-- DELETE FROM pricing_requests WHERE id = 13;

-- ============================================================

-- Option 3: If you want to keep some data, delete comments for specific requests
-- Example: Delete comments for requests with no decision (still UNDER_REVIEW_PL)

-- DELETE FROM comments 
-- WHERE request_id IN (
--     SELECT id FROM pricing_requests 
--     WHERE status = 'UNDER_REVIEW_PL'
-- );
-- DELETE FROM pricing_requests WHERE status = 'UNDER_REVIEW_PL';

-- ============================================================

-- Show remaining data after cleanup:
SELECT 'Pricing Requests' as table_name, COUNT(*) as count FROM pricing_requests
UNION ALL
SELECT 'Comments', COUNT(*) FROM comments
UNION ALL
SELECT 'Notifications', COUNT(*) FROM notifications;
