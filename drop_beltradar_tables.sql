-- Drop all beltradar tables and reset migration history
-- Run this when migrations are irreversible and you need a clean slate.
-- After running this, execute: python manage.py migrate beltradar

SET FOREIGN_KEY_CHECKS = 0;

-- Beltradar tables
DROP TABLE IF EXISTS `beltradar_beltsurveyentry`;
DROP TABLE IF EXISTS `beltradar_beltsurveysession`;
DROP TABLE IF EXISTS `beltradar_beltsurveysnapshot`;
DROP TABLE IF EXISTS `beltradar_beltsurveysnapshot_asteroids`;
DROP TABLE IF EXISTS `beltradar_belttimer`;
DROP TABLE IF EXISTS `beltradar_evemarketprice`;
DROP TABLE IF EXISTS `beltradar_usersettings`;

SET FOREIGN_KEY_CHECKS = 1;

-- Clear migration history so Django will re-apply from scratch
DELETE FROM django_migrations WHERE app = 'beltradar';
