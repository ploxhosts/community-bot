-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 08, 2021 at 10:10 PM
-- Server version: 10.4.20-MariaDB
-- PHP Version: 8.0.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- --------------------------------------------------------

--
-- Table structure for table `ploxy_automod`
--

CREATE TABLE IF NOT EXISTS `ploxy_automod` (
  `guild_id` varchar(255) NOT NULL,
  `bad_word_check` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'check for bad words',
  `user_date_check` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Should minimum age exist?',
  `minimum_user_age` bigint(20) NOT NULL DEFAULT 0 COMMENT 'Minimum amount of user age to be allowed in days',
  `preset_badwords` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'What preset you want to use for bad words',
  `message_spam_check` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Check for spam messages?',
  `on_fail_bad_word` text DEFAULT NULL COMMENT 'What to do on failing a bad word inspection',
  `on_fail_spam_check` text NOT NULL COMMENT 'What to do on failing the spam check',
  `auto_ban_count` int(10) UNSIGNED NOT NULL COMMENT 'amount of warns till you get auto banned/kicked'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ploxy_automod`
--
ALTER TABLE `ploxy_automod`
  ADD UNIQUE KEY `guild_id` (`guild_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
