CREATE DATABASE IF NOT EXISTS `UserBot` DEFAULT CHARACTER SET utf8;
USE `UserBot`;

DROP TABLE IF EXISTS `Admins`;
CREATE TABLE IF NOT EXISTS `Admins` (
  `id` BIGINT,
  `is_self` BOOLEAN DEFAULT False,
  `is_contact` BOOLEAN DEFAULT False,
  `is_mutual_contact` BOOLEAN DEFAULT False,
  `is_deleted` BOOLEAN DEFAULT False,
  `is_bot` BOOLEAN DEFAULT False,
  `is_verified` BOOLEAN DEFAULT False,
  `is_restricted` BOOLEAN DEFAULT False,
  `is_scam` BOOLEAN DEFAULT False,
  `is_support` BOOLEAN DEFAULT False,
  `first_name` TEXT DEFAULT NULL,
  `last_name` TEXT DEFAULT NULL,
  `username` TEXT UNIQUE DEFAULT NULL,
  `language_code` TEXT DEFAULT NULL,
  `phone_number` TEXT DEFAULT NULL,
  PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8;

DROP TABLE IF EXISTS `Chats`;
CREATE TABLE IF NOT EXISTS `Chats` (
  `id` BIGINT,
  `type` TEXT NOT NULL,
  `is_verified` BOOLEAN DEFAULT False,
  `is_restricted` BOOLEAN DEFAULT False,
  `is_scam` BOOLEAN DEFAULT False,
  `is_support` BOOLEAN DEFAULT False,
  `title` TEXT DEFAULT NULL,
  `username` TEXT UNIQUE DEFAULT NULL,
  `first_name` TEXT DEFAULT NULL,
  `last_name` TEXT DEFAULT NULL,
  `invite_link` TEXT DEFAULT NULL,
  PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8;
