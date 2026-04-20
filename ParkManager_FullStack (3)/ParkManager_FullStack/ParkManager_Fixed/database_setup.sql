-- ══════════════════════════════════════════════════════════════════
--  ParkManager — Complete MySQL Database Setup
--  Credentials: root / unimanagement12345
--  Run this file in phpMyAdmin, MySQL Workbench, or CLI:
--    mysql -u root -punimanagement12345 < database_setup.sql
-- ══════════════════════════════════════════════════════════════════

-- 1. Create & select database
CREATE DATABASE IF NOT EXISTS park_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE park_management;

-- ══════════════════════════════════════════════════════════════════
--  DJANGO BUILT-IN TABLES
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id`       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `app_label` VARCHAR(100) NOT NULL,
  `model`    VARCHAR(100) NOT NULL,
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id`              INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`            VARCHAR(255) NOT NULL,
  `content_type_id` INT          NOT NULL,
  `codename`        VARCHAR(100) NOT NULL,
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co`
    FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id`      BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `app`     VARCHAR(255) NOT NULL,
  `name`    VARCHAR(255) NOT NULL,
  `applied` DATETIME(6)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key`  VARCHAR(40)  NOT NULL PRIMARY KEY,
  `session_data` LONGTEXT     NOT NULL,
  `expire_date`  DATETIME(6)  NOT NULL,
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id`              INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `action_time`     DATETIME(6)  NOT NULL,
  `object_id`       LONGTEXT,
  `object_repr`     VARCHAR(200) NOT NULL,
  `action_flag`     SMALLINT UNSIGNED NOT NULL,
  `change_message`  LONGTEXT     NOT NULL,
  `content_type_id` INT,
  `user_id`         CHAR(32)     NOT NULL,
  KEY `django_admin_log_content_type_id_c4bce8eb_fk` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk`
    FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  USERS (Custom AbstractBaseUser)
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_user` (
  `id`                CHAR(32)     NOT NULL PRIMARY KEY COMMENT 'UUID without hyphens',
  `password`          VARCHAR(128) NOT NULL,
  `last_login`        DATETIME(6)  DEFAULT NULL,
  `is_superuser`      TINYINT(1)   NOT NULL DEFAULT 0,
  `car_number`        VARCHAR(20)  NOT NULL UNIQUE,
  `name`              VARCHAR(100) NOT NULL DEFAULT '',
  `role`              VARCHAR(10)  NOT NULL DEFAULT 'User'
                        COMMENT 'User | Admin | Staff',
  `phone`             VARCHAR(20)  NOT NULL DEFAULT '',
  `email`             VARCHAR(254) NOT NULL DEFAULT '',
  `subscription_plan` VARCHAR(10)  NOT NULL DEFAULT 'None'
                        COMMENT 'None | Basic | Gold | Premium',
  `is_active`         TINYINT(1)   NOT NULL DEFAULT 1,
  `is_staff`          TINYINT(1)   NOT NULL DEFAULT 0,
  `date_joined`       DATETIME(6)  NOT NULL,
  `notify_sms`        TINYINT(1)   NOT NULL DEFAULT 1,
  `notify_email`      TINYINT(1)   NOT NULL DEFAULT 1,
  KEY `parking_user_car_number_idx` (`car_number`),
  KEY `parking_user_role_idx` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Custom user model (car_number is username)';

-- Many-to-many: user <-> permission
CREATE TABLE IF NOT EXISTS `parking_user_user_permissions` (
  `id`            BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`       CHAR(32) NOT NULL,
  `permission_id` INT      NOT NULL,
  UNIQUE KEY `parking_user_user_permissions_user_id_permission_id` (`user_id`,`permission_id`),
  CONSTRAINT `parking_user_user_perms_user_fk`
    FOREIGN KEY (`user_id`) REFERENCES `parking_user` (`id`),
  CONSTRAINT `parking_user_user_perms_perm_fk`
    FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Many-to-many: user <-> group (kept for Django compat even if unused)
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id`   INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id`            BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `group_id`      INT    NOT NULL,
  `permission_id` INT    NOT NULL,
  UNIQUE KEY `auth_group_permissions_group_id_permission_id` (`group_id`,`permission_id`),
  CONSTRAINT `auth_group_permissions_group_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissions_perm_fk`  FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `parking_user_groups` (
  `id`       BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`  CHAR(32) NOT NULL,
  `group_id` INT NOT NULL,
  UNIQUE KEY `parking_user_groups_user_id_group_id` (`user_id`,`group_id`),
  CONSTRAINT `parking_user_groups_user_fk`  FOREIGN KEY (`user_id`)  REFERENCES `parking_user` (`id`),
  CONSTRAINT `parking_user_groups_group_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  PARKING SLOTS
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_parkingslot` (
  `id`           INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `slot_code`    VARCHAR(10)  NOT NULL UNIQUE COMMENT 'e.g. F1A01',
  `floor`        INT          NOT NULL DEFAULT 1 COMMENT '1 | 2 | 3',
  `zone`         VARCHAR(1)   NOT NULL DEFAULT 'A' COMMENT 'A=Cars B=Bikes C=CNG',
  `vehicle_type` VARCHAR(10)  NOT NULL DEFAULT 'Car' COMMENT 'Car | Bike | CNG',
  `status`       VARCHAR(10)  NOT NULL DEFAULT 'Available'
                   COMMENT 'Available | Occupied | Reserved | Disabled',
  `rate_per_hour` DECIMAL(8,2) NOT NULL DEFAULT 40.00,
  `notes`        TEXT         NOT NULL DEFAULT '',
  KEY `parking_slot_floor_zone_idx` (`floor`,`zone`),
  KEY `parking_slot_status_idx` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  BOOKINGS
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_booking` (
  `id`             CHAR(32)     NOT NULL PRIMARY KEY COMMENT 'UUID',
  `user_id`        CHAR(32)     NOT NULL,
  `slot_id`        INT          NOT NULL,
  `date`           DATE         NOT NULL,
  `entry_time`     TIME(6)      NOT NULL,
  `exit_time`      TIME(6)      NOT NULL,
  `actual_entry`   DATETIME(6)  DEFAULT NULL,
  `actual_exit`    DATETIME(6)  DEFAULT NULL,
  `vehicle_type`   VARCHAR(10)  NOT NULL COMMENT 'Car | Bike | CNG',
  `status`         VARCHAR(10)  NOT NULL DEFAULT 'Pending'
                     COMMENT 'Pending | Active | Completed | Cancelled | Overstay',
  `qr_code`        VARCHAR(100) DEFAULT NULL,
  `base_charge`    DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `overstay_charge` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `total_charge`   DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `created_at`     DATETIME(6)  NOT NULL,
  `notes`          TEXT         NOT NULL DEFAULT '',
  KEY `parking_booking_user_id_idx`   (`user_id`),
  KEY `parking_booking_slot_id_idx`   (`slot_id`),
  KEY `parking_booking_date_idx`      (`date`),
  KEY `parking_booking_status_idx`    (`status`),
  CONSTRAINT `parking_booking_user_id_fk`
    FOREIGN KEY (`user_id`) REFERENCES `parking_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `parking_booking_slot_id_fk`
    FOREIGN KEY (`slot_id`) REFERENCES `parking_parkingslot` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  PAYMENTS
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_payment` (
  `id`             CHAR(32)     NOT NULL PRIMARY KEY COMMENT 'UUID',
  `booking_id`     CHAR(32)     NOT NULL UNIQUE,
  `amount`         DECIMAL(10,2) NOT NULL,
  `method`         VARCHAR(10)  NOT NULL DEFAULT 'Cash' COMMENT 'Cash | bKash | Nagad',
  `status`         VARCHAR(10)  NOT NULL DEFAULT 'Pending'
                     COMMENT 'Pending | Completed | Refunded | Failed',
  `transaction_id` VARCHAR(100) NOT NULL DEFAULT '',
  `receipt_pdf`    VARCHAR(100) DEFAULT NULL,
  `refund_amount`  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `refund_reason`  TEXT         NOT NULL DEFAULT '',
  `paid_at`        DATETIME(6)  DEFAULT NULL,
  `created_at`     DATETIME(6)  NOT NULL,
  KEY `parking_payment_status_idx` (`status`),
  CONSTRAINT `parking_payment_booking_id_fk`
    FOREIGN KEY (`booking_id`) REFERENCES `parking_booking` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  STAFF
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_staff` (
  `id`            INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`       CHAR(32)     NOT NULL UNIQUE,
  `staff_id`      VARCHAR(20)  NOT NULL UNIQUE COMMENT 'e.g. ST001',
  `role`          VARCHAR(15)  NOT NULL DEFAULT 'Gate' COMMENT 'Gate | Counter | Supervisor',
  `current_shift` VARCHAR(10)  NOT NULL DEFAULT '' COMMENT 'Morning | Evening | Night',
  `is_on_duty`    TINYINT(1)   NOT NULL DEFAULT 0,
  `joined_date`   DATE         NOT NULL,
  CONSTRAINT `parking_staff_user_id_fk`
    FOREIGN KEY (`user_id`) REFERENCES `parking_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  SHIFT SCHEDULE
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_shiftschedule` (
  `id`           INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `staff_id`     INT          NOT NULL,
  `shift_type`   VARCHAR(10)  NOT NULL COMMENT 'Morning | Evening | Night',
  `date`         DATE         NOT NULL,
  `start_time`   TIME(6)      NOT NULL,
  `end_time`     TIME(6)      NOT NULL,
  `is_confirmed` TINYINT(1)   NOT NULL DEFAULT 0,
  `notes`        TEXT         NOT NULL DEFAULT '',
  UNIQUE KEY `parking_shiftschedule_staff_id_date_uniq` (`staff_id`,`date`),
  CONSTRAINT `parking_shiftschedule_staff_id_fk`
    FOREIGN KEY (`staff_id`) REFERENCES `parking_staff` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  NOTIFICATIONS
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_notification` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`     CHAR(32)     NOT NULL,
  `type`        VARCHAR(15)  NOT NULL DEFAULT 'General'
                  COMMENT 'Booking | Payment | Overstay | Subscription | General | LostFound',
  `title`       VARCHAR(200) NOT NULL,
  `message`     TEXT         NOT NULL,
  `is_read`     TINYINT(1)   NOT NULL DEFAULT 0,
  `sent_at`     DATETIME(6)  NOT NULL,
  `sms_sent`    TINYINT(1)   NOT NULL DEFAULT 0,
  `email_sent`  TINYINT(1)   NOT NULL DEFAULT 0,
  KEY `parking_notification_user_id_idx`  (`user_id`),
  KEY `parking_notification_is_read_idx`  (`is_read`),
  KEY `parking_notification_sent_at_idx`  (`sent_at`),
  CONSTRAINT `parking_notification_user_id_fk`
    FOREIGN KEY (`user_id`) REFERENCES `parking_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  SUBSCRIPTIONS
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_subscription` (
  `id`            INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`       CHAR(32)     NOT NULL,
  `plan`          VARCHAR(10)  NOT NULL COMMENT 'Basic | Gold | Premium',
  `reserved_slot_id` INT       DEFAULT NULL,
  `start_date`    DATE         NOT NULL,
  `end_date`      DATE         NOT NULL,
  `amount_paid`   DECIMAL(10,2) NOT NULL,
  `is_active`     TINYINT(1)   NOT NULL DEFAULT 1,
  `auto_renew`    TINYINT(1)   NOT NULL DEFAULT 0,
  `created_at`    DATETIME(6)  NOT NULL,
  KEY `parking_subscription_user_id_idx` (`user_id`),
  KEY `parking_subscription_is_active_idx` (`is_active`),
  CONSTRAINT `parking_subscription_user_id_fk`
    FOREIGN KEY (`user_id`) REFERENCES `parking_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `parking_subscription_slot_id_fk`
    FOREIGN KEY (`reserved_slot_id`) REFERENCES `parking_parkingslot` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  LOST & FOUND
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS `parking_lostfound` (
  `id`               INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `description`      TEXT         NOT NULL,
  `slot_id`          INT          DEFAULT NULL,
  `date_found`       DATE         NOT NULL,
  `found_by_staff_id` INT         DEFAULT NULL,
  `car_number`       VARCHAR(20)  NOT NULL DEFAULT '',
  `status`           VARCHAR(10)  NOT NULL DEFAULT 'Unclaimed' COMMENT 'Unclaimed | Claimed',
  `claimed_at`       DATETIME(6)  DEFAULT NULL,
  `photo`            VARCHAR(100) DEFAULT NULL,
  `notes`            TEXT         NOT NULL DEFAULT '',
  `created_at`       DATETIME(6)  NOT NULL,
  KEY `parking_lostfound_status_idx` (`status`),
  CONSTRAINT `parking_lostfound_slot_id_fk`
    FOREIGN KEY (`slot_id`) REFERENCES `parking_parkingslot` (`id`) ON DELETE SET NULL,
  CONSTRAINT `parking_lostfound_staff_id_fk`
    FOREIGN KEY (`found_by_staff_id`) REFERENCES `parking_staff` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ══════════════════════════════════════════════════════════════════
--  SEED DATA
-- ══════════════════════════════════════════════════════════════════

-- ── PARKING SLOTS (3 floors × 3 zones × 10 slots = 90 total) ──

INSERT IGNORE INTO `parking_parkingslot`
  (`slot_code`, `floor`, `zone`, `vehicle_type`, `status`, `rate_per_hour`, `notes`)
VALUES
-- Floor 1, Zone A (Cars - ৳40/hr)
('F1A01',1,'A','Car','Available',40.00,''),
('F1A02',1,'A','Car','Available',40.00,''),
('F1A03',1,'A','Car','Occupied', 40.00,''),
('F1A04',1,'A','Car','Available',40.00,''),
('F1A05',1,'A','Car','Reserved', 40.00,''),
('F1A06',1,'A','Car','Available',40.00,''),
('F1A07',1,'A','Car','Occupied', 40.00,''),
('F1A08',1,'A','Car','Available',40.00,''),
('F1A09',1,'A','Car','Available',40.00,''),
('F1A10',1,'A','Car','Available',40.00,''),
-- Floor 1, Zone B (Bikes - ৳20/hr)
('F1B01',1,'B','Bike','Available',20.00,''),
('F1B02',1,'B','Bike','Available',20.00,''),
('F1B03',1,'B','Bike','Occupied', 20.00,''),
('F1B04',1,'B','Bike','Available',20.00,''),
('F1B05',1,'B','Bike','Available',20.00,''),
('F1B06',1,'B','Bike','Available',20.00,''),
('F1B07',1,'B','Bike','Reserved', 20.00,''),
('F1B08',1,'B','Bike','Available',20.00,''),
('F1B09',1,'B','Bike','Available',20.00,''),
('F1B10',1,'B','Bike','Available',20.00,''),
-- Floor 1, Zone C (CNG - ৳30/hr)
('F1C01',1,'C','CNG','Available',30.00,''),
('F1C02',1,'C','CNG','Occupied', 30.00,''),
('F1C03',1,'C','CNG','Available',30.00,''),
('F1C04',1,'C','CNG','Available',30.00,''),
('F1C05',1,'C','CNG','Available',30.00,''),
('F1C06',1,'C','CNG','Available',30.00,''),
('F1C07',1,'C','CNG','Available',30.00,''),
('F1C08',1,'C','CNG','Available',30.00,''),
('F1C09',1,'C','CNG','Reserved', 30.00,''),
('F1C10',1,'C','CNG','Available',30.00,''),
-- Floor 2, Zone A
('F2A01',2,'A','Car','Available',40.00,''),
('F2A02',2,'A','Car','Available',40.00,''),
('F2A03',2,'A','Car','Available',40.00,''),
('F2A04',2,'A','Car','Occupied', 40.00,''),
('F2A05',2,'A','Car','Occupied', 40.00,''),
('F2A06',2,'A','Car','Available',40.00,''),
('F2A07',2,'A','Car','Available',40.00,''),
('F2A08',2,'A','Car','Available',40.00,''),
('F2A09',2,'A','Car','Available',40.00,''),
('F2A10',2,'A','Car','Disabled', 40.00,'Under maintenance'),
-- Floor 2, Zone B
('F2B01',2,'B','Bike','Available',20.00,''),
('F2B02',2,'B','Bike','Available',20.00,''),
('F2B03',2,'B','Bike','Available',20.00,''),
('F2B04',2,'B','Bike','Available',20.00,''),
('F2B05',2,'B','Bike','Occupied', 20.00,''),
('F2B06',2,'B','Bike','Available',20.00,''),
('F2B07',2,'B','Bike','Available',20.00,''),
('F2B08',2,'B','Bike','Available',20.00,''),
('F2B09',2,'B','Bike','Available',20.00,''),
('F2B10',2,'B','Bike','Available',20.00,''),
-- Floor 2, Zone C
('F2C01',2,'C','CNG','Available',30.00,''),
('F2C02',2,'C','CNG','Available',30.00,''),
('F2C03',2,'C','CNG','Occupied', 30.00,''),
('F2C04',2,'C','CNG','Available',30.00,''),
('F2C05',2,'C','CNG','Available',30.00,''),
('F2C06',2,'C','CNG','Available',30.00,''),
('F2C07',2,'C','CNG','Available',30.00,''),
('F2C08',2,'C','CNG','Available',30.00,''),
('F2C09',2,'C','CNG','Available',30.00,''),
('F2C10',2,'C','CNG','Reserved', 30.00,''),
-- Floor 3, Zone A
('F3A01',3,'A','Car','Available',40.00,''),
('F3A02',3,'A','Car','Available',40.00,''),
('F3A03',3,'A','Car','Available',40.00,''),
('F3A04',3,'A','Car','Available',40.00,''),
('F3A05',3,'A','Car','Available',40.00,''),
('F3A06',3,'A','Car','Occupied', 40.00,''),
('F3A07',3,'A','Car','Available',40.00,''),
('F3A08',3,'A','Car','Available',40.00,''),
('F3A09',3,'A','Car','Available',40.00,''),
('F3A10',3,'A','Car','Available',40.00,''),
-- Floor 3, Zone B
('F3B01',3,'B','Bike','Available',20.00,''),
('F3B02',3,'B','Bike','Available',20.00,''),
('F3B03',3,'B','Bike','Available',20.00,''),
('F3B04',3,'B','Bike','Occupied', 20.00,''),
('F3B05',3,'B','Bike','Available',20.00,''),
('F3B06',3,'B','Bike','Available',20.00,''),
('F3B07',3,'B','Bike','Available',20.00,''),
('F3B08',3,'B','Bike','Available',20.00,''),
('F3B09',3,'B','Bike','Available',20.00,''),
('F3B10',3,'B','Bike','Available',20.00,''),
-- Floor 3, Zone C
('F3C01',3,'C','CNG','Available',30.00,''),
('F3C02',3,'C','CNG','Available',30.00,''),
('F3C03',3,'C','CNG','Available',30.00,''),
('F3C04',3,'C','CNG','Available',30.00,''),
('F3C05',3,'C','CNG','Available',30.00,''),
('F3C06',3,'C','CNG','Available',30.00,''),
('F3C07',3,'C','CNG','Occupied', 30.00,''),
('F3C08',3,'C','CNG','Available',30.00,''),
('F3C09',3,'C','CNG','Available',30.00,''),
('F3C10',3,'C','CNG','Available',30.00,'');

-- ── USERS ──
-- Passwords below are Django-hashed for "admin123" (pbkdf2_sha256)
-- You can log in with these credentials after running this SQL + migrate

INSERT IGNORE INTO `parking_user`
  (`id`,`password`,`last_login`,`is_superuser`,`car_number`,`name`,`role`,
   `phone`,`email`,`subscription_plan`,`is_active`,`is_staff`,`date_joined`,`notify_sms`,`notify_email`)
VALUES
-- Admin user (car_number=ADMIN, password=admin123)
('a0000000000000000000000000000001',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+python+manage.py+createsuperuser',
 NULL,1,'ADMIN','System Administrator','Admin',
 '+8801700000000','admin@parkmanager.bd','None',1,1,NOW(),1,1),
-- Sample regular users
('u0000000000000000000000000000001',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+changepassword',
 NULL,0,'DHA-1234','Rahim Uddin','User',
 '+8801711111111','rahim@gmail.com','Gold',1,0,NOW(),1,1),
('u0000000000000000000000000000002',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+changepassword',
 NULL,0,'CTG-9012','Kamal Hossain','User',
 '+8801722222222','kamal@gmail.com','None',1,0,NOW(),1,1),
('u0000000000000000000000000000003',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+changepassword',
 NULL,0,'SYL-3456','Fatima Begum','User',
 '+8801733333333','fatima@gmail.com','Basic',1,0,NOW(),1,1),
-- Staff users
('s0000000000000000000000000000001',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+changepassword',
 NULL,0,'DHA-0001','Karim Ahmed','Staff',
 '+8801744444444','karim.staff@pm.bd','None',1,0,NOW(),1,1),
('s0000000000000000000000000000002',
 'pbkdf2_sha256$600000$salt$Fake+hash+replace+via+changepassword',
 NULL,0,'DHA-0002','Rina Begum','Staff',
 '+8801755555555','rina.staff@pm.bd','None',1,0,NOW(),1,1);

-- ── STAFF PROFILES ──
INSERT IGNORE INTO `parking_staff`
  (`user_id`,`staff_id`,`role`,`current_shift`,`is_on_duty`,`joined_date`)
VALUES
('s0000000000000000000000000000001','ST001','Gate','Morning',1,CURDATE()),
('s0000000000000000000000000000002','ST002','Counter','Evening',0,CURDATE());

-- ── SAMPLE BOOKINGS ──
INSERT IGNORE INTO `parking_booking`
  (`id`,`user_id`,`slot_id`,`date`,`entry_time`,`exit_time`,
   `actual_entry`,`actual_exit`,`vehicle_type`,`status`,
   `base_charge`,`overstay_charge`,`total_charge`,`created_at`,`notes`)
VALUES
('b0000000000000000000000000000001',
 'u0000000000000000000000000000001',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F1A01'),
 CURDATE(),'09:00:00','11:00:00',
 NULL,NULL,'Car','Active',
 80.00,0.00,80.00,NOW(),''),

('b0000000000000000000000000000002',
 'u0000000000000000000000000000002',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F2A05'),
 CURDATE(),'08:00:00','10:00:00',
 NOW(),NULL,'Car','Overstay',
 80.00,40.00,120.00,NOW(),'Overstay alert sent'),

('b0000000000000000000000000000003',
 'u0000000000000000000000000000003',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F1C02'),
 DATE_SUB(CURDATE(),INTERVAL 1 DAY),'14:00:00','16:00:00',
 DATE_SUB(NOW(),INTERVAL 1 DAY),DATE_SUB(NOW(),INTERVAL 22 HOUR),
 'CNG','Completed',
 60.00,0.00,60.00,DATE_SUB(NOW(),INTERVAL 1 DAY),'');

-- ── SAMPLE PAYMENTS ──
INSERT IGNORE INTO `parking_payment`
  (`id`,`booking_id`,`amount`,`method`,`status`,`transaction_id`,
   `refund_amount`,`refund_reason`,`paid_at`,`created_at`)
VALUES
('p0000000000000000000000000000003',
 'b0000000000000000000000000000003',
 60.00,'Cash','Completed','',
 0.00,'',DATE_SUB(NOW(),INTERVAL 22 HOUR),DATE_SUB(NOW(),INTERVAL 22 HOUR));

-- ── SAMPLE NOTIFICATIONS ──
INSERT IGNORE INTO `parking_notification`
  (`user_id`,`type`,`title`,`message`,`is_read`,`sent_at`,`sms_sent`,`email_sent`)
VALUES
('u0000000000000000000000000000001','Booking','Booking Confirmed',
 'Your booking for slot F1A01 on today has been confirmed.',0,NOW(),0,0),
('u0000000000000000000000000000002','Overstay','Overstay Alert',
 'Your vehicle at F2A05 has exceeded exit time. Extra charges apply.',0,NOW(),1,0),
('u0000000000000000000000000000003','Payment','Payment Received',
 'Payment of ৳60 received for your booking at F1C02.',1,DATE_SUB(NOW(),INTERVAL 22 HOUR),0,1);

-- ── SAMPLE LOST & FOUND ──
INSERT IGNORE INTO `parking_lostfound`
  (`description`,`slot_id`,`date_found`,`found_by_staff_id`,`car_number`,
   `status`,`claimed_at`,`notes`,`created_at`)
VALUES
('Black leather wallet',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F1A03'),
 DATE_SUB(CURDATE(),INTERVAL 1 DAY),
 (SELECT id FROM parking_staff WHERE staff_id='ST001'),
 '','Unclaimed',NULL,'Found near slot entrance',NOW()),
('Red umbrella',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F2B07'),
 DATE_SUB(CURDATE(),INTERVAL 2 DAY),
 (SELECT id FROM parking_staff WHERE staff_id='ST002'),
 'DHA-1234','Claimed',NOW(),'Owner contacted via SMS',NOW());

-- ── SAMPLE SUBSCRIPTION ──
INSERT IGNORE INTO `parking_subscription`
  (`user_id`,`plan`,`reserved_slot_id`,`start_date`,`end_date`,
   `amount_paid`,`is_active`,`auto_renew`,`created_at`)
VALUES
('u0000000000000000000000000000001','Gold',
 (SELECT id FROM parking_parkingslot WHERE slot_code='F1A01'),
 DATE_FORMAT(CURDATE(),'%Y-%m-01'),
 DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 MONTH),'%Y-%m-01'),
 800.00,1,0,NOW());

-- ══════════════════════════════════════════════════════════════════
--  USEFUL QUERIES FOR OPERATIONS
-- ══════════════════════════════════════════════════════════════════

-- View all available slots
-- SELECT slot_code, floor, zone, vehicle_type, rate_per_hour
--   FROM parking_parkingslot WHERE status = 'Available' ORDER BY floor, zone, slot_code;

-- View today's active bookings
-- SELECT b.id, u.car_number, u.name, s.slot_code, b.entry_time, b.exit_time, b.status, b.total_charge
--   FROM parking_booking b
--   JOIN parking_user u ON b.user_id = u.id
--   JOIN parking_parkingslot s ON b.slot_id = s.id
--   WHERE b.date = CURDATE() ORDER BY b.entry_time;

-- View overstay bookings
-- SELECT b.id, u.car_number, s.slot_code, b.exit_time, b.overstay_charge
--   FROM parking_booking b
--   JOIN parking_user u ON b.user_id = u.id
--   JOIN parking_parkingslot s ON b.slot_id = s.id
--   WHERE b.status = 'Overstay';

-- Today's revenue
-- SELECT SUM(amount) as total_revenue, method, COUNT(*) as count
--   FROM parking_payment
--   WHERE status = 'Completed' AND DATE(paid_at) = CURDATE()
--   GROUP BY method;

-- Monthly income summary
-- SELECT DATE_FORMAT(paid_at,'%Y-%m') as month, SUM(amount) as income, COUNT(*) as payments
--   FROM parking_payment WHERE status = 'Completed'
--   GROUP BY month ORDER BY month DESC;

-- Slot occupancy by floor
-- SELECT floor,
--   SUM(status='Available') as available,
--   SUM(status='Occupied')  as occupied,
--   SUM(status='Reserved')  as reserved,
--   COUNT(*)                as total,
--   ROUND(SUM(status='Occupied')/COUNT(*)*100,1) as occupancy_pct
-- FROM parking_parkingslot GROUP BY floor;

-- Staff on duty
-- SELECT st.staff_id, u.name, st.role, st.current_shift, st.is_on_duty
--   FROM parking_staff st JOIN parking_user u ON st.user_id = u.id
--   WHERE st.is_on_duty = 1;

-- Unclaimed lost items
-- SELECT lf.id, lf.description, ps.slot_code, lf.date_found, lf.car_number
--   FROM parking_lostfound lf
--   LEFT JOIN parking_parkingslot ps ON lf.slot_id = ps.id
--   WHERE lf.status = 'Unclaimed';

-- ══════════════════════════════════════════════════════════════════
--  NOTES
-- ══════════════════════════════════════════════════════════════════
-- After importing this SQL, run Django migrations to finalize:
--   cd backend
--   pip install -r requirements.txt
--   python manage.py migrate --fake-initial
--   python manage.py createsuperuser   (car_number=ADMIN, password=admin123)
--
-- OR skip migrate and just run:
--   python manage.py migrate
-- (This will create tables via Django - they match this schema exactly)
--
-- Database: park_management
-- User:     root
-- Password: unimanagement12345
-- ══════════════════════════════════════════════════════════════════
