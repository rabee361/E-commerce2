-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Feb 10, 2024 at 12:07 PM
-- Server version: 5.7.36
-- PHP Version: 8.1.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `eps_acc_`
--
CREATE DATABASE IF NOT EXISTS `eps_acc_` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `eps_acc_`;

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `details` varchar(50) DEFAULT NULL,
  `parent_account` int(11) DEFAULT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `type` varchar(25) NOT NULL DEFAULT 'normal',
  `final_account` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_account` (`parent_account`),
  KEY `final_account` (`final_account`)
) ENGINE=InnoDB AUTO_INCREMENT=409 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `name`, `code`, `details`, `parent_account`, `date`, `type`, `final_account`) VALUES
(357, 'الأصول', '1', NULL, NULL, '2022-09-18 16:23:02', 'normal', NULL),
(358, 'الخصوم', '2', NULL, NULL, '2022-09-18 16:23:02', 'normal', NULL),
(359, 'حقوق الملكية', '3', NULL, NULL, '2022-09-18 16:23:02', 'final', NULL),
(360, 'التكاليف', '4', NULL, NULL, '2022-09-18 16:23:02', 'normal', NULL),
(361, 'الإيرادات', '5', NULL, NULL, '2022-09-18 16:23:02', 'normal', NULL),
(362, 'المصروفات', '3-1', NULL, 359, '2022-09-18 16:23:02', 'final', NULL),
(394, 'حساب الحسم للزبون ايهم', '6', NULL, NULL, '2022-11-26 15:51:02', 'normal', NULL),
(395, 'تجريب', '7', NULL, NULL, '2023-06-18 18:52:09', 'normal', 359),
(396, 'المواد', '8', '', NULL, '2023-06-18 18:52:17', 'normal', NULL),
(397, 'المواد', '3-2', '', 359, '2023-06-18 18:52:47', 'normal', NULL),
(398, 'الحسميات', '7-1', '', 395, '2023-06-18 18:52:58', 'normal', NULL),
(399, 'الاضافات', '7-2', '', 395, '2023-06-18 18:53:10', 'normal', NULL),
(400, 'الاضافات', '7-3', '', 395, '2023-06-18 18:53:22', 'normal', NULL),
(401, 'النقديات', '7-4', '', 395, '2023-06-18 18:53:32', 'normal', NULL),
(402, 'القيمة المضافة', '7-5', '', 395, '2023-06-18 18:53:41', 'normal', NULL),
(403, 'التكلفة', '7-6', '', 395, '2023-06-18 18:53:50', 'normal', NULL),
(404, 'المخزون', '7-7', '', 395, '2023-06-18 18:53:59', 'normal', NULL),
(405, 'الهدايا', '7-8', '', 395, '2023-06-18 18:54:11', 'normal', NULL),
(406, 'مقابل الهدايا', '7-9', '', 395, '2023-06-18 18:54:20', 'normal', NULL),
(407, 'جت', '9', '', NULL, '2023-07-06 19:37:27', 'normal', NULL),
(408, 'صضثضصث', '7-10', NULL, 395, '2023-07-12 09:53:45', '', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `aggregator`
--

DROP TABLE IF EXISTS `aggregator`;
CREATE TABLE IF NOT EXISTS `aggregator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` int(11) NOT NULL,
  `ammount` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `aggregator`
--

INSERT INTO `aggregator` (`id`, `product`, `ammount`) VALUES
(1, 3, 500),
(2, 5, 500);

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `governorate` varchar(50) DEFAULT NULL,
  `address` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `phone1` varchar(50) DEFAULT NULL,
  `phone2` varchar(50) DEFAULT NULL,
  `phone3` varchar(50) DEFAULT NULL,
  `phone4` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `clients`
--

INSERT INTO `clients` (`id`, `name`, `governorate`, `address`, `email`, `phone1`, `phone2`, `phone3`, `phone4`) VALUES
(4, 'ايهم', 'طرطوس', 'طرطوس', 'ts@asd.ce', '0111111', '', '', ''),
(5, 'حسين', '', '', '', '', '', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `clients_accounts`
--

DROP TABLE IF EXISTS `clients_accounts`;
CREATE TABLE IF NOT EXISTS `clients_accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `used_price` varchar(50) DEFAULT NULL,
  `discount` double DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `days_count` int(11) DEFAULT NULL,
  `day` varchar(50) DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `client_account_id` int(11) DEFAULT NULL,
  `discount_account_id` int(11) DEFAULT NULL,
  `tax_account_id` int(11) DEFAULT NULL,
  `vat_account_id` int(11) DEFAULT NULL,
  `tax_exemption` tinyint(1) NOT NULL DEFAULT '0',
  `client_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`),
  KEY `client_account_id` (`client_account_id`),
  KEY `discount_account_id` (`discount_account_id`),
  KEY `tax_account_id` (`tax_account_id`),
  KEY `vat_account_id` (`vat_account_id`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `clients_accounts`
--

INSERT INTO `clients_accounts` (`id`, `used_price`, `discount`, `payment_method`, `days_count`, `day`, `payment_date`, `client_account_id`, `discount_account_id`, `tax_account_id`, `vat_account_id`, `tax_exemption`, `client_id`) VALUES
(39, '6', 12, 'دفع نقدي فقط', NULL, 'sat', '2000-01-01', 394, NULL, NULL, NULL, 0, 4);

-- --------------------------------------------------------

--
-- Table structure for table `compositions`
--

DROP TABLE IF EXISTS `compositions`;
CREATE TABLE IF NOT EXISTS `compositions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` int(11) NOT NULL,
  `material` int(11) NOT NULL,
  `quantity` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `costs`
--

DROP TABLE IF EXISTS `costs`;
CREATE TABLE IF NOT EXISTS `costs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `unit_cost_sp` float DEFAULT NULL,
  `unit_cost_usd` float DEFAULT NULL,
  `total_cost_sp` float DEFAULT NULL,
  `total_cost_usd` float DEFAULT NULL,
  `date` date DEFAULT NULL,
  `exchange_price` float DEFAULT NULL,
  `box_per_batch` float DEFAULT NULL,
  `working_hours_standard` float DEFAULT NULL,
  `pills_standard` float DEFAULT NULL,
  `expenses_type` varchar(50) NOT NULL,
  `material_pricing_method` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=36 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `costs`
--

INSERT INTO `costs` (`id`, `pid`, `unit_cost_sp`, `unit_cost_usd`, `total_cost_sp`, `total_cost_usd`, `date`, `exchange_price`, `box_per_batch`, `working_hours_standard`, `pills_standard`, `expenses_type`, `material_pricing_method`) VALUES
(35, 3, 0.03229, 0.00001, 1614.5, 0.50453, '2021-07-07', 3200, 50000, 6, 50000, 'month_pills', 'avg_invoice'),
(34, 3, 0.00079, 0.0000158, 39.5, 0.79, '2021-07-05', 3200, 50000, 6, 50000, 'month_no_expenses', 'avg_invoice');

-- --------------------------------------------------------

--
-- Table structure for table `cost_centers`
--

DROP TABLE IF EXISTS `cost_centers`;
CREATE TABLE IF NOT EXISTS `cost_centers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `notes` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `changable_division_factors` tinyint(1) NOT NULL DEFAULT '0',
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `parent` (`parent`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `cost_centers`
--

INSERT INTO `cost_centers` (`id`, `name`, `notes`, `type`, `parent`, `changable_division_factors`, `date`) VALUES
(1, 'الاول', NULL, 'تجميعي', NULL, 0, '2022-12-04 14:27:37'),
(2, 'الثاني Plus', 'عادي', 'توزيعي', NULL, 1, '2022-12-04 14:27:57'),
(3, 'الثالث', 'Temples march', 'عادي', NULL, 0, '2022-12-04 15:08:05'),
(4, 'الرابع Max', NULL, 'عادي', NULL, 0, '2022-12-04 16:22:54');

-- --------------------------------------------------------

--
-- Table structure for table `cost_centers_aggregations_distributives`
--

DROP TABLE IF EXISTS `cost_centers_aggregations_distributives`;
CREATE TABLE IF NOT EXISTS `cost_centers_aggregations_distributives` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `master_cost_center` int(11) NOT NULL,
  `cost_center` int(11) NOT NULL,
  `division_factor` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cost_center` (`cost_center`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `cost_centers_aggregations_distributives`
--

INSERT INTO `cost_centers_aggregations_distributives` (`id`, `master_cost_center`, `cost_center`, `division_factor`) VALUES
(1, 2, 1, 12),
(2, 2, 3, 88);

-- --------------------------------------------------------

--
-- Table structure for table `cost_materials`
--

DROP TABLE IF EXISTS `cost_materials`;
CREATE TABLE IF NOT EXISTS `cost_materials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `process_id` int(11) NOT NULL,
  `material` int(11) NOT NULL,
  `price_sp` float DEFAULT NULL,
  `price_usd` float DEFAULT NULL,
  `standard_quantity` float DEFAULT NULL,
  `required_quantity` float DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=154 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `cost_materials`
--

INSERT INTO `cost_materials` (`id`, `process_id`, `material`, `price_sp`, `price_usd`, `standard_quantity`, `required_quantity`, `unit`) VALUES
(150, 35, 1120, 0, 0, 5.2, NULL, 'كغ'),
(149, 35, 946, 0.24, 0.000075, 50, NULL, 'كغ'),
(148, 35, 944, 1602.5, 0.500781, 1, NULL, 'كغ'),
(153, 34, 1120, 0, 0, 5.2, NULL, 'كغ'),
(152, 34, 946, 0.24, 0.000075, 50, NULL, 'كغ'),
(151, 34, 944, 1602.5, 0.500781, 1, NULL, 'كغ');

-- --------------------------------------------------------

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
CREATE TABLE IF NOT EXISTS `currencies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `symbol` varchar(50) DEFAULT NULL,
  `parts` varchar(50) DEFAULT NULL,
  `parts_relation` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `currencies`
--

INSERT INTO `currencies` (`id`, `name`, `symbol`, `parts`, `parts_relation`) VALUES
(1, 'دولار أمريكي', '$', 'سنت', 100),
(2, 'ليرة سورية', 'S.P', 'قرش', 100),
(3, 'ليرة لبنانية', 'L.B', 'قرش لبناني', 100),
(4, 'دينار كويتي', 'KWD', 'درهم', 100);

-- --------------------------------------------------------

--
-- Table structure for table `exchange_price`
--

DROP TABLE IF EXISTS `exchange_price`;
CREATE TABLE IF NOT EXISTS `exchange_price` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usd` double NOT NULL,
  `syp` double NOT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `exchange_price`
--

INSERT INTO `exchange_price` (`id`, `usd`, `syp`, `date`) VALUES
(1, 50, 1, '2000-01-01'),
(5, 250, 1, '2020-03-06'),
(6, 3200, 1, '2021-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `exchange_prices`
--

DROP TABLE IF EXISTS `exchange_prices`;
CREATE TABLE IF NOT EXISTS `exchange_prices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `currency1` int(11) NOT NULL,
  `currency2` int(11) NOT NULL,
  `exchange` double NOT NULL DEFAULT '1',
  `date` date DEFAULT NULL,
  `currency1_ordered` int(11) GENERATED ALWAYS AS (least(`currency1`,`currency2`)) STORED,
  `currency2_ordered` int(11) GENERATED ALWAYS AS (greatest(`currency2`,`currency1`)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unqBi_test` (`currency1_ordered`,`currency2_ordered`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `exchange_prices`
--

INSERT INTO `exchange_prices` (`id`, `currency1`, `currency2`, `exchange`, `date`) VALUES
(2, 1, 2, 10, '2020-01-01'),
(4, 2, 1, 0.5, '2021-03-01'),
(5, 1, 2, 10, '2023-04-14'),
(6, 1, 2, 10, '2023-03-27'),
(7, 1, 2, 10, '2023-04-12'),
(8, 1, 2, 10, '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
CREATE TABLE IF NOT EXISTS `expenses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_slot` varchar(25) NOT NULL DEFAULT 'month',
  `value` double NOT NULL,
  `year` varchar(50) NOT NULL,
  `month` varchar(50) DEFAULT '1',
  `expense_type_id` int(50) NOT NULL,
  `currency` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `year` (`year`,`month`,`expense_type_id`) USING BTREE,
  KEY `currency` (`currency`),
  KEY `type` (`expense_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`id`, `time_slot`, `value`, `year`, `month`, `expense_type_id`, `currency`) VALUES
(19, 'year', 1000, '2000', '', 5, 1);

-- --------------------------------------------------------

--
-- Table structure for table `expenses_monthly`
--

DROP TABLE IF EXISTS `expenses_monthly`;
CREATE TABLE IF NOT EXISTS `expenses_monthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `expenses` double NOT NULL,
  `year` varchar(50) NOT NULL,
  `month` varchar(50) NOT NULL DEFAULT '1',
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `expenses_types`
--

DROP TABLE IF EXISTS `expenses_types`;
CREATE TABLE IF NOT EXISTS `expenses_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `calculated_in_manufacture` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `opposite_account_id` (`opposite_account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `expenses_types`
--

INSERT INTO `expenses_types` (`id`, `name`, `account_id`, `opposite_account_id`, `calculated_in_manufacture`) VALUES
(5, 'operational', 361, 361, 1);

-- --------------------------------------------------------

--
-- Table structure for table `groupped_materials_composition`
--

DROP TABLE IF EXISTS `groupped_materials_composition`;
CREATE TABLE IF NOT EXISTS `groupped_materials_composition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `groupped_material_id` int(11) NOT NULL,
  `composition_material_id` int(11) NOT NULL,
  `quantity` double DEFAULT NULL,
  `unit` int(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `composition_material_id` (`composition_material_id`),
  KEY `groupped_material_id` (`groupped_material_id`),
  KEY `unit` (`unit`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `groupped_materials_composition`
--

INSERT INTO `groupped_materials_composition` (`id`, `groupped_material_id`, `composition_material_id`, `quantity`, `unit`) VALUES
(1, 1, 2, 1, 1),
(2, 1, 3, 2, 1);

-- --------------------------------------------------------

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
CREATE TABLE IF NOT EXISTS `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `parent_group` varchar(50) DEFAULT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `parent_group` (`parent_group`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `groups`
--

INSERT INTO `groups` (`id`, `name`, `code`, `parent_group`, `date`) VALUES
(16, 'a', '1-1-1', '18', '2022-09-07 07:31:06'),
(17, 'b', '1-1-2', '18', '2022-09-07 07:31:13'),
(18, 'c', '1-1', 'None', '2022-09-07 07:31:19');

-- --------------------------------------------------------

--
-- Table structure for table `hr_additional_costs`
--

DROP TABLE IF EXISTS `hr_additional_costs`;
CREATE TABLE IF NOT EXISTS `hr_additional_costs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `statement` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `account_id` int(11) NOT NULL,
  `department_id` int(11) DEFAULT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `value` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `state` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'active',
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `department_id` (`department_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_additional_costs`
--

INSERT INTO `hr_additional_costs` (`id`, `statement`, `account_id`, `department_id`, `opposite_account_id`, `value`, `currency_id`, `date`, `state`) VALUES
(1, '', 361, 2, 357, 50, 1, '2023-04-29', 'active'),
(2, 'يبل سيب', 357, 1, 357, 344, 1, '2001-01-01', 'active'),
(3, 'r4', 357, 1, 357, 4, 2, '2000-01-01', 'active'),
(4, 'gdf ', 357, 1, 357, 12, 1, '2000-01-01', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `hr_courses`
--

DROP TABLE IF EXISTS `hr_courses`;
CREATE TABLE IF NOT EXISTS `hr_courses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `providor` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `cost` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `location` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_courses`
--

INSERT INTO `hr_courses` (`id`, `title`, `providor`, `account_id`, `opposite_account_id`, `cost`, `currency_id`, `date`, `location`) VALUES
(1, 'Test course1', 'Eliana1', 357, 394, 7777, 2, '2023-04-20 20:00:00', 'Damascus Syria1s5');

-- --------------------------------------------------------

--
-- Table structure for table `hr_course_employees`
--

DROP TABLE IF EXISTS `hr_course_employees`;
CREATE TABLE IF NOT EXISTS `hr_course_employees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `gpa` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  KEY `employee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_course_employees`
--

INSERT INTO `hr_course_employees` (`id`, `course_id`, `employee_id`, `gpa`) VALUES
(1, 1, 10, 15),
(2, 1, 12, 13),
(4, 1, 14, 12);

-- --------------------------------------------------------

--
-- Table structure for table `hr_departments`
--

DROP TABLE IF EXISTS `hr_departments`;
CREATE TABLE IF NOT EXISTS `hr_departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `day_hours` double NOT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `notes` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `work_day_saturday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_sunday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_monday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_tuesday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_wednesday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_thursday` tinyint(1) NOT NULL DEFAULT '0',
  `work_day_friday` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `opposite_account_id` (`opposite_account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_departments`
--

INSERT INTO `hr_departments` (`id`, `name`, `day_hours`, `account_id`, `opposite_account_id`, `notes`, `work_day_saturday`, `work_day_sunday`, `work_day_monday`, `work_day_tuesday`, `work_day_wednesday`, `work_day_thursday`, `work_day_friday`) VALUES
(1, 'managment', 8, 357, 361, 'None', 1, 1, 1, 1, 1, 1, 0),
(2, 'DevTeam', 8, 357, 361, 'None', 1, 0, 1, 1, 1, 1, 1),
(3, 'Accounting Team', 8, 357, 361, NULL, 0, 0, 0, 0, 0, 0, 0),
(4, 'data clerks', 8, 357, 357, NULL, 0, 0, 0, 0, 0, 0, 0),
(5, 'قسم', 8, 357, 357, 'بوب', 0, 0, 0, 0, 0, 0, 0),
(6, 'test', 8, 357, 357, 'rr', 0, 0, 0, 0, 0, 0, 0),
(7, 'gaga', 8, 357, 357, '', 0, 1, 1, 1, 1, 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `hr_departments_finance`
--

DROP TABLE IF EXISTS `hr_departments_finance`;
CREATE TABLE IF NOT EXISTS `hr_departments_finance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department_id` int(11) NOT NULL,
  `statement` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(11) COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `employmee_id` (`department_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_departments_finance`
--

INSERT INTO `hr_departments_finance` (`id`, `department_id`, `statement`, `type`, `value`, `currency_id`, `start_date`, `end_date`, `account_id`, `opposite_account_id`, `date`) VALUES
(9, 1, 'sfsdfيبسيب', 'addition', 3423, 1, '2023-01-05', '2023-01-31', 357, 357, '2023-04-24 21:35:31'),
(10, 2, '', 'discount', 12, 1, '2023-01-01', '2023-01-31', 357, 357, '2023-04-25 10:33:24');

-- --------------------------------------------------------

--
-- Table structure for table `hr_departments_leaves`
--

DROP TABLE IF EXISTS `hr_departments_leaves`;
CREATE TABLE IF NOT EXISTS `hr_departments_leaves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department_id` int(11) NOT NULL,
  `statement` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration_in_hours` double NOT NULL,
  `duration_in_days` double NOT NULL,
  `start_date` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `hr_positions_leaves_ibfk_1` (`department_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_departments_leaves`
--

INSERT INTO `hr_departments_leaves` (`id`, `department_id`, `statement`, `duration_in_hours`, `duration_in_days`, `start_date`, `date`) VALUES
(1, 6, 'adasيسبسيب', 1, 0, '2000-01-01', '2023-04-25 10:00:31'),
(2, 6, '12', 2.4, 0.3, '2000-01-01', '2023-04-25 11:59:01');

-- --------------------------------------------------------

--
-- Table structure for table `hr_employees`
--

DROP TABLE IF EXISTS `hr_employees`;
CREATE TABLE IF NOT EXISTS `hr_employees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employment_request_id` int(11) NOT NULL,
  `national_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `start_date` date NOT NULL,
  `resignation_date` date DEFAULT NULL,
  `bank` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bank_account_number` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bank_notes` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employment_request_id` (`employment_request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employees`
--

INSERT INTO `hr_employees` (`id`, `employment_request_id`, `national_id`, `phone`, `address`, `name`, `email`, `birthdate`, `start_date`, `resignation_date`, `bank`, `bank_account_number`, `bank_notes`) VALUES
(10, 2, '2222', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-20', NULL, 'bemo', 'ds54fsdf45', 'None'),
(12, 3, '1010', '0932660775', 'safita', 'hussain biedouh', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-20', NULL, NULL, NULL, NULL),
(13, 4, '1010', '0932660775', 'safita', 'Ayham Yousef', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-20', NULL, NULL, NULL, NULL),
(14, 5, '1010', '0932660775', 'safita', 'Maher Mouhammad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-20', NULL, NULL, NULL, NULL),
(16, 6, '1010', '0932660775', 'safita', 'Bashar Baddour', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-20', '2023-04-15', NULL, NULL, NULL),
(17, 7, '1010', '0932660775', 'safita', 'Mahmoud', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-23', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `hr_employees_certificates`
--

DROP TABLE IF EXISTS `hr_employees_certificates`;
CREATE TABLE IF NOT EXISTS `hr_employees_certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `university_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `university_specialty` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `university_year` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `university_certificate` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `university_gpa` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employment_request_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employees_certificates`
--

INSERT INTO `hr_employees_certificates` (`id`, `employee_id`, `university_name`, `university_specialty`, `university_year`, `university_certificate`, `university_gpa`) VALUES
(9, 12, '5', '55', '5', '55', 5),
(10, 12, '5', '55', '5', '55', 5),
(11, 16, 'الجامعة', 'الاختصاص', '2010', 'الشهادة', 100),
(12, 14, 'الجامعة', 'الاختصاص', '2010', 'الشهادة', 100),
(13, 12, '4', '4', '4', '4', 4),
(14, 13, '4', '4', '4', '4', 4),
(15, 10, 'D', 'S', '2022', 'S', 2);

-- --------------------------------------------------------

--
-- Table structure for table `hr_employees_salaries_additions_discounts`
--

DROP TABLE IF EXISTS `hr_employees_salaries_additions_discounts`;
CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `repeatition` int(1) NOT NULL,
  `value` double NOT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `statement` varchar(500) CHARACTER SET latin1 DEFAULT NULL,
  `currency_id` int(11) DEFAULT NULL,
  `state` varchar(11) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'active',
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `employee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employees_salaries_additions_discounts`
--

INSERT INTO `hr_employees_salaries_additions_discounts` (`id`, `employee_id`, `type`, `start_date`, `repeatition`, `value`, `account_id`, `opposite_account_id`, `statement`, `currency_id`, `state`) VALUES
(1, 10, 'permenant addition', '2000-01-01', 3, 10, 357, 357, '', NULL, 'active'),
(2, 10, 'permenant addition', '2000-01-01', 2, 10, 357, 357, '', 2, 'active'),
(3, 10, 'permenant addition', '2000-01-01', 2, 10, 357, 357, '', 1, 'active');

-- --------------------------------------------------------

--
-- Table structure for table `hr_employees_salaries_additions_discounts_payments`
--

DROP TABLE IF EXISTS `hr_employees_salaries_additions_discounts_payments`;
CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts_payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `salaries_additions_discounts` int(11) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `salaries_additions_discounts` (`salaries_additions_discounts`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hr_employees_transfers`
--

DROP TABLE IF EXISTS `hr_employees_transfers`;
CREATE TABLE IF NOT EXISTS `hr_employees_transfers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `department_id` int(11) NOT NULL,
  `position_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `employee_id` (`employee_id`),
  KEY `department_id` (`department_id`),
  KEY `position_id` (`position_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employees_transfers`
--

INSERT INTO `hr_employees_transfers` (`id`, `employee_id`, `department_id`, `position_id`, `date`) VALUES
(1, 10, 1, 1, '2023-04-21 22:16:05'),
(2, 12, 2, 2, '2023-04-22 07:17:19'),
(3, 13, 3, 4, '2023-04-22 00:21:17');

-- --------------------------------------------------------

--
-- Table structure for table `hr_employee_received_items`
--

DROP TABLE IF EXISTS `hr_employee_received_items`;
CREATE TABLE IF NOT EXISTS `hr_employee_received_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `warehouse_id` int(11) DEFAULT NULL,
  `material_id` int(11) DEFAULT NULL,
  `quantity` double DEFAULT NULL,
  `unit_id` int(11) DEFAULT NULL,
  `received_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `material_id` (`material_id`),
  KEY `unit_id` (`unit_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `hr_employee_received_items_ibfk_4` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employee_received_items`
--

INSERT INTO `hr_employee_received_items` (`id`, `employee_id`, `warehouse_id`, `material_id`, `quantity`, `unit_id`, `received_date`) VALUES
(1, 16, 6, 2, 1, 1, '2023-04-13'),
(2, 16, 6, 2, 1, 1, '2023-04-13');

-- --------------------------------------------------------

--
-- Table structure for table `hr_employment_requests`
--

DROP TABLE IF EXISTS `hr_employment_requests`;
CREATE TABLE IF NOT EXISTS `hr_employment_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `national_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employment_requests`
--

INSERT INTO `hr_employment_requests` (`id`, `national_id`, `phone`, `address`, `name`, `email`, `birthdate`, `date`) VALUES
(2, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(3, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(4, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(5, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(6, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(7, '1010', '0932660775', 'safita', 'Mahmoud', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(8, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25'),
(9, '1010', '0932660775', 'safita', 'Ali K. Ahmad', 'alikahmad@hotmail.com', '1983-01-01', '2023-04-19 10:34:25');

-- --------------------------------------------------------

--
-- Table structure for table `hr_employment_request_certificates`
--

DROP TABLE IF EXISTS `hr_employment_request_certificates`;
CREATE TABLE IF NOT EXISTS `hr_employment_request_certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employment_request_id` int(11) NOT NULL,
  `university_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `university_specialty` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `university_year` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `university_certificate` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `university_gpa` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employment_request_id` (`employment_request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_employment_request_certificates`
--

INSERT INTO `hr_employment_request_certificates` (`id`, `employment_request_id`, `university_name`, `university_specialty`, `university_year`, `university_certificate`, `university_gpa`) VALUES
(4, 2, '5', '55', '5', '55', 5),
(5, 2, 'الجامعة', 'الاختصاص', '2010', 'الشهادة', 100),
(6, 2, '4', '4', '4', '4', 4);

-- --------------------------------------------------------

--
-- Table structure for table `hr_extra`
--

DROP TABLE IF EXISTS `hr_extra`;
CREATE TABLE IF NOT EXISTS `hr_extra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `department_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `value` double NOT NULL,
  `duration_in_hours` double NOT NULL,
  `duration_in_days` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `statement` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `state` varchar(11) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'active',
  PRIMARY KEY (`id`),
  KEY `currency_id` (`currency_id`),
  KEY `employee_id` (`employee_id`),
  KEY `department_id` (`department_id`),
  KEY `account_id` (`account_id`),
  KEY `opposite_account_id` (`opposite_account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_extra`
--

INSERT INTO `hr_extra` (`id`, `employee_id`, `department_id`, `start_date`, `value`, `duration_in_hours`, `duration_in_days`, `currency_id`, `statement`, `account_id`, `opposite_account_id`, `state`) VALUES
(1, 12, 1, '2000-01-01', 10000, 16, 2, 1, NULL, 357, 357, 'active'),
(2, 10, 1, '2000-01-01', 125, 1, 0.125, 1, '', 357, 357, 'active'),
(4, 10, 1, '2000-01-01', 200000, 8, 1, 2, '', 357, 357, 'active');

-- --------------------------------------------------------

--
-- Table structure for table `hr_finance`
--

DROP TABLE IF EXISTS `hr_finance`;
CREATE TABLE IF NOT EXISTS `hr_finance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `cycle` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'month',
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `employmee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_finance`
--

INSERT INTO `hr_finance` (`id`, `employee_id`, `type`, `value`, `currency_id`, `start_date`, `end_date`, `account_id`, `opposite_account_id`, `cycle`, `date`) VALUES
(2, 12, 'salary', 50000, 1, '2023-04-01', NULL, 357, 361, 'week', '2023-04-22 21:21:49'),
(3, 12, 'insurance', 700, 1, '2023-04-01', NULL, 357, 361, 'week', '2023-04-22 21:21:49'),
(4, 10, 'insurance', 25000, 2, '2023-04-01', NULL, 360, 358, 'month', '2023-04-22 21:21:49'),
(7, 10, 'salary', 50000, 2, '2000-01-01', NULL, 361, 357, 'day', '2023-04-24 09:16:30'),
(16, 13, 'salary', 50000, 2, '2000-01-01', NULL, 361, 358, 'month', '2023-04-24 10:26:21'),
(17, 13, 'insurance', 700, 2, '2000-01-01', NULL, 361, 362, 'day', '2023-04-24 10:26:21');

-- --------------------------------------------------------

--
-- Table structure for table `hr_insurance_blocks`
--

DROP TABLE IF EXISTS `hr_insurance_blocks`;
CREATE TABLE IF NOT EXISTS `hr_insurance_blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_insurance_blocks`
--

INSERT INTO `hr_insurance_blocks` (`id`, `from_date`, `to_date`, `date`) VALUES
(22, '2000-01-01', '2000-01-01', '2023-05-11 20:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `hr_insurance_block_entries`
--

DROP TABLE IF EXISTS `hr_insurance_block_entries`;
CREATE TABLE IF NOT EXISTS `hr_insurance_block_entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `insurance_block_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `cycles` double NOT NULL,
  `value` double NOT NULL,
  `currency` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salary_block_id` (`insurance_block_id`),
  KEY `employee_id` (`employee_id`),
  KEY `currency` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_insurance_block_entries`
--

INSERT INTO `hr_insurance_block_entries` (`id`, `insurance_block_id`, `employee_id`, `cycles`, `value`, `currency`) VALUES
(1, 22, 10, 0.036, 892.8571428571428, 2),
(2, 22, 12, 0.143, 7142.857142857142, 2),
(3, 22, 13, 1, 700, 2);

-- --------------------------------------------------------

--
-- Table structure for table `hr_leaves`
--

DROP TABLE IF EXISTS `hr_leaves`;
CREATE TABLE IF NOT EXISTS `hr_leaves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `leave_type_id` int(50) NOT NULL,
  `alternative_id` int(11) NOT NULL,
  `duration_in_hours` double NOT NULL,
  `duration_in_days` double NOT NULL,
  `start_date` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `state` varchar(11) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'active',
  PRIMARY KEY (`id`),
  KEY `employee_id` (`employee_id`),
  KEY `alternative_id` (`alternative_id`),
  KEY `type` (`leave_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_leaves`
--

INSERT INTO `hr_leaves` (`id`, `employee_id`, `leave_type_id`, `alternative_id`, `duration_in_hours`, `duration_in_days`, `start_date`, `date`, `state`) VALUES
(3, 10, 1, 10, 16, 2, '2000-01-01', '2023-05-05 09:22:44', 'active'),
(5, 10, 1, 10, 4, 0.5, '2000-01-01', '2023-05-05 21:42:31', 'cancelled'),
(9, 12, 1, 10, 36, 4.5, '2000-01-01', '2023-05-05 22:18:46', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `hr_leave_types`
--

DROP TABLE IF EXISTS `hr_leave_types`;
CREATE TABLE IF NOT EXISTS `hr_leave_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `days_per_month` int(11) NOT NULL,
  `date_added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `paid` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_leave_types`
--

INSERT INTO `hr_leave_types` (`id`, `name`, `days_per_month`, `date_added`, `paid`) VALUES
(1, 'اجازة مدفوعة', 7, '2023-05-02 20:21:33', 0),
(2, 'اجازة غير مدفوعة', 7, '2023-05-02 20:35:38', 1);

-- --------------------------------------------------------

--
-- Table structure for table `hr_loans`
--

DROP TABLE IF EXISTS `hr_loans`;
CREATE TABLE IF NOT EXISTS `hr_loans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `value` double NOT NULL,
  `currency` int(11) NOT NULL,
  `date` date NOT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `periodically_subtract_from_salary` tinyint(1) NOT NULL DEFAULT '0',
  `subtract_currency` int(11) DEFAULT NULL,
  `subtract_cycle` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `subtract_value` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency` (`currency`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `employee_id` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_loans`
--

INSERT INTO `hr_loans` (`id`, `employee_id`, `value`, `currency`, `date`, `account_id`, `opposite_account_id`, `periodically_subtract_from_salary`, `subtract_currency`, `subtract_cycle`, `subtract_value`) VALUES
(17, 10, 100000, 2, '2000-01-01', 357, 357, 1, 1, 'day', 10000);

-- --------------------------------------------------------

--
-- Table structure for table `hr_loans_payment`
--

DROP TABLE IF EXISTS `hr_loans_payment`;
CREATE TABLE IF NOT EXISTS `hr_loans_payment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loan_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  `currency` int(11) NOT NULL,
  `source` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `loan_id` (`loan_id`),
  KEY `currency` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_loans_payment`
--

INSERT INTO `hr_loans_payment` (`id`, `loan_id`, `value`, `currency`, `source`, `date`) VALUES
(7, 17, 50000, 2, 'direct', '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `hr_positions`
--

DROP TABLE IF EXISTS `hr_positions`;
CREATE TABLE IF NOT EXISTS `hr_positions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `salary` double DEFAULT NULL,
  `currency_id` int(11) DEFAULT NULL,
  `notes` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `currency_id` (`currency_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_positions`
--

INSERT INTO `hr_positions` (`id`, `name`, `salary`, `currency_id`, `notes`) VALUES
(1, 'manager', 5000, 2, 'asdasd'),
(2, 'it', 5000, 1, NULL),
(3, 'accountant', 5000, 1, NULL),
(4, 'accountant leader', 5000, 1, NULL),
(5, 'coder', 5000, 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `hr_positions_finance`
--

DROP TABLE IF EXISTS `hr_positions_finance`;
CREATE TABLE IF NOT EXISTS `hr_positions_finance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `position_id` int(11) NOT NULL,
  `statement` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency_id` (`currency_id`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `employmee_id` (`position_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_positions_finance`
--

INSERT INTO `hr_positions_finance` (`id`, `position_id`, `statement`, `type`, `value`, `currency_id`, `start_date`, `end_date`, `account_id`, `opposite_account_id`, `date`) VALUES
(1, 1, '', 'discount', 10, 1, '2023-01-15', '2023-01-31', 357, 361, '2023-04-25 21:48:12'),
(2, 2, '47d5f', 'addition', 4000, 2, '2023-01-01', '2023-01-31', 357, 357, '2023-04-25 22:06:51');

-- --------------------------------------------------------

--
-- Table structure for table `hr_positions_leaves`
--

DROP TABLE IF EXISTS `hr_positions_leaves`;
CREATE TABLE IF NOT EXISTS `hr_positions_leaves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `position_id` int(11) NOT NULL,
  `statement` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `duration_in_hours` double NOT NULL,
  `duration_in_days` double NOT NULL,
  `start_date` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `hr_positions_leaves_ibfk_1` (`position_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_positions_leaves`
--

INSERT INTO `hr_positions_leaves` (`id`, `position_id`, `statement`, `duration_in_hours`, `duration_in_days`, `start_date`, `date`) VALUES
(1, 1, 'adsa asd asdasdf', 8, 1, '2023-04-26', '2023-04-25 21:45:44'),
(2, 1, '44545', 8, 1, '2000-01-01', '2023-04-25 21:51:00'),
(3, 3, 'fgdfg', 8, 1, '2001-01-01', '2023-04-25 22:07:04');

-- --------------------------------------------------------

--
-- Table structure for table `hr_salary_blocks`
--

DROP TABLE IF EXISTS `hr_salary_blocks`;
CREATE TABLE IF NOT EXISTS `hr_salary_blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `account_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_salary_blocks`
--

INSERT INTO `hr_salary_blocks` (`id`, `from_date`, `to_date`, `date`, `account_id`) VALUES
(21, '2000-01-01', '2000-01-30', '2023-07-03 20:00:00', 360);

-- --------------------------------------------------------

--
-- Table structure for table `hr_salary_block_entries`
--

DROP TABLE IF EXISTS `hr_salary_block_entries`;
CREATE TABLE IF NOT EXISTS `hr_salary_block_entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `salary_block_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `statement` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `currency` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salary_block_id` (`salary_block_id`),
  KEY `employee_id` (`employee_id`),
  KEY `currency` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=391 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_salary_block_entries`
--

INSERT INTO `hr_salary_block_entries` (`id`, `salary_block_id`, `employee_id`, `statement`, `value`, `currency`) VALUES
(355, 21, 10, 'cycles', 30, NULL),
(356, 21, 10, 'paid_value', 1406470, 2),
(357, 21, 10, 'depratment_additions', 0, 2),
(358, 21, 10, 'department_discounts', 0, 2),
(359, 21, 10, 'position_additions', 0, 2),
(360, 21, 10, 'position_discounts', 0, 2),
(361, 21, 10, 'leaves_discounts', 100000, 2),
(362, 21, 10, 'extras_additions', 56250, 2),
(363, 21, 10, 'loans_subtraction', 50000, 2),
(364, 21, 10, 'salary_discounts', 0, 2),
(365, 21, 10, 'salary_additions', 220, 2),
(366, 21, 10, 'base_salary', 1500000, 2),
(367, 21, 12, 'cycles', 4.286, NULL),
(368, 21, 12, 'paid_value', 196428.571, 2),
(369, 21, 12, 'depratment_additions', 0, 2),
(370, 21, 12, 'department_discounts', 0, 2),
(371, 21, 12, 'position_additions', 0, 2),
(372, 21, 12, 'position_discounts', 0, 2),
(373, 21, 12, 'leaves_discounts', 32142.857, 2),
(374, 21, 12, 'extras_additions', 14285.714, 2),
(375, 21, 12, 'loans_subtraction', 0, 2),
(376, 21, 12, 'salary_discounts', 0, 2),
(377, 21, 12, 'salary_additions', 0, 2),
(378, 21, 12, 'base_salary', 214285.714, 2),
(379, 21, 13, 'cycles', 1.071, NULL),
(380, 21, 13, 'paid_value', 53571.429, 2),
(381, 21, 13, 'depratment_additions', 0, 2),
(382, 21, 13, 'department_discounts', 0, 2),
(383, 21, 13, 'position_additions', 0, 2),
(384, 21, 13, 'position_discounts', 0, 2),
(385, 21, 13, 'leaves_discounts', 0, 2),
(386, 21, 13, 'extras_additions', 0, 2),
(387, 21, 13, 'loans_subtraction', 0, 2),
(388, 21, 13, 'salary_discounts', 0, 2),
(389, 21, 13, 'salary_additions', 0, 2),
(390, 21, 13, 'base_salary', 53571.429, 2);

-- --------------------------------------------------------

--
-- Table structure for table `hr_settings`
--

DROP TABLE IF EXISTS `hr_settings`;
CREATE TABLE IF NOT EXISTS `hr_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(11) COLLATE utf8_unicode_ci DEFAULT NULL,
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1019 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `hr_settings`
--

INSERT INTO `hr_settings` (`id`, `name`, `value`, `last_update`) VALUES
(103, 'setting_default_leave_duration_unit', 'day', '2023-04-30 09:49:34'),
(104, 'setting_cycle_unused_leaves', '1', '2023-05-03 21:27:47'),
(105, 'setting_default_leave_duration', '5', '2023-04-30 18:17:03'),
(106, 'setting_default_leave_duration_range', 'month', '2023-04-30 10:06:34'),
(107, 'setting_day_hours', '8', '2023-04-30 18:17:03'),
(108, 'setting_week_days', '5', '2023-04-30 18:17:03'),
(109, 'setting_insurance_opposite_account', '357', '2023-04-29 10:12:07'),
(110, 'setting_departments_default_account', '357', '2023-04-29 10:12:07'),
(111, 'setting_additional_costs_account', '360', '2023-04-29 10:20:21'),
(112, 'setting_departments_additions_opposite_account', '357', '2023-04-29 10:12:07'),
(113, 'setting_additions_opposite_account', '357', '2023-04-29 10:12:07'),
(114, 'setting_salaries_opposite_account', '358', '2023-04-29 10:20:12'),
(115, 'setting_departments_additions_account', '357', '2023-04-29 10:12:07'),
(116, 'setting_salaries_account', '360', '2023-04-29 10:20:03'),
(117, 'setting_additions_account', '357', '2023-04-29 10:12:07'),
(118, 'setting_discounts_opposite_account', '357', '2023-04-29 10:12:07'),
(119, 'setting_departments_default_opposite_account', '394', '2023-04-29 10:20:03'),
(120, 'setting_departments_discounts_account', '357', '2023-04-29 10:12:07'),
(121, 'setting_discounts_account', '359', '2023-04-29 10:20:21'),
(122, 'setting_additional_costs_opposite_account', '394', '2023-04-29 10:20:21'),
(123, 'setting_courses_costs_account', '357', '2023-04-29 10:12:07'),
(124, 'setting_courses_costs_opposite_account', '357', '2023-04-29 10:12:07'),
(125, 'setting_loans_account', '357', '2023-04-29 10:12:07'),
(126, 'setting_departments_discounts_opposite_account', '357', '2023-04-29 10:12:07'),
(127, 'setting_loans_opposite_account', '357', '2023-04-29 10:12:07'),
(128, 'setting_insurance_account', '359', '2023-04-29 10:20:12'),
(155, 'setting_extra_account', '359', '2023-04-30 18:16:35'),
(156, 'setting_extra_opposite_account', '360', '2023-04-30 18:16:35'),
(213, 'setting_week_start_day', 'sunday', '2023-04-30 18:17:03'),
(301, 'setting_default_leave_unit', 'day', '2023-04-30 10:10:20'),
(304, 'setting_default_leave_range', 'month', '2023-04-30 18:17:03'),
(388, 'setting_extra_normal', '2', '2023-04-30 11:22:43'),
(389, 'setting_extra_high', '4', '2023-04-30 11:22:43'),
(508, 'setting_work_day_sunday', '1', '2023-05-03 21:28:20'),
(509, 'setting_work_day_monday', '1', '2023-05-03 21:28:20'),
(510, 'setting_work_day_tuesday', '1', '2023-05-03 21:28:20'),
(511, 'setting_work_day_wednesday', '1', '2023-05-03 21:28:20'),
(512, 'setting_work_day_thursday', '1', '2023-05-04 08:37:59'),
(513, 'setting_work_day_friday', '0', '2023-05-03 20:58:44'),
(514, 'setting_work_day_saturday', '0', '2023-05-03 20:58:44'),
(1018, 'setting_month_duration', '28', '2023-05-06 11:04:03');

-- --------------------------------------------------------

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
CREATE TABLE IF NOT EXISTS `invoices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) NOT NULL,
  `number` int(11) NOT NULL,
  `client` int(11) NOT NULL,
  `client_account` int(11) NOT NULL,
  `payment` varchar(50) NOT NULL,
  `paid` tinyint(1) NOT NULL,
  `currency` int(11) NOT NULL,
  `cost_center` int(11) DEFAULT NULL,
  `warehouse` int(11) DEFAULT NULL,
  `cost_account` int(11) DEFAULT NULL,
  `gifts_account` int(11) DEFAULT NULL,
  `added_value_account` int(11) DEFAULT NULL,
  `monetary_account` int(11) DEFAULT NULL,
  `materials_account` int(11) DEFAULT NULL,
  `stock_account` int(11) DEFAULT NULL,
  `gifts_opposite_account` int(11) DEFAULT NULL,
  `statement` varchar(500) DEFAULT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `client` (`client`),
  KEY `client_account` (`client_account`),
  KEY `currency` (`currency`),
  KEY `cost_center` (`cost_center`),
  KEY `warehouse` (`warehouse`),
  KEY `cost_account` (`cost_account`),
  KEY `gifts_account` (`gifts_account`),
  KEY `added_value_account` (`added_value_account`),
  KEY `monetary_account` (`monetary_account`),
  KEY `materials_account` (`materials_account`),
  KEY `stock_account` (`stock_account`),
  KEY `gifts_opposite_account` (`gifts_opposite_account`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `invoices`
--

INSERT INTO `invoices` (`id`, `type`, `number`, `client`, `client_account`, `payment`, `paid`, `currency`, `cost_center`, `warehouse`, `cost_account`, `gifts_account`, `added_value_account`, `monetary_account`, `materials_account`, `stock_account`, `gifts_opposite_account`, `statement`, `date`) VALUES
(30, 'buy', 1, 4, 357, 'cash', 0, 1, 4, 6, 362, 357, 361, 360, 362, 394, 358, '', '2000-01-01'),
(31, 'buy', 1, 4, 357, 'cash', 0, 2, 4, 6, 362, 357, 361, 360, 362, 394, 358, '', '2023-03-27'),
(32, 'buy', 2, 4, 357, 'cash', 1, 2, 4, 6, 362, 357, 361, 360, 362, 394, 358, '', '2000-01-01'),
(33, 'buy', 3, 4, 357, 'cash', 1, 1, NULL, NULL, NULL, NULL, NULL, 361, NULL, NULL, NULL, NULL, '2023-06-17'),
(34, 'buy', 4, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-18'),
(35, 'buy', 5, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-19'),
(36, 'buy', 6, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-19'),
(37, 'buy', 7, 4, 357, 'cash', 1, 2, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-19'),
(38, 'buy', 7, 4, 357, 'cash', 1, 2, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-19'),
(39, 'buy', 8, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-19'),
(40, 'buy', 9, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-20'),
(41, 'buy', 10, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-20'),
(42, 'buy', 11, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-06-20'),
(43, 'buy', 12, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(44, 'buy', 13, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(45, 'buy', 13, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(46, 'buy', 14, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(47, 'buy', 15, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(48, 'buy', 16, 4, 357, 'cash', 1, 2, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(49, 'buy', 17, 4, 357, 'cash', 1, 2, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(50, 'buy', 18, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2023-08-12'),
(51, 'buy', 19, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-06'),
(52, 'buy', 20, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(53, 'buy', 21, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(54, 'buy', 22, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(55, 'buy', 23, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(56, 'buy', 24, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(57, 'buy', 25, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(58, 'buy', 26, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(59, 'buy', 27, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(60, 'buy', 28, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(61, 'buy', 29, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(62, 'buy', 30, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(63, 'buy', 31, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(64, 'buy', 32, 4, 357, 'cash', 1, 1, NULL, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(65, 'buy', 33, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(66, 'buy', 34, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(67, 'buy', 35, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(68, 'buy', 36, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(69, 'buy', 37, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(70, 'buy', 38, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(71, 'buy', 39, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(72, 'buy', 40, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07'),
(73, 'buy', 41, 4, 357, 'cash', 1, 1, 2, NULL, 403, 405, 402, 401, 396, 404, 406, NULL, '2024-02-07');

-- --------------------------------------------------------

--
-- Table structure for table `invoices_discounts_additions`
--

DROP TABLE IF EXISTS `invoices_discounts_additions`;
CREATE TABLE IF NOT EXISTS `invoices_discounts_additions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `account` int(11) NOT NULL,
  `cost_center` int(11) DEFAULT NULL,
  `currency` int(11) DEFAULT NULL,
  `exchange` int(11) DEFAULT NULL,
  `opposite_account` int(11) DEFAULT NULL,
  `equilivance` double DEFAULT NULL,
  `percent` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `cost_center` (`cost_center`),
  KEY `currency` (`currency`),
  KEY `exchange` (`exchange`),
  KEY `opposite_account` (`opposite_account`),
  KEY `invoices_discounts_additions_ibfk_6` (`account`),
  KEY `invoices_discounts_additions_ibfk_7` (`invoice_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `invoices_out`
--

DROP TABLE IF EXISTS `invoices_out`;
CREATE TABLE IF NOT EXISTS `invoices_out` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(50) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `client` varchar(50) DEFAULT NULL,
  `direct_client` varchar(50) DEFAULT NULL,
  `payment` varchar(50) DEFAULT NULL,
  `currency` varchar(50) DEFAULT NULL,
  `exchange` double DEFAULT '1',
  `statement` varchar(50) DEFAULT NULL,
  `paid` varchar(5) DEFAULT NULL,
  `total_discount` double DEFAULT '0',
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `invoices_out_items`
--

DROP TABLE IF EXISTS `invoices_out_items`;
CREATE TABLE IF NOT EXISTS `invoices_out_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice` int(11) NOT NULL,
  `prodcut` int(11) NOT NULL,
  `quantity` int(11) DEFAULT '0',
  `price_sp` double DEFAULT '0',
  `price_usd` double DEFAULT '0',
  `discount` double DEFAULT '0',
  `price_sp_after_discount` double DEFAULT '0',
  `price_usd_after_discount` double DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `invoice_items`
--

DROP TABLE IF EXISTS `invoice_items`;
CREATE TABLE IF NOT EXISTS `invoice_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_id` int(11) NOT NULL,
  `material_id` int(11) NOT NULL,
  `quantity1` double NOT NULL,
  `unit1_id` int(11) NOT NULL,
  `quantity2` double NOT NULL,
  `unit2_id` int(11) NOT NULL,
  `quantity3` float NOT NULL,
  `unit3_id` int(11) NOT NULL,
  `price_type_id` int(11) NOT NULL,
  `unit_price` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `equilivance_price` int(11) NOT NULL,
  `exchange_id` int(11) DEFAULT NULL,
  `discount` double DEFAULT NULL,
  `discount_percent` double DEFAULT NULL,
  `addition` double DEFAULT NULL,
  `addition_percent` double DEFAULT NULL,
  `added_value` double DEFAULT NULL,
  `gifts` double DEFAULT NULL,
  `gifts_discount` double DEFAULT NULL,
  `warehouse_id` int(11) DEFAULT NULL,
  `cost_center_id` int(11) DEFAULT NULL,
  `notes` varchar(500) CHARACTER SET latin1 DEFAULT NULL,
  `item_discount_account` int(11) DEFAULT NULL,
  `item_addition_account` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cost_center_id` (`cost_center_id`),
  KEY `currency_id` (`currency_id`),
  KEY `exchange_id` (`exchange_id`),
  KEY `material_id` (`material_id`),
  KEY `price_type_id` (`price_type_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `item_discount_account` (`item_discount_account`),
  KEY `item_addition_account` (`item_addition_account`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `invoice_items`
--

INSERT INTO `invoice_items` (`id`, `invoice_id`, `material_id`, `quantity1`, `unit1_id`, `quantity2`, `unit2_id`, `quantity3`, `unit3_id`, `price_type_id`, `unit_price`, `currency_id`, `equilivance_price`, `exchange_id`, `discount`, `discount_percent`, `addition`, `addition_percent`, `added_value`, `gifts`, `gifts_discount`, `warehouse_id`, `cost_center_id`, `notes`, `item_discount_account`, `item_addition_account`) VALUES
(4, 31, 3, 10, 1, 0.01, 1, 0.00001, 3, 6, 7, 1, 50, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 6, NULL, NULL, NULL, NULL),
(6, 32, 2, 1, 1, 1000, 1, 1000000, 4, 6, 7, 1, 70, 2, 0, 0, 0, NULL, NULL, 0, 0.7, 6, NULL, NULL, NULL, NULL),
(7, 32, 3, 5, 1, 5000, 1, 5000000, 4, 6, 7, 1, 70, 2, 0, 0, 0, NULL, NULL, 0, 3.5, 3, NULL, NULL, NULL, NULL),
(8, 33, 2, 5, 1, 5000, 1, 5000000, 4, 1, 5, 1, 5, NULL, 1, 4, 1, NULL, NULL, 2, 2.5, NULL, NULL, NULL, 358, 359),
(9, 34, 3, 5, 1, 5000, 1, 5000000, 4, 1, 10, 1, 10, NULL, 0.5, 1, 1, NULL, 3, 2, 5, 6, NULL, 'kjh', 398, 400),
(10, 35, 4, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 1, NULL, 0.05, 1, 0.05, NULL, NULL, 2, 0.5, NULL, NULL, NULL, 398, 400),
(11, 36, 5, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 1, NULL, 0.05, 1, 0.05, NULL, 2, 2, 0.5, NULL, NULL, NULL, 398, 400),
(12, 37, 6, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 10, 2, 0.05, 1, 0.1, NULL, 3, 2, 0.5, NULL, NULL, NULL, 398, 400),
(13, 38, 3, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 10, 2, 0.05, 1, 0.1, NULL, 3, 2, 0.5, NULL, NULL, NULL, 398, 400),
(14, 39, 3, 5, 1, 5000, 1, 5000000, 4, 1, 4, 1, 4, NULL, 0.2, 1, 0.2, NULL, 2, 2, 2, NULL, NULL, NULL, 398, 400),
(15, 40, 3, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 1, NULL, 0.35, 7, 0.4, NULL, 2, 2, 0.5, 3, 1, NULL, 398, 400),
(16, 41, 3, 5, 1, 5000, 1, 5000000, 4, 1, 5, 1, 5, NULL, 2, 8, 3, NULL, 3, 2, 2.5, NULL, NULL, NULL, 398, 400),
(17, 42, 3, 5, 1, 5000, 1, 5000000, 4, 1, 1, 1, 1, NULL, 1, 20, 2, NULL, 5, 2, 0.5, NULL, NULL, NULL, 398, 400),
(18, 43, 1, 1, 3, 1000, 1, 1000000, 4, 1, 5, 1, 5, NULL, 0, 0, 0, NULL, NULL, 0, 2.5, NULL, NULL, NULL, 398, 400),
(19, 44, 1, 1, 3, 1000, 1, 1000000, 4, 1, 5, 1, 5, NULL, 0, 0, 0, NULL, NULL, 0, 2.5, NULL, NULL, NULL, 398, 400),
(20, 45, 1, 1, 3, 1000, 1, 1000000, 4, 1, 5, 1, 5, NULL, 0, 0, 0, NULL, NULL, 0, 2.5, 6, NULL, NULL, 398, 400),
(21, 46, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, 0.5, 6, NULL, NULL, 398, 400),
(22, 47, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, 0.5, NULL, NULL, NULL, 398, 400),
(23, 48, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 10, 2, 0, 0, 0, NULL, NULL, 0, 0.5, 6, NULL, NULL, 398, 400),
(24, 49, 1, 1, 3, 1000, 1, 1000000, 4, 1, 5, 1, 50, 2, 0, 0, 0, NULL, NULL, 0, 2.5, NULL, NULL, NULL, 398, 400),
(25, 50, 1, 2, 3, 2000, 1, 2000000, 4, 1, 5, 1, 5, NULL, 0, 0, 0, NULL, NULL, 1, NULL, 6, NULL, NULL, 398, 400),
(26, 51, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(27, 52, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(28, 53, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(29, 54, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(30, 55, 1, 2, 3, 2000, 1, 2000000, 4, 2, 2, 1, 2, NULL, 1, 25, 1, NULL, 1, 1, NULL, 3, NULL, NULL, 398, 400),
(31, 56, 1, 2, 3, 2000, 1, 2000000, 4, 1, 2, 1, 2, NULL, 1, 25, 1, NULL, 1, 1, NULL, 3, NULL, NULL, 398, 400),
(32, 57, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(33, 58, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 1, NULL, NULL, NULL, NULL, 398, 400),
(34, 59, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(35, 60, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(36, 61, 1, 4, 3, 4000, 1, 4000000, 4, 1, 4, 1, 4, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(37, 62, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(38, 63, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(39, 64, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(40, 65, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(41, 66, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(42, 67, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(43, 68, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(44, 69, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(45, 70, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(46, 71, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, NULL, 0, NULL, NULL, NULL, NULL, 398, 400),
(47, 72, 1, 1, 3, 1000, 1, 1000000, 4, 1, 1, 1, 1, NULL, 0, 0, 0, NULL, 0, 0, NULL, NULL, NULL, NULL, 398, 400),
(48, 73, 1, 5, 3, 5000, 1, 5000000, 4, 1, 5, 1, 5, NULL, 1, 4, 2, NULL, 1, 1, NULL, 3, NULL, NULL, 398, 400);

-- --------------------------------------------------------

--
-- Table structure for table `journal_entries`
--

DROP TABLE IF EXISTS `journal_entries`;
CREATE TABLE IF NOT EXISTS `journal_entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` int(11) NOT NULL,
  `date` date NOT NULL,
  `entry_date` date NOT NULL,
  `origin_type` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `origin_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `currency` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `journal_entries`
--

INSERT INTO `journal_entries` (`id`, `currency`, `date`, `entry_date`, `origin_type`, `origin_id`) VALUES
(38, 1, '2024-02-07', '2024-02-07', 'invoice', 72),
(39, 1, '2024-02-07', '2024-02-07', 'invoice', 73),
(40, 1, '2024-02-08', '2000-01-01', 'period_start', 1),
(41, 1, '2024-02-08', '2000-01-01', 'period_start', 2);

-- --------------------------------------------------------

--
-- Table structure for table `journal_entries_items`
--

DROP TABLE IF EXISTS `journal_entries_items`;
CREATE TABLE IF NOT EXISTS `journal_entries_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `journal_entry_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `statement` varchar(2500) COLLATE utf8_unicode_ci NOT NULL,
  `currency` int(11) NOT NULL,
  `opposite_account_id` int(11) NOT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `cost_center_id` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `currency` (`currency`),
  KEY `opposite_account_id` (`opposite_account_id`),
  KEY `journal_entries_items_ibfk_3` (`journal_entry_id`),
  KEY `cost_center` (`cost_center_id`)
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `journal_entries_items`
--

INSERT INTO `journal_entries_items` (`id`, `journal_entry_id`, `account_id`, `statement`, `currency`, `opposite_account_id`, `type`, `value`, `cost_center_id`) VALUES
(87, 38, 396, 'xx', 1, 401, 'creditor', 1, 2),
(88, 38, 401, 'xx', 1, 396, 'debtor', 1, 2),
(89, 38, 404, 'xx', 1, 403, 'creditor', 1, NULL),
(90, 38, 403, 'xx', 1, 404, 'debtor', 1, NULL),
(91, 39, 396, 'xx', 1, 401, 'creditor', 25, 2),
(92, 39, 400, 'Addition xx', 1, 401, 'creditor', 2, 2),
(93, 39, 404, 'xx', 1, 403, 'creditor', 28, NULL),
(94, 39, 403, 'xx', 1, 404, 'debtor', 28, NULL),
(95, 40, 408, 'Period opening xx ()', 1, 357, 'creditor', 100, 2),
(96, 40, 357, 'Period opening xx ()', 1, 408, 'creditor', 100, 2),
(97, 41, 408, 'Period opening xx ()', 1, 357, 'creditor', 100, 2),
(98, 41, 357, 'Period opening xx ()', 1, 408, 'creditor', 100, 2);

-- --------------------------------------------------------

--
-- Table structure for table `journal_entries_items_distributive_cost_center_values`
--

DROP TABLE IF EXISTS `journal_entries_items_distributive_cost_center_values`;
CREATE TABLE IF NOT EXISTS `journal_entries_items_distributive_cost_center_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `journal_entry_item_id` int(11) NOT NULL,
  `cost_centers_aggregations_distributives_id` int(11) NOT NULL,
  `percentage` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `journal_entry_item_id` (`journal_entry_item_id`,`cost_centers_aggregations_distributives_id`),
  KEY `cost_centers_aggregations_distributives_id` (`cost_centers_aggregations_distributives_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `journal_entries_items_distributive_cost_center_values`
--

INSERT INTO `journal_entries_items_distributive_cost_center_values` (`id`, `journal_entry_item_id`, `cost_centers_aggregations_distributives_id`, `percentage`) VALUES
(54, 87, 1, 12),
(55, 87, 2, 88),
(56, 88, 1, 12),
(57, 88, 2, 88),
(58, 91, 1, 12),
(59, 91, 2, 88),
(60, 92, 1, 12),
(61, 92, 2, 88),
(62, 95, 1, 12),
(63, 95, 2, 88),
(64, 96, 1, 12),
(65, 96, 2, 88),
(66, 97, 1, 12),
(67, 97, 2, 88),
(68, 98, 1, 12),
(69, 98, 2, 88);

-- --------------------------------------------------------

--
-- Table structure for table `lab`
--

DROP TABLE IF EXISTS `lab`;
CREATE TABLE IF NOT EXISTS `lab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `element` int(11) NOT NULL,
  `quantity` float DEFAULT NULL,
  `unit` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `src` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `lab`
--

INSERT INTO `lab` (`id`, `element`, `quantity`, `unit`, `src`, `date`) VALUES
(12, 944, 5.03, 'كغ', 'raws', '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `machines`
--

DROP TABLE IF EXISTS `machines`;
CREATE TABLE IF NOT EXISTS `machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `years_age` double DEFAULT NULL,
  `estimated_waste_value` double DEFAULT NULL,
  `estimated_waste_currency` int(11) DEFAULT NULL,
  `estimated_waste_account` int(11) DEFAULT NULL,
  `invoice_item_id` int(11) DEFAULT NULL,
  `notes` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_item_id` (`invoice_item_id`),
  KEY `estimated_waste_account` (`estimated_waste_account`),
  KEY `estimated_waste_currency` (`estimated_waste_currency`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `machines`
--

INSERT INTO `machines` (`id`, `name`, `years_age`, `estimated_waste_value`, `estimated_waste_currency`, `estimated_waste_account`, `invoice_item_id`, `notes`) VALUES
(1, 'مخروط', 12, 12, 2, 357, 7, '12'),
(2, 'طاحون', NULL, NULL, NULL, NULL, 4, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `machine_modes`
--

DROP TABLE IF EXISTS `machine_modes`;
CREATE TABLE IF NOT EXISTS `machine_modes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machine_id` int(11) NOT NULL,
  `name` varchar(250) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `machine_modes_ibfk_1` (`machine_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `machine_modes`
--

INSERT INTO `machine_modes` (`id`, `machine_id`, `name`, `date`) VALUES
(1, 1, 'est', '2023-05-15 18:08:30'),
(2, 1, 'est2', '2023-05-16 10:31:09'),
(3, 2, 'ge', '2023-05-16 10:31:09');

-- --------------------------------------------------------

--
-- Table structure for table `manufacture`
--

DROP TABLE IF EXISTS `manufacture`;
CREATE TABLE IF NOT EXISTS `manufacture` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `working_hours` double DEFAULT NULL,
  `batch` int(11) DEFAULT NULL,
  `quantity1` int(11) NOT NULL,
  `unit1` int(11) NOT NULL,
  `quantity2` double NOT NULL,
  `unit2` int(11) NOT NULL,
  `quantity3` double NOT NULL,
  `unit3` int(11) NOT NULL,
  `pullout_date` date DEFAULT NULL,
  `date` date DEFAULT NULL,
  `expenses_type` varchar(50) NOT NULL,
  `material_pricing_method` varchar(50) NOT NULL,
  `currency` int(11) NOT NULL,
  `expenses_cost` double NOT NULL,
  `machines_operation_cost` double NOT NULL,
  `salaries_cost` double NOT NULL,
  `warehouse` int(11) NOT NULL,
  `mid_account` int(11) NOT NULL,
  `account` int(11) NOT NULL,
  `composition_materials_cost` double DEFAULT NULL,
  `quantity_unit_expenses` int(11) DEFAULT NULL,
  `expenses_distribution` varchar(50) DEFAULT NULL,
  `state` varchar(20) NOT NULL DEFAULT 'active',
  `ingredients_pullout_method` varchar(50) NOT NULL,
  `ingredients_pullout_account` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `unit1` (`unit1`),
  KEY `unit2` (`unit2`),
  KEY `unit3` (`unit3`),
  KEY `warehouse` (`warehouse`),
  KEY `med_account` (`mid_account`),
  KEY `account` (`account`),
  KEY `quantity_unit_expenses` (`quantity_unit_expenses`),
  KEY `material_id` (`material_id`),
  KEY `manufacture_ibfk_1` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `manufacture`
--

INSERT INTO `manufacture` (`id`, `material_id`, `working_hours`, `batch`, `quantity1`, `unit1`, `quantity2`, `unit2`, `quantity3`, `unit3`, `pullout_date`, `date`, `expenses_type`, `material_pricing_method`, `currency`, `expenses_cost`, `machines_operation_cost`, `salaries_cost`, `warehouse`, `mid_account`, `account`, `composition_materials_cost`, `quantity_unit_expenses`, `expenses_distribution`, `state`, `ingredients_pullout_method`, `ingredients_pullout_account`) VALUES
(115, 2, 5, 1, 1, 3, 1000, 1, 1000000, 4, '2023-07-08', '2023-07-08', 'month', 'material_exact_invoice', 1, 0, 0, 0, 3, 357, 357, 42, 3, 'no_expenses', 'active', 'FIFO', 357),
(116, 2, 10, 1, 2, 3, 2000, 1, 2000000, 4, '2023-07-08', '2023-07-08', 'month', 'material_invoices_average', 1, 0, 0, 0, 3, 357, 357, 120.7, 3, 'no_expenses', 'active', 'FIFO', 357),
(117, 2, 10, 1, 2, 3, 2000, 1, 2000000, 4, '2023-07-08', '2023-07-08', 'month', 'material_exact_invoice', 1, 0, 0, 0, 3, 357, 357, 14, 3, 'no_expenses', 'active', 'FIFO', 357),
(118, 2, 5, 1, 1, 3, 1000, 1, 1000000, 4, '2023-08-12', '2023-08-12', 'month', 'material_invoices_average', 1, 0, 0, 0, 6, 357, 357, 15.889, 3, 'no_expenses', 'active', 'FIFO', 357),
(119, 2, 5, 1, 1, 3, 1000, 1, 1000000, 4, '2023-08-12', '2023-08-12', 'month', 'material_invoices_average', 1, 0, 0, 0, 3, 357, 357, 15.889, 3, 'no_expenses', 'active', 'FIFO', 357),
(120, 2, 5, 1, 1, 3, 1000, 1, 1000000, 4, '2023-08-12', '2023-08-12', 'month', 'material_invoices_average', 1, 0, 0, 0, 3, 357, 357, 15.889, 3, 'no_expenses', 'active', 'FIFO', 357);

-- --------------------------------------------------------

--
-- Table structure for table `manufacture_halls`
--

DROP TABLE IF EXISTS `manufacture_halls`;
CREATE TABLE IF NOT EXISTS `manufacture_halls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `warehouse_id` int(11) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `warehouse_id` (`warehouse_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `manufacture_halls`
--

INSERT INTO `manufacture_halls` (`id`, `warehouse_id`, `date`) VALUES
(6, 6, '2023-06-21 21:26:54');

-- --------------------------------------------------------

--
-- Table structure for table `manufacture_machines`
--

DROP TABLE IF EXISTS `manufacture_machines`;
CREATE TABLE IF NOT EXISTS `manufacture_machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `manufacture_id` int(11) NOT NULL,
  `machine_id` int(11) NOT NULL,
  `mode_id` int(11) NOT NULL,
  `duration` double NOT NULL,
  `exclusive` tinyint(11) NOT NULL,
  `exclusive_percent` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `machine_id` (`machine_id`),
  KEY `mode_id` (`mode_id`),
  KEY `manufacture_id` (`manufacture_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `manufacture_machines`
--

INSERT INTO `manufacture_machines` (`id`, `manufacture_id`, `machine_id`, `mode_id`, `duration`, `exclusive`, `exclusive_percent`) VALUES
(19, 115, 1, 1, 5, 0, 50),
(20, 116, 1, 1, 5, 0, 50),
(21, 117, 1, 1, 5, 0, 50),
(22, 118, 1, 1, 5, 0, 50),
(23, 119, 1, 1, 5, 0, 50),
(24, 120, 1, 1, 5, 0, 50);

-- --------------------------------------------------------

--
-- Table structure for table `manufacture_materials`
--

DROP TABLE IF EXISTS `manufacture_materials`;
CREATE TABLE IF NOT EXISTS `manufacture_materials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `manufacture_id` int(11) NOT NULL,
  `composition_item_id` int(11) NOT NULL,
  `standard_quantity` double DEFAULT NULL,
  `required_quantity` double DEFAULT NULL,
  `unit` int(50) DEFAULT NULL,
  `unit_cost` int(11) DEFAULT NULL,
  `row_type` varchar(10) NOT NULL,
  `warehouse_id` int(11) DEFAULT NULL,
  `warehouse_account_id` int(11) DEFAULT NULL,
  `pulled_quantity` double DEFAULT NULL,
  `shortage` double DEFAULT NULL,
  `currency` int(11) DEFAULT NULL,
  `warehouse_quantity` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `manufacture_id` (`manufacture_id`),
  KEY `unit` (`unit`),
  KEY `manufacture_materials_ibfk_2` (`composition_item_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `warehouse_account_id` (`warehouse_account_id`),
  KEY `currency` (`currency`)
) ENGINE=InnoDB AUTO_INCREMENT=583 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `manufacture_materials`
--

INSERT INTO `manufacture_materials` (`id`, `manufacture_id`, `composition_item_id`, `standard_quantity`, `required_quantity`, `unit`, `unit_cost`, `row_type`, `warehouse_id`, `warehouse_account_id`, `pulled_quantity`, `shortage`, `currency`, `warehouse_quantity`) VALUES
(565, 115, 1, 10, 10, 1, NULL, 'parent', NULL, NULL, 10, 0, 1, NULL),
(566, 115, 1, NULL, NULL, NULL, 1, 'child', 3, 360, 10, NULL, 1, 10),
(567, 115, 2, 5, 5, 1, NULL, 'parent', NULL, NULL, 5, 0, 1, NULL),
(568, 115, 2, NULL, NULL, NULL, 7, 'child', 3, 360, 5, NULL, 1, 5),
(569, 116, 1, 10, 20, 1, 6, 'parent', NULL, NULL, 11, 9, 1, NULL),
(570, 116, 2, 5, 10, 1, 0, 'parent', NULL, NULL, 10, 0, 1, NULL),
(571, 117, 1, 10, 20, 1, NULL, 'parent', NULL, NULL, 11, 9, 1, NULL),
(572, 117, 1, NULL, NULL, NULL, 1, 'child', 3, 360, 10, NULL, 1, 10),
(573, 117, 1, NULL, NULL, NULL, 7, 'child', 6, 360, 1, NULL, 1, 1),
(574, 117, 2, 5, 10, 1, NULL, 'parent', NULL, NULL, 10, 0, 1, NULL),
(575, 117, 2, NULL, NULL, NULL, 7, 'child', 3, 360, 5, NULL, 1, 5),
(576, 117, 2, NULL, NULL, NULL, 1, 'child', 6, 360, 5, NULL, 1, 10),
(577, 118, 1, 1, 1, 1, NULL, 'parent', NULL, NULL, 1, 0, 1, NULL),
(578, 118, 2, 2, 2, 1, NULL, 'parent', NULL, NULL, 2, 0, 1, NULL),
(579, 119, 1, 1, 1, 1, NULL, 'parent', NULL, NULL, 1, 0, 1, NULL),
(580, 119, 2, 2, 2, 1, NULL, 'parent', NULL, NULL, 2, 0, 1, NULL),
(581, 120, 1, 1, 1, 1, NULL, 'parent', NULL, NULL, 1, 0, 1, NULL),
(582, 120, 2, 2, 2, 1, NULL, 'parent', NULL, NULL, 2, 0, 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `manufacture_pullout_requests`
--

DROP TABLE IF EXISTS `manufacture_pullout_requests`;
CREATE TABLE IF NOT EXISTS `manufacture_pullout_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `manufacture_id` int(11) NOT NULL,
  `material_id` int(11) NOT NULL,
  `pullout_request_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `response_date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `material_id` (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `materials`
--

DROP TABLE IF EXISTS `materials`;
CREATE TABLE IF NOT EXISTS `materials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `group` int(11) DEFAULT NULL,
  `specs` varchar(500) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `manufacturer` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `origin` varchar(50) DEFAULT NULL,
  `quality` varchar(50) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `model` varchar(50) DEFAULT NULL,
  `unit1` int(11) DEFAULT NULL,
  `unit2` int(11) DEFAULT NULL,
  `unit3` int(11) DEFAULT NULL,
  `default_unit` int(11) NOT NULL DEFAULT '1',
  `current_quantity` double DEFAULT NULL,
  `max_quantity` double DEFAULT NULL,
  `min_quantity` double DEFAULT NULL,
  `request_limit` double DEFAULT NULL,
  `gift` double DEFAULT NULL,
  `gift_for` double DEFAULT NULL,
  `price1_desc` int(11) DEFAULT NULL,
  `price1_1` double DEFAULT NULL,
  `price1_1_unit` varchar(50) DEFAULT NULL,
  `price1_2` double DEFAULT NULL,
  `price1_2_unit` varchar(50) DEFAULT NULL,
  `price1_3` double DEFAULT NULL,
  `price1_3_unit` varchar(50) DEFAULT NULL,
  `price2_desc` int(11) DEFAULT NULL,
  `price2_1` double DEFAULT NULL,
  `price2_1_unit` varchar(50) DEFAULT NULL,
  `price2_2` double DEFAULT NULL,
  `price2_2_unit` varchar(50) DEFAULT NULL,
  `price2_3` double DEFAULT NULL,
  `price2_3_unit` varchar(50) DEFAULT NULL,
  `price3_desc` int(11) DEFAULT NULL,
  `price3_1` double DEFAULT NULL,
  `price3_1_unit` varchar(50) DEFAULT NULL,
  `price3_2` double DEFAULT NULL,
  `price3_2_unit` varchar(50) DEFAULT NULL,
  `price3_3` double DEFAULT NULL,
  `price3_3_unit` varchar(50) DEFAULT NULL,
  `price4_desc` int(11) DEFAULT NULL,
  `price4_1` double DEFAULT NULL,
  `price4_1_unit` varchar(50) DEFAULT NULL,
  `price4_2` double DEFAULT NULL,
  `price4_2_unit` varchar(50) DEFAULT NULL,
  `price4_3` double DEFAULT NULL,
  `price4_3_unit` varchar(50) DEFAULT NULL,
  `price5_desc` int(11) DEFAULT NULL,
  `price5_1` double DEFAULT NULL,
  `price5_1_unit` varchar(50) DEFAULT NULL,
  `price5_2` double DEFAULT NULL,
  `price5_2_unit` varchar(50) DEFAULT NULL,
  `price5_3` double DEFAULT NULL,
  `price5_3_unit` varchar(50) DEFAULT NULL,
  `price6_desc` int(11) DEFAULT NULL,
  `price6_1` double DEFAULT NULL,
  `price6_1_unit` varchar(50) DEFAULT NULL,
  `price6_2` double DEFAULT NULL,
  `price6_2_unit` varchar(50) DEFAULT NULL,
  `price6_3` double DEFAULT NULL,
  `price6_3_unit` varchar(50) DEFAULT NULL,
  `expiray` int(11) DEFAULT NULL,
  `groupped` tinyint(1) NOT NULL DEFAULT '0',
  `yearly_required` double DEFAULT NULL,
  `work_hours` double DEFAULT NULL,
  `standard_unit3_quantity` double DEFAULT NULL,
  `standard_unit2_quantity` double DEFAULT NULL,
  `standard_unit1_quantity` double DEFAULT NULL,
  `manufacture_hall` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `price1_desc` (`price1_desc`),
  KEY `price2_desc` (`price2_desc`),
  KEY `price3_desc` (`price3_desc`),
  KEY `price4_desc` (`price4_desc`),
  KEY `price5_desc` (`price5_desc`),
  KEY `price6_desc` (`price6_desc`),
  KEY `unit1` (`unit1`),
  KEY `unit2` (`unit2`),
  KEY `unit3` (`unit3`),
  KEY `group` (`group`),
  KEY `manufacture_hall` (`manufacture_hall`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `materials`
--

INSERT INTO `materials` (`id`, `code`, `name`, `group`, `specs`, `size`, `manufacturer`, `color`, `origin`, `quality`, `type`, `model`, `unit1`, `unit2`, `unit3`, `default_unit`, `current_quantity`, `max_quantity`, `min_quantity`, `request_limit`, `gift`, `gift_for`, `price1_desc`, `price1_1`, `price1_1_unit`, `price1_2`, `price1_2_unit`, `price1_3`, `price1_3_unit`, `price2_desc`, `price2_1`, `price2_1_unit`, `price2_2`, `price2_2_unit`, `price2_3`, `price2_3_unit`, `price3_desc`, `price3_1`, `price3_1_unit`, `price3_2`, `price3_2_unit`, `price3_3`, `price3_3_unit`, `price4_desc`, `price4_1`, `price4_1_unit`, `price4_2`, `price4_2_unit`, `price4_3`, `price4_3_unit`, `price5_desc`, `price5_1`, `price5_1_unit`, `price5_2`, `price5_2_unit`, `price5_3`, `price5_3_unit`, `price6_desc`, `price6_1`, `price6_1_unit`, `price6_2`, `price6_2_unit`, `price6_3`, `price6_3_unit`, `expiray`, `groupped`, `yearly_required`, `work_hours`, `standard_unit3_quantity`, `standard_unit2_quantity`, `standard_unit1_quantity`, `manufacture_hall`) VALUES
(1, '', 'xx', 18, NULL, '2', NULL, NULL, 'الصين', NULL, 'assets', NULL, 3, 1, 4, 1, NULL, NULL, NULL, NULL, NULL, NULL, 6, 7, '2', 5, '1', 5, '1', 2, 14, '2', 15, '1', 15, '1', 3, 21, '1', 25, '1', 25, '1', 4, 4, '1', 4, '3', 44, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '', NULL, '1', NULL, 1, NULL, 5, 1000000, 1000, 1, 6),
(2, '', 'x2', 18, NULL, '2', NULL, NULL, 'الصين', NULL, 'assets', NULL, 3, 4, 1, 3, NULL, NULL, NULL, NULL, NULL, NULL, 6, 10, '1', 1, '1', 0.1, '1', 2, 100, '2', NULL, '1', NULL, '1', 3, 5000, '1', NULL, '1', NULL, '1', 6, 10, '1', NULL, '3', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '', NULL, '1', NULL, 1, NULL, 5, 2000, 2000000, 2, NULL),
(3, 'ce', 'cea', 16, NULL, NULL, NULL, NULL, NULL, NULL, 'stock', NULL, 3, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '', NULL, '1', NULL, 1, NULL, NULL, NULL, NULL, 1, NULL),
(4, 'x1', 'test_man', 16, 'specsss', 'sizeeee', 'ssssss sss', 'cccccccc', 'ccccccc', 'gggggg', 'stock', 'ttttttttt', 3, 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, 2, 10, '2', 5, '2', 1, '2', 1, 10, '1', 5, '1', 1, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '', NULL, '1', NULL, 1, 25, 50, NULL, 10000, 10, NULL),
(5, 'ad', 'asda', 16, 'adas', NULL, NULL, NULL, NULL, NULL, 'stock', NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '', NULL, '1', NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL),
(6, 'z', 'تجريب مع صالة انتاج', 16, NULL, NULL, NULL, NULL, NULL, NULL, 'stock', NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, 1, 1, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', 1, NULL, '1', NULL, '1', NULL, '1', NULL, 0, NULL, NULL, NULL, NULL, NULL, 6);

-- --------------------------------------------------------

--
-- Table structure for table `materials.old`
--

DROP TABLE IF EXISTS `materials.old`;
CREATE TABLE IF NOT EXISTS `materials.old` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` text NOT NULL,
  `name` text NOT NULL,
  `name_en` text NOT NULL,
  `quantity` double DEFAULT '0',
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `unit` varchar(50) NOT NULL,
  `default_price` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1489 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `materials.old`
--

INSERT INTO `materials.old` (`id`, `code`, `name`, `name_en`, `quantity`, `date`, `unit`, `default_price`) VALUES
(944, 'API0002', '', 'Ibandronate sodium monohydrate', 11.11, '2020-12-10 10:39:10', 'كغ', 1),
(945, 'API0003', '', 'Finasteride', -23.982, '2020-12-10 10:39:10', 'كغ', 0),
(946, 'API0004', '', 'Cellulase', -500, '2020-12-10 10:39:10', 'كغ', 0),
(947, 'API0009', '', 'Sodium dehydrocholate', 10.13, '2020-12-10 10:39:10', '', 0),
(948, 'API0010', '', 'Sodium Valproate', 465.586, '2020-12-10 10:39:10', '', 0),
(949, 'API0011', '', 'Perindopril Arginine', 24.563, '2020-12-10 10:39:10', '', 0),
(950, 'API0012', '', 'Hyoscine Butylbromide', 0.346, '2020-12-10 10:39:10', '', 0),
(951, 'API0013', '', 'Paracetamol DC', 12, '2020-12-10 10:39:10', '', 0),
(952, 'API0014', '', 'Glutamic acid', 49.95, '2020-12-10 10:39:10', '', 0),
(953, 'API0018', '', 'Orlistat as pellets', 0, '2020-12-10 10:39:10', 'كغ', 0),
(954, 'API0019', '', 'Metronidazole', 5.228, '2020-12-10 10:39:10', '', 0),
(955, 'API0020', '', 'Spiramycin', 0, '2020-12-10 10:39:10', '', 0),
(956, 'API0021', '', 'Tiaprofenic Acid', 0.007, '2020-12-10 10:39:10', '', 0),
(957, 'API0022', '', 'L-Isoleucine', 236.091, '2020-12-10 10:39:10', '', 0),
(958, 'API0023', '', 'MSM (methylsulfonylmethane, from optiMSM)', 191.493, '2020-12-10 10:39:10', '', 0),
(959, 'API0024', '', 'Creatine(monohydrate)', 1808.99, '2020-12-10 10:39:10', '', 0),
(960, 'API0025', '', 'Chondroitin sulfate(from chondroitin sulfate sodium)', 510.257, '2020-12-10 10:39:10', '', 0),
(961, 'API0027', '', 'L-Leucine', 392.262, '2020-12-10 10:39:10', '', 0),
(962, 'API0028', '', 'L -Valine', 231.497, '2020-12-10 10:39:10', '', 0),
(963, 'API0029', '', 'L -Glutamine', 1297.793, '2020-12-10 10:39:10', '', 0),
(964, 'API0030', '', 'Ciprofloxacin Base', 1.596, '2020-12-10 10:39:10', '', 0),
(965, 'API0031', '', 'Ciprofloxacin HCI / Hydrochloride', 16.056, '2020-12-10 10:39:10', '', 0),
(966, 'API0032', '', 'Hydrochlorothiazide / HCT', 35.657, '2020-12-10 10:39:10', '', 0),
(967, 'API0033', '', 'Valsartan', 297.675, '2020-12-10 10:39:10', '', 0),
(968, 'API0034', '', 'Metformin HCT /Hydrochloride', 7704.583, '2020-12-10 10:39:10', '', 0),
(969, 'API0035', '', 'Amlodipine (Besylate)', 8.768, '2020-12-10 10:39:10', '', 0),
(970, 'API0036', '', 'Rosuvastatin', 24.99, '2020-12-10 10:39:10', '', 0),
(971, 'API0037', 'فلوكونازول', 'Fluconazole', 68.79, '2020-12-10 10:39:10', '', 0),
(972, 'API0038', '', 'Lansoprazole', 500.451, '2020-12-10 10:39:10', '', 0),
(973, 'API0039', '', 'Sitagliptin Phosphate Monohydrate', 16.565, '2020-12-10 10:39:10', '', 0),
(974, 'API0043', '', 'Doxazosin(Mesilate)', 0.003, '2020-12-10 10:39:10', '', 0),
(975, 'API0044', '', 'Diosmin & Hesperidin', 5.018, '2020-12-10 10:39:10', '', 0),
(976, 'API0045', '', 'Iron carbonyl ,Zinc sulfate ,Folic acid(as pellets)', 0.794, '2020-12-10 10:39:10', '', 0),
(977, 'API0048', '', 'Cholecalciferol-Vitamin-D3', 137.292, '2020-12-10 10:39:10', '', 0),
(978, 'API0049', '', 'Chlorpheniramine maleate', 18.958, '2020-12-10 10:39:10', '', 0),
(979, 'API0051', '', 'Calcium carbonate', 6211.253, '2020-12-10 10:39:10', '', 0),
(980, 'API0052', '', 'Cupric Sulphate Anhydrous AR', 0, '2020-12-10 10:39:10', '', 0),
(981, 'API0057', '', 'pyridoxine hcl hydrocloride', 142.208, '2020-12-10 10:39:10', '', 0),
(982, 'API0058', '', 'Cyanocobalamin', 0.007, '2020-12-10 10:39:10', '', 0),
(983, 'API0059', '', 'Thiamine hydrochloride', 143.208, '2020-12-10 10:39:10', '', 0),
(984, 'API0060', '', 'Betamethasone', 3.231, '2020-12-10 10:39:10', '', 0),
(985, 'API0061', '', 'Diclofenac sodium', 551.093, '2020-12-10 10:39:10', '', 0),
(986, 'API0063', '', 'Pentoxifyllime', 134.478, '2020-12-10 10:39:10', '', 0),
(987, 'API0064', '', 'cilostazol', 10.827, '2020-12-10 10:39:10', '', 0),
(988, 'API0065', '', 'Loperamide hydrochloride', 0.803, '2020-12-10 10:39:10', '', 0),
(989, 'API0066', '', 'Simethicone powder 50%', 104.409, '2020-12-10 10:39:10', '', 0),
(990, 'API0067', '', 'Ibuprofen', 92.921, '2020-12-10 10:39:10', '', 0),
(991, 'API0068', '', 'Alanine', 94.793, '2020-12-10 10:39:10', '', 0),
(992, 'API0069', '', 'Glycine', 66.772, '2020-12-10 10:39:10', '', 0),
(993, 'API0070', '', 'Serine', 93.261, '2020-12-10 10:39:10', '', 0),
(994, 'API0071', '', 'Aspartic acide', 225.352, '2020-12-10 10:39:10', '', 0),
(995, 'API0072', '', 'Proline', 119.421, '2020-12-10 10:39:10', '', 0),
(996, 'API0073', '', 'Histidine', 37.244, '2020-12-10 10:39:10', '', 0),
(997, 'API0074', '', 'Tyrosine', 65.181, '2020-12-10 10:39:10', '', 0),
(998, 'API0075', '', 'Cystine', 27.927, '2020-12-10 10:39:10', '', 0),
(999, 'API0076', '', 'Arginine', 111.721, '2020-12-10 10:39:10', '', 0),
(1000, 'API0077', '', 'Methionine', 37.27, '2020-12-10 10:39:10', '', 0),
(1001, 'API0078', '', 'Phenylalanine', 85.457, '2020-12-10 10:39:10', '', 0),
(1002, 'API0079', '', 'Threonine', 104.025, '2020-12-10 10:39:10', '', 0),
(1003, 'API0080', '', 'Tryptophan', 37.223, '2020-12-10 10:39:10', '', 0),
(1004, 'API0081', '', 'Indapamide', 4.576, '2020-12-10 10:39:10', '', 0),
(1005, 'API0082', '', 'Sodium bicarbonate', 1871.151, '2020-12-10 10:39:10', '', 0),
(1006, 'API0084', '', 'Ondansetrone Hydrochloride', 0.966, '2020-12-10 10:39:10', '', 0),
(1007, 'API0085', '', 'Omeprazole', 16.989, '2020-12-10 10:39:10', '', 0),
(1008, 'API0086', '', 'Sodium Hyaluronate', 21.55, '2020-12-10 10:39:10', '', 0),
(1009, 'API0087', '', 'Methocarbamol', 474.366, '2020-12-10 10:39:10', '', 0),
(1010, 'API0089', '', 'Lysine Base', 150.25, '2020-12-10 10:39:10', '', 0),
(1011, 'API0090', '', 'Glucosamine Hydrochloride', 577.82, '2020-12-10 10:39:10', '', 0),
(1012, 'API0092', '', 'Sacubitril Valsartan Sodium Salt Complex', 21.47, '2020-12-10 10:39:10', '', 0),
(1013, 'API0093', '', 'Dextromethorphan Hydrobromide', 4.744, '2020-12-10 10:39:10', '', 0),
(1014, 'API0094', '', 'Paracetamol powder', 1072.86, '2020-12-10 10:39:10', '', 0),
(1015, 'API0095', '', 'Dapagliflozin propanediol monohydrate', 8.888, '2020-12-10 10:39:10', '', 0),
(1016, 'API0096', '', 'Phenylephrine Hydrochloride', 60.535, '2020-12-10 10:39:10', '', 0),
(1017, 'API0098', '', 'atorvastatine calcium', 0.297, '2020-12-10 10:39:10', '', 0),
(1018, 'API0099', '', 'ezitmbe', 1.4, '2020-12-10 10:39:10', '', 0),
(1019, 'API0102', '', 'Sodium Polystyrene Sulphonate', 2465.464, '2020-12-10 10:39:10', '', 0),
(1020, 'API0103', 'انتيكافير', 'ENTECAVIR', 0.116, '2020-12-10 10:39:10', 'كغ', 0),
(1021, 'API0104', '', 'DEFERASIROX', 30.174, '2020-12-10 10:39:10', '', 0),
(1022, 'API0105', '', 'pregabalin ih', 0.183, '2020-12-10 10:39:10', '', 0),
(1023, 'API0106', '', 'Ibuprofen Lysinate', 58.157, '2020-12-10 10:39:10', '', 0),
(1024, 'API0107', '', 'Sevelamer Hydrochloride', 69.332, '2020-12-10 10:39:10', '', 0),
(1025, 'API0111', '', 'Magnesium-Hydroxide', 7.592, '2020-12-10 10:39:10', '', 0),
(1026, 'API0112', '', 'Zinc-Sulfate-Heptahydrate', 21.895, '2020-12-10 10:39:10', '', 0),
(1027, 'API0113', '', 'Copper-Sulfate-Pentahydrate', 10.499, '2020-12-10 10:39:10', '', 0),
(1028, 'API0114', '', 'Sodium-Selenate', 0.815, '2020-12-10 10:39:10', '', 0),
(1029, 'API0119', '', 'Alpha-Lipoic-Acid', 0.221, '2020-12-10 10:39:10', '', 0),
(1030, 'API0120', '', 'Rivaroxaban', 7.129, '2020-12-10 10:39:10', '', 0),
(1031, 'API0121', '', 'Ondansetrone', 0.237, '2020-12-10 10:39:10', '', 0),
(1032, 'API0122', '', 'Manganese(11) Sulphate (Mono)', 9.842, '2020-12-10 10:39:10', '', 0),
(1033, 'API0124', '', 'Sodium-Metaborate(Tetrahydrate)', 0.095, '2020-12-10 10:39:10', '', 0),
(1034, 'API0125', '', 'Ascorbic Acid (Vitamin C)', 35.721, '2020-12-10 10:39:10', '', 0),
(1035, 'API0126', '', 'Aprepitant pellets 40%', 28.777, '2020-12-10 10:39:10', '', 0),
(1036, 'API0127', '', 'Golden Vit -Dc Granules', 0, '2020-12-10 10:39:10', '', 0),
(1037, 'API0129', '', 'Bone Aid-Dc Granules', 1.841, '2020-12-10 10:39:10', '', 0),
(1038, 'API0130', '', 'Diosmin', 0, '2020-12-10 10:39:10', '', 0),
(1039, 'API0131', '', 'Hesperidin', 0, '2020-12-10 10:39:10', '', 0),
(1040, 'API0133', '', 'Zinc Sulphate GR Heptahydrate', 0.006, '2020-12-10 10:39:10', '', 0),
(1041, 'API0134', '', 'Di-Sodium Tetraborate Decahydrate 99%(Extra Pure)', 0.016, '2020-12-10 10:39:10', '', 0),
(1042, 'API0135', '', 'Di-Sodium -Tetraborate -Decahydrate 99.5%(Borax) AR/ACS', 2.388, '2020-12-10 10:39:10', '', 0),
(1043, 'API0136', '', 'Coenzyme Q10', 9.976, '2020-12-10 10:39:10', '', 0),
(1044, 'API0137', '', 'Dexlansoprazole Pellets', 534.958, '2020-12-10 10:39:10', '', 0),
(1045, 'API0140', '', 'telmisartan', 96.756, '2020-12-10 10:39:10', '', 0),
(1046, 'API0141', '', 'Copper -Sulfate Anhydrous (Extra pure)', 0.037, '2020-12-10 10:39:10', '', 0),
(1047, 'API0142', '', 'manganese sulfate monohydrate (99-100)%', 2.162, '2020-12-10 10:39:10', '', 0),
(1048, 'ERM0003', '', 'Colloidal silicon dioxide', 332.291, '2020-12-10 10:39:10', '', 0),
(1049, 'ERM0004', '', 'Crospovidone', 215.086, '2020-12-10 10:39:10', '', 0),
(1050, 'ERM0006', '', 'Docusate sodium', 0, '2020-12-10 10:39:10', '', 0),
(1051, 'ERM0008', '', 'Hypromellose', 698.391, '2020-12-10 10:39:10', '', 0),
(1052, 'ERM0010', '', 'Iron oxide red', 5.695, '2020-12-10 10:39:10', '', 0),
(1053, 'ERM0011', '', 'Iron oxide yellow', 0.18, '2020-12-10 10:39:10', '', 0),
(1054, 'ERM0012', '', 'Lactose monohydrate', 258.698, '2020-12-10 10:39:10', '', 0),
(1055, 'ERM0013', '', 'Magnesium stearate', 358.612, '2020-12-10 10:39:10', '', 0),
(1056, 'ERM0014', '', 'Maize starch', 161.689, '2020-12-10 10:39:10', '', 0),
(1057, 'ERM0015', '', 'Microcrystalline cellulose 102', 671.081, '2020-12-10 10:39:10', '', 0),
(1058, 'ERM0017', '', 'Polyethylene glycol 6000', 266.854, '2020-12-10 10:39:10', '', 0),
(1059, 'ERM0018', '', 'Povidone k30', 977.586, '2020-12-10 10:39:10', '', 0),
(1060, 'ERM0019', '', 'Sodium lauryi sulfate', 11.151, '2020-12-10 10:39:10', '', 0),
(1061, 'ERM0020', '', 'Stearic acid', 23.575, '2020-12-10 10:39:10', '', 0),
(1062, 'ERM0021', '', 'Talc', 755.479, '2020-12-10 10:39:10', '', 0),
(1063, 'ERM0022', '', 'Titanium dioxide', 146.377, '2020-12-10 10:39:10', '', 0),
(1064, 'ERM0024', '', 'Sodium hydroxide', 1, '2020-12-10 10:39:10', '', 0),
(1065, 'ERM0025', '', 'Triethyl citrate', 0.124, '2020-12-10 10:39:10', '', 0),
(1066, 'ERM0027', '', 'Capsule-Gelatine-Size 1-(C) turquoise-(B) turquoise', 189173, '2020-12-10 10:39:10', '', 0),
(1067, 'ERM0028', '', 'Capsule-Gelatine-Size 1-(C) purple-(B) tranc', 361049.152, '2020-12-10 10:39:10', '', 0),
(1068, 'ERM0029', '', 'Capsule- Gelatin-Size 0-(C) white-(B) white', 721753, '2020-12-10 10:39:10', '', 0),
(1069, 'ERM0032', '', 'Capsule- Gelatin-Size 3-(C) green - (B) green', 983419, '2020-12-10 10:39:10', '', 0),
(1070, 'ERM0035', '', 'Microcrystalline cellulose 101', 799.324, '2020-12-10 10:39:10', '', 0),
(1071, 'ERM0036', '', 'Croscarmellose sodium', 200.953, '2020-12-10 10:39:10', '', 0),
(1072, 'ERM0037', '', 'Sunset yellow FCF', 2.494, '2020-12-10 10:39:10', '', 0),
(1073, 'ERM0038', '', 'Isopropyl alcohol', 0, '2020-12-10 10:39:10', '', 0),
(1074, 'ERM0040', '', 'Brilliant Blue lake', 7.809, '2020-12-10 10:39:10', '', 0),
(1075, 'ERM0042', '', 'Sucralose', 8.119, '2020-12-10 10:39:10', '', 0),
(1076, 'ERM0046', '', 'Mannitol', 125.586, '2020-12-10 10:39:10', '', 0),
(1077, 'ERM0048', '', 'Aspartam', 25.152, '2020-12-10 10:39:10', '', 0),
(1078, 'ERM0051', '', 'Anhydrous lactose', 155.427, '2020-12-10 10:39:10', '', 0),
(1079, 'ERM0052', '', 'Ethyl Alcohol 100%', 15775.634, '2020-12-10 10:39:10', '', 0),
(1080, 'ERM0053', '', 'Sorbitol powder', 200.31, '2020-12-10 10:39:10', '', 0),
(1081, 'ERM0054', '', 'Sodium starch glycolate type A', 445.536, '2020-12-10 10:39:10', '', 0),
(1082, 'ERM0055', '', 'Carboxymethylcellulose sodium', 17.782, '2020-12-10 10:39:10', '', 0),
(1083, 'ERM0062', '', 'Capsule-Gelatine-Size 2-(C) red-(B) off-white', 39167, '2020-12-10 10:39:10', '', 0),
(1084, 'ERM0064', '', 'Hypromellose phthalate_ hp 55', 228.974, '2020-12-10 10:39:10', '', 0),
(1085, 'ERM0065', '', 'Capsule-Gelatine-Size00 -(C) white -(B) white', 281341, '2020-12-10 10:39:10', '', 0),
(1086, 'ERM0066', '', 'Capsule-Gelatine-Size00 -(C) off-white-(B) off-white', 456972, '2020-12-10 10:39:10', '', 0),
(1087, 'ERM0067', '', 'Capsule-Gelatine-Size 3 -(C) black -(B) red', 385240, '2020-12-10 10:39:10', '', 0),
(1088, 'ERM0068', '', 'Capsule-Gelatine-Size 2-(C) blue -(B) pink', 736712.719, '2020-12-10 10:39:10', '', 0),
(1089, 'ERM0069', '', 'Capsule-Gelatine-Size 1-(C) red-(B) tranc', 28044, '2020-12-10 10:39:10', '', 0),
(1090, 'ERM0070', '', 'Maltodextrin', 116.444, '2020-12-10 10:39:10', '', 0),
(1091, 'ERM0071', '', 'ACETONE', 1953.217, '2020-12-10 10:39:10', '', 0),
(1092, 'ERM0072', '', 'Lake ponceau 4R E124', 4.998, '2020-12-10 10:39:10', '', 0),
(1093, 'ERM0073', '', 'Acesulfame potassium', 24.855, '2020-12-10 10:39:10', '', 0),
(1094, 'ERM0074', '', 'Vanillin', 0.435, '2020-12-10 10:39:10', '', 0),
(1095, 'ERM0075', '', 'Dibasic calsium phosphate Anhydrouse', 364.44, '2020-12-10 10:39:10', '', 0),
(1096, 'ERM0077', '', 'Hydroxyethyl cellulose', 23.966, '2020-12-10 10:39:10', '', 0),
(1097, 'ERM0079', '', 'Sorbitan Monooleate Polyoxyethylene (Tween 80)', 4.906, '2020-12-10 10:39:10', '', 0),
(1098, 'ERM0085', '', 'Propylene glycol', 213.893, '2020-12-10 10:39:10', '', 0),
(1099, 'ERM0086', '', 'Pregelatinized starch', 141.309, '2020-12-10 10:39:10', '', 0),
(1100, 'ERM0088', '', 'Xanthan gum', 219.707, '2020-12-10 10:39:10', '', 0),
(1101, 'ERM0089', '', 'Povidone K90', 23.975, '2020-12-10 10:39:10', '', 0),
(1102, 'ERM0091', '', 'Soybean lecthin', 0.9, '2020-12-10 10:39:10', '', 0),
(1103, 'ERM0092', '', 'Hypromellos 100000', 109.615, '2020-12-10 10:39:10', '', 0),
(1104, 'ERM0093', '', 'Castor Oil', 91.59, '2020-12-10 10:39:10', '', 0),
(1105, 'ERM0094', '', 'Lactose DC', 141.565, '2020-12-10 10:39:10', '', 0),
(1106, 'ERM0095', '', 'Capsule-Gelatine-Size 0-body:white-cap:red', 94840, '2020-12-10 10:39:10', '', 0),
(1107, 'ERM0097', '', 'Brilliant Blue E133', 2.866, '2020-12-10 10:39:10', '', 0),
(1108, 'ERM0098', '', 'Sunset-yellow-85%', 2.158, '2020-12-10 10:39:10', '', 0),
(1109, 'ERM0100', '', 'Tartrazine-E102', 0.872, '2020-12-10 10:39:10', '', 0),
(1110, 'ERM0101', '', 'Capsule-Gelatin-Size 3 -(C ) Brick - (B) trans', 211519, '2020-12-10 10:39:10', '', 0),
(1111, 'ERM0102', '', 'B.H.T Butilidrossitoluolo', 1.939, '2020-12-10 10:39:10', '', 0),
(1112, 'ERM0103', '', 'Hydroquinon', 0, '2020-12-10 10:39:10', '', 0),
(1113, 'ERM0104', '', 'sodium saccharin', 22.004, '2020-12-10 10:39:10', '', 0),
(1114, 'ERM0105', '', 'erythrosin lake E 127', 1.894, '2020-12-10 10:39:10', '', 0),
(1115, 'ERM0107', '', 'microcrystalline cellulose 113', 321.923, '2020-12-10 10:39:10', '', 0),
(1116, 'ERM0108', '', 'Capsule-Gelatine-size(00)-(c)red-(B) white', 1134500, '2020-12-10 10:39:10', '', 0),
(1117, 'ERM0109', '', 'capsule-size(00)-(c) green-(B)white', 1007250.7, '2020-12-10 10:39:10', '', 0),
(1118, 'ERM0111', '', 'Micro Crystalline Cellulose 112', 380.938, '2020-12-10 10:39:10', '', 0),
(1119, 'ERM0113', '', 'crosspovidone-Type(B)', 6.019, '2020-12-10 10:39:10', '', 0),
(1120, 'ERM0114', '', 'EDTA Disodium', -216.06499999999986, '2020-12-10 10:39:10', '', 0),
(1121, 'ERM0115', '', 'Methyl Paraben Sodium', 0.401, '2020-12-10 10:39:10', '', 0),
(1122, 'ERM0116', '', 'Propyl Paraben Sodium', 3.317, '2020-12-10 10:39:10', '', 0),
(1123, 'ERM0117', '', 'Sodium-Metabisulphite', 0.346, '2020-12-10 10:39:10', '', 0),
(1124, 'ERM0119', '', 'Sodium-Hypochlorite', 38.634, '2020-12-10 10:39:10', '', 0),
(1125, 'ERM0120', '', 'Black-E151', 0.98, '2020-12-10 10:39:10', '', 0),
(1126, 'ERM0121', '', 'Sodium Ascorbate', 1.797, '2020-12-10 10:39:10', '', 0),
(1127, 'ERM0123', '', 'Citric Acid Anhydrous', 18.563, '2020-12-10 10:39:10', '', 0),
(1128, 'ERM0124', '', 'Sodium Stearyl Fumarate', 15.866, '2020-12-10 10:39:10', '', 0),
(1129, 'ERM0125', '', 'Sodium Benzoate', 24.983, '2020-12-10 10:39:10', '', 0),
(1130, 'ERM0126', '', 'polyethlene glycol 6000-powder', 296.301, '2020-12-10 10:39:10', '', 0),
(1131, 'ERM0127', '', 'Calcium Ascorbate', 24.983, '2020-12-10 10:39:10', '', 0),
(1132, 'ERM0128', '', 'Sodium Lauryl Sulfate (Extra Pure)', 0.018, '2020-12-10 10:39:10', '', 0),
(1133, 'ERM0129', '', 'Strawberry Flavor (Powder)', 3.29, '2020-12-10 10:39:10', '', 0),
(1134, 'ERM0130', '', 'ALUMINUM MAGNESIUM SILSCATE (VECGUM)', 28.226, '2020-12-10 10:39:10', '', 0),
(1135, 'ERM0131', '', 'microcrystalline cellulose 200', 245.523, '2020-12-10 10:39:10', '', 0),
(1136, 'ERM0132', '', 'Dibutyl phthalate', 238.896, '2020-12-10 10:39:10', '', 0),
(1137, 'ERM0136', '', 'Sodium Hypochlorite 12%', 0.0005, '2020-12-10 10:39:10', '', 0),
(1138, 'PPM0001', '', 'Aluminum roll - unprinted on it- width 260 mm', 28.3, '2020-12-10 10:39:10', '', 0),
(1139, 'PPM0002', '', 'P V C -Trans-Width 260 mm', 38.09, '2020-12-10 10:39:10', '', 0),
(1140, 'PPM0004', '', 'Aluminum -Dentazol- F.C.Tablets-width 260 mm', 35.61, '2020-12-10 10:39:10', '', 0),
(1141, 'PPM0005', '', 'Aluminum -Dentazol Fort- F.C.Tablets-width 260 mm', 58.03, '2020-12-10 10:39:10', '', 0),
(1142, 'PPM0006', '', 'PVDC- Milky -Width 260 mm', 2095.526, '2020-12-10 10:39:10', '', 0),
(1143, 'PPM0007', '', 'PVDC- Trans -Width 260 mm', 7014.79, '2020-12-10 10:39:10', '', 0),
(1144, 'PPM0008', '', 'Aluminum -Finaprost-5mg - F.C.Tab-width 260 mm', 14, '2020-12-10 10:39:10', '', 0),
(1145, 'PPM0009', '', 'Aluminum -Fــ Z ــ gold- Cap-width 260 mm', 40.02, '2020-12-10 10:39:10', '', 0),
(1146, 'PPM0010', '', 'Aluminum -Gold stat- 120 mg-Cap-width 260 mm', 7.1, '2020-12-10 10:39:10', '', 0),
(1147, 'PPM0011', '', 'Aluminum -Duogaste- 15 mg -Cap-width 260 mm', 32.88, '2020-12-10 10:39:10', '', 0),
(1148, 'PPM0012', '', 'Aluminum -Duogaste- 30 mg-Cap-width 260 mm', 3.5, '2020-12-10 10:39:10', '', 0),
(1149, 'PPM0013', '', 'Aluminum -Flocozol - 50 mg- Cap-width 260 mm', 15.65, '2020-12-10 10:39:10', '', 0),
(1150, 'PPM0014', '', 'Aluminum -Flocozol -150 mg-Cap-width 260 mm', 17.9, '2020-12-10 10:39:10', '', 0),
(1152, 'PPM0016', '', 'Aluminum -Vartan - 80 mg-Cap-width 260 mm', 22.06, '2020-12-10 10:39:10', '', 0),
(1153, 'PPM0017', '', 'Aluminum -Vartan- 160 mg-Cap-width 260 mm', 0, '2020-12-10 10:39:10', '', 0),
(1154, 'PPM0018', '', 'Aluminum -Glucostop- 850 mg-Retard- C.Tabs-width 260 mm', 30.23, '2020-12-10 10:39:10', '', 0),
(1155, 'PPM0019', '', 'Aluminum -Neurpain- E.C.Tabs-width 260 mm', 23.91, '2020-12-10 10:39:10', '', 0),
(1156, 'PPM0020', '', 'Aluminum -Diclocort-B12- F.C.Tabs-width 260 mm', 0, '2020-12-10 10:39:10', '', 0),
(1157, 'PPM0021', '', 'Aluminum -Buscogold plus- F.C.Tabs-width 260 mm', 24.281, '2020-12-10 10:39:10', '', 0),
(1158, 'PPM0022', '', 'Aluminum -Coronasyl-2.5 mg- F.C.Tabs-width 260 mm', 11.94, '2020-12-10 10:39:10', '', 0),
(1159, 'PPM0023', '', 'Aluminum -Coronasyl-5 mg- F.C.Tabs-width 260 mm', 13.94, '2020-12-10 10:39:10', '', 0),
(1160, 'PPM0024', '', 'Aluminum -Coronasyl-10 mg- F.C.Tabs-width 260 mm', 72.2, '2020-12-10 10:39:10', '', 0),
(1161, 'PPM0025', '', 'Aluminum -Daflogold- F.C.Tabs-width 260 mm', 2.463, '2020-12-10 10:39:10', '', 0),
(1162, 'PPM0026', '', 'Aluminum -SACUVAL-24/26 mg- F.C.Tabs-width 260 mm', 25.93, '2020-12-10 10:39:10', '', 0),
(1163, 'PPM0027', '', 'Aluminum -SACUVAL-49/51 mg- F.C.Tabs-width 260 mm', 41.63, '2020-12-10 10:39:10', '', 0),
(1164, 'PPM0028', '', 'Aluminum -SACUVAL-97/103mg- F.C.Tabs-width 260 mm', 48.2, '2020-12-10 10:39:10', '', 0),
(1165, 'PPM0029', '', 'Alu-Alu-Cold Forming Blister Foil-Width225mm', 503.618, '2020-12-10 10:39:10', '', 0),
(1166, 'PPM0030', '', 'Aluminum -Dapagold-5mg-F.C.Tab-width 225 mm', 53.004, '2020-12-10 10:39:10', '', 0),
(1167, 'PPM0031', '', 'Aluminum -coronasyl AM 5/10 mg-F.C.Tab-width 260 mm', 124.43, '2020-12-10 10:39:10', '', 0),
(1168, 'PPM0032', '', 'Aluminum -coronasyl AM 10/5 mg-F.C.Tab-width 260 mm', 0, '2020-12-10 10:39:10', '', 0),
(1169, 'PPM0033', '', 'Aluminum -No flu day -Caplets-width 260 mm', 46.465, '2020-12-10 10:39:10', '', 0),
(1170, 'PPM0034', '', 'Aluminum -No flu night -Caplets-width 260 mm', 13.497, '2020-12-10 10:39:10', '', 0),
(1171, 'PPM0035', '', 'Aluminum -No flu HBP -F.C.Caplets-width 260 mm', 141.458, '2020-12-10 10:39:10', '', 0),
(1172, 'PPM0036', '', 'Aluminum -coronasyl AM 5/5 mg-F.C.Tab-width 260 mm', 30.15, '2020-12-10 10:39:10', '', 0),
(1173, 'PPM0037', '', 'Aluminum -coronasyl 10/10mg-F.C.Tab-width 260 mm', 19.4, '2020-12-10 10:39:10', '', 0),
(1174, 'PPM0038', '', 'Aluminum -Dapagold-10mg-F.C.Tab-width 225mm', 38.253, '2020-12-10 10:39:10', '', 0),
(1175, 'PPM0039', '', 'Aluminum -Imodicon-Tab-width 260 mm', 21, '2020-12-10 10:39:10', '', 0),
(1176, 'PPM0040', '', 'Aluminum -VartanPlus160/10-F.C.Tab-width 260 mm', 19.64, '2020-12-10 10:39:10', '', 0),
(1177, 'PPM0041', '', 'Aluminum -VartanPlus320/5-F.C.Tab-width 260 mm', 19.46, '2020-12-10 10:39:10', '', 0),
(1178, 'PPM0042', '', 'Aluminum -Vartan80HCT-F.C.Tab-width 260 mm', 50, '2020-12-10 10:39:10', '', 0),
(1179, 'PPM0043', '', 'Aluminum -GlucoStop-500mg-F.C.Tab-width 260 mm', 598.654, '2020-12-10 10:39:10', '', 0),
(1180, 'PPM0044', '', 'Aluminum -Pletazol-50mg-Tab-width 260 mm', 4.91, '2020-12-10 10:39:10', '', 0),
(1181, 'PPM0045', '', 'Aluminum -Pletazol-100mg-Tab-width 260 mm', 2.32, '2020-12-10 10:39:10', '', 0),
(1182, 'PPM0046', '', 'Aluminum -Vartan Plus160/5mg-F.C.Tab-width 260 mm', 18.74, '2020-12-10 10:39:10', '', 0),
(1183, 'PPM0047', '', 'Aluminum -Vartan HCT160-F.C.Tab-width 260 mm', 24.68, '2020-12-10 10:39:10', '', 0),
(1184, 'PPM0048', '', 'Aluminum-Vartan-plus320/10', 27.38, '2020-12-10 10:39:10', '', 0),
(1185, 'PPM0049', '', 'Aluminum -Pentovas-400mg-M.R.Tab-width 260 mm', 6.8, '2020-12-10 10:39:10', '', 0),
(1186, 'PPM0050', '', 'Aluminum -Heproval-40mg-F.c.Tab-width 260 mm', 24.18, '2020-12-10 10:39:10', '', 0),
(1187, 'PPM0051', '', 'Aluminum -Heproval-80mg-F.c.Tab-width 260 mm', 12.84, '2020-12-10 10:39:10', '', 0),
(1188, 'PPM0052', '', 'Aluminum -Heproval-160mg-F.c.Tab-width 260 mm', 21.15, '2020-12-10 10:39:10', '', 0),
(1189, 'PPM0054', '', 'Plastic -Containers-Black-size 750cc', 1608, '2020-12-10 10:39:10', '', 0),
(1190, 'PPM0055', '', 'Plastic -Containers-Black-size 500cc', 903, '2020-12-10 10:39:10', '', 0),
(1192, 'PPM0058', 'عبوة بلاستيكية قياس 52 ملم لون اسود', 'Plastic-Bottle-cap-size-52mm-Black', 80625, '2020-12-10 10:39:10', '', 0),
(1193, 'PPM0059', '', 'Aluminum -Surgafenic-100mg-Tab-width 260 mm', 34.7, '2020-12-10 10:39:10', '', 0),
(1194, 'PPM0060', '', 'aluminum entecavir golden 1ml', 34.3, '2020-12-10 10:39:10', '', 0),
(1195, 'PPM0061', '', 'aluminum-glumolip-50/1000', 95.28, '2020-12-10 10:39:10', '', 0),
(1196, 'PPM0062', '', 'aluminum-glumolip-50/500', 36.28, '2020-12-10 10:39:10', '', 0),
(1197, 'PPM0063', '', 'aluminum cholestor 5mg', 22.2, '2020-12-10 10:39:10', '', 0),
(1198, 'PPM0064', '', 'aluminum cholestor 10mg', 57.2, '2020-12-10 10:39:10', '', 0),
(1199, 'PPM0065', '', 'aluminum cholestor 20mg', 67.24, '2020-12-10 10:39:10', '', 0),
(1200, 'PPM0066', '', 'aluminum cholestor 40mg', 24.4, '2020-12-10 10:39:10', '', 0),
(1201, 'PPM0067', '', 'aluminum prosten 1 mg', 41.5, '2020-12-10 10:39:10', '', 0),
(1202, 'PPM0068', '', 'aluminum prosten 2 mg', 35.74, '2020-12-10 10:39:10', '', 0),
(1203, 'PPM0069', '', 'aluminum prosten 4 mg', 37.89, '2020-12-10 10:39:10', '', 0),
(1204, 'PPM0070', '', 'Aluminum Gold D3 -5000 IU', 1.46, '2020-12-10 10:39:10', '', 0),
(1205, 'PPM0071', '', 'Aluminum Robaxifen', 51.6, '2020-12-10 10:39:10', '', 0),
(1206, 'PPM0072', '', 'Aluminum-Not printined on it-Width 225mm', 12.7, '2020-12-10 10:39:10', '', 0),
(1207, 'PPM0073', '', 'Aluminum- Enticavir Golden- 0.5 mg - F.C.Taplets', 0, '2020-12-10 10:39:10', '', 0),
(1208, 'PPM0074', '', 'Plastic-Containers-Bronze-Size 150 cc', 2301, '2020-12-10 10:39:10', '', 0),
(1209, 'PPM0075', '', 'Plastic Containers Caps- Bronze-Size 38 mm', 1967, '2020-12-10 10:39:10', '', 0),
(1210, 'PPM0076', '', 'Silica gel bag-Size 2×4 cm', 214531, '2020-12-10 10:39:10', '', 0),
(1211, 'PPM0077', '', 'Aluminum-Ironfree-125mg-Dispersible tabs-width 260mm', 12.9, '2020-12-10 10:39:10', '', 0),
(1212, 'PPM0078', '', 'Aluminum -Iron Free-250mg-Dispersible Tab-width 260 mm', 10.46, '2020-12-10 10:39:10', '', 0),
(1213, 'PPM0079', '', 'Aluminum -Ironfree -500mg -Dispersible -width 260mm', 25.71, '2020-12-10 10:39:10', '', 0),
(1214, 'PPM0080', '', 'Aluminum -Nurofen fast -200 Mg-F.C.Tab -Width 260mm', 2.47, '2020-12-10 10:39:10', '', 0),
(1215, 'PPM0081', '', 'Aluminum-Nurofen fast -400 mg-F.C.Tab-Width 260mm', 4.22, '2020-12-10 10:39:10', '', 0),
(1216, 'PPM0082', '', 'pvdc-trans-width260mm-thickness60mm', 5, '2020-12-10 10:39:10', '', 0),
(1217, 'PPM0083', '', 'PVDC -Trans-Width260mm -Thickness 90mm', 5, '2020-12-10 10:39:10', '', 0),
(1218, 'PPM0087', '', 'ALuminum-omicarp 20/1100 mg-cap-width260mm', 11.13, '2020-12-10 10:39:10', '', 0),
(1219, 'PPM0088', '', 'ALuminum-omicarp 40/1100 mg-cap -width 260mm', 14.3, '2020-12-10 10:39:10', '', 0),
(1220, 'PPM0089', '', 'ALuminum-Ciprogold XR-500mg-F.C.Tab-width260mm', 12.4, '2020-12-10 10:39:10', '', 0),
(1221, 'PPM0090', '', 'ALuminum -Ciprogold XR 1000mg F.C.Tab-width 260mm', 2.3, '2020-12-10 10:39:10', '', 0),
(1222, 'PPM0091', '', 'ALuminum-Atorvamib-10/10mg-F.C.Tab.Width260mm', 26.06, '2020-12-10 10:39:10', '', 0),
(1223, 'PPM0092', '', 'Aluminum-Atorvamib-10/20mg-F.C.Tab-Width260mm', 30.88, '2020-12-10 10:39:10', '', 0),
(1224, 'PPM0093', '', 'Aluminum-Atorvamib-10/40mg-F.C.Tab-Width260mm', 16.4, '2020-12-10 10:39:10', '', 0),
(1225, 'PPM0094', '', 'Aluminum-Atorvamib-10/80mg-F.C.Tab-Width260mm', 20.8, '2020-12-10 10:39:10', '', 0),
(1226, 'PPM0095', '', 'pvc-milky-width260mm/250mic', 3.6, '2020-12-10 10:39:10', '', 0),
(1227, 'PPM0096', '', 'pvc-milky-width260mm/300mic', 3.5, '2020-12-10 10:39:10', '', 0),
(1228, 'PPM0097', '', 'pvc-trans-width260mm/250mic', 3.5, '2020-12-10 10:39:10', '', 0),
(1229, 'PPM0099', '', 'Aluminum -Coronasyl plus-2.5/0.625 mg-F.C.Tab-width 225 mm', 50.032, '2020-12-10 10:39:10', '', 0),
(1230, 'PPM0100', '', 'Aluminum-Coronasyl Plus 5/1.25 mg -F.C.Tab Width 225mm', 56.701, '2020-12-10 10:39:10', '', 0),
(1231, 'PPM0101', '', 'Aluminum-Coronasyl Plus 10/2.5 mg-F.C.Tab Width 255mm', 71.246, '2020-12-10 10:39:10', '', 0),
(1232, 'PPM0102', '', 'Aluminum-Bone Aid-Caplets-width260mm', 118.905, '2020-12-10 10:39:10', '', 0),
(1233, 'PPM0103', '', 'Aluminum-Gold D3-10000 IU F.C.Tab width 260 mm', 13.39, '2020-12-10 10:39:10', '', 0),
(1234, 'PPM0104', '', 'Aluminum-Gold D3 20000 IU F.C.Tab width 260mm', 26.64, '2020-12-10 10:39:10', '', 0),
(1235, 'PPM0105', '', 'PVDC-Trans-Width 260 mm/300 mic', 3, '2020-12-10 10:39:10', '', 0),
(1236, 'PPM0106', '', 'PVDC-Trans-Width 260mm/350 mic', 3, '2020-12-10 10:39:10', '', 0),
(1237, 'PPM0107', '', 'aluminum-dentagold-f.c.tab-width260mm', 15.3, '2020-12-10 10:39:10', '', 0),
(1238, 'PPM0108', '', 'aluminum-dentagold fort-f.c.tab-widhth260mm', 2.6, '2020-12-10 10:39:10', '', 0),
(1239, 'PPM0109', '', 'aluminum-vaxan-2.5mg-f.c.tab-width260mm', 15.49, '2020-12-10 10:39:10', '', 0),
(1240, 'PPM0110', '', 'aluminum-vaxan-10mg f.c.tab-width260mm', 52.23, '2020-12-10 10:39:10', '', 0),
(1241, 'PPM0111', '', 'aluminum-vaxan-15mg-f.c.tab-width260mm', 28.45, '2020-12-10 10:39:10', '', 0),
(1242, 'PPM0112', '', 'aluminum-vaxan20mg-f.c.tab-width260mm', 0, '2020-12-10 10:39:10', '', 0),
(1243, 'PPM0113', '', 'alumium-platica-60mg-f.c.tab-width260mm', 24.3, '2020-12-10 10:39:10', '', 0),
(1244, 'PPM0114', '', 'aluminum-platica-90mg-f.c.tab-width260mm', 22.83, '2020-12-10 10:39:10', '', 0),
(1245, 'PPM0115', '', 'Aluminum-Vomset-4 mg-Orally Disintegrating Tablet-width 225 mm', 50.88, '2020-12-10 10:39:10', '', 0),
(1246, 'PPM0116', '', 'Aluminum-Vomset-8 mg-Orally Disintegrating Tablet-width 225 mm', 20.93, '2020-12-10 10:39:10', '', 0),
(1247, 'PPM0119', '', 'aluminum-vomend-40mg-capsules-width260mm', 23.85, '2020-12-10 10:39:10', '', 0),
(1248, 'PPM0120', '', 'aluminum-vomend-80mg-capsules-width260mm', 0, '2020-12-10 10:39:10', '', 0),
(1249, 'PPM0121', '', 'aluminum-vomend-125mg-capsules-width260mm', 0, '2020-12-10 10:39:10', '', 0),
(1250, 'PPM0122', '', 'Alu-Alu-Cold Forming Blister -Foil-Width 260 mm', 26.84, '2020-12-10 10:39:10', '', 0),
(1251, 'PPM0123', '', 'aluminum-bonebuild150mg-f.c.tab-width260mm', 22.73, '2020-12-10 10:39:10', '', 0),
(1252, 'PPM0124', '', 'Plastic-Containers-White-Size 750cc-Round', 30, '2020-12-10 10:39:10', '', 0),
(1253, 'PPM0130', '', 'aluminum-coronasyl tri 5/1.25/5mg width 225mm', 45.56, '2020-12-10 10:39:10', '', 0),
(1254, 'PPM0131', '', 'aluminum-coronasyl tri 2.5/0.625/5mg', 64.66, '2020-12-10 10:39:10', '', 0),
(1255, 'PPM0132', '', 'aluminum-coronasyl tri 5/1.25/10mg-f.c.tab width 225mm', 66.16, '2020-12-10 10:39:10', '', 0),
(1256, 'PPM0133', '', 'aluminum-coronasyl tri 10/2.5/5mg f.c.tab width 225mm', 62.23, '2020-12-10 10:39:10', '', 0),
(1257, 'PPM0134', '', 'aluminum-coronasyl tri 10/2.5/10mg f.c.tab width 225mm', 56.28, '2020-12-10 10:39:10', '', 0),
(1258, 'PPM0135', '', 'PVDC-Milky-Width 260mm/250mic/Gramage 90', 0.002, '2020-12-10 10:39:10', '', 0),
(1259, 'PPM0136', '', 'PVDC-Trans-Width 260mm/250mic/Gramage 90', 0.002, '2020-12-10 10:39:10', '', 0),
(1260, 'PPM0138', '', 'PVDC-Milky-Width 260mm/350mic/Gramage 60', 836.26, '2020-12-10 10:39:10', '', 0),
(1261, 'PPM0139', '', 'Aluminum-Maxilans-30 mg -Cap-Width 260mm', 71.549, '2020-12-10 10:39:10', '', 0),
(1262, 'PPM0140', '', 'Aluminum-Maxilans-60 mg-Cap-Width 260 mm', 37.79, '2020-12-10 10:39:10', '', 0),
(1263, 'PPM0141', '', 'Aluminum-Filamir-400 mg-F.C.Caplets-Width 260 mm', 14.6, '2020-12-10 10:39:10', '', 0),
(1264, 'PPM0142', '', 'aluminum-filamir-800mg-f.c.caplets-width260mm', 61.39, '2020-12-10 10:39:10', '', 0),
(1265, 'PPM0143', '', 'aluminum-dapagoldplus5/850mg-f.c.caplets width 225mm', 205.788, '2020-12-10 10:39:10', '', 0),
(1266, 'PPM0144', '', 'aluminum-dapagold plus 5/1000mg-f.c.calplets width 225', 242.257, '2020-12-10 10:39:10', '', 0),
(1267, 'PPM0148', '', 'Aluminum-Epiless-200 mg-E.C.Tablets-Width 260 mm', 48.38, '2020-12-10 10:39:10', '', 0),
(1268, 'SPM0001', '', 'Carton -Dentazol - 20 F. C. Tablets in PVC', 59765, '2020-12-10 10:39:10', '', 0),
(1269, 'SPM0002', '', 'Carton -Dentazol Fort - 20 F. C. Tablets in PVC', 48470, '2020-12-10 10:39:10', '', 0),
(1270, 'SPM0003', '', 'Leaflets - Dentazol &Dentazol Fort - ( F. C.Tablets )', 100530, '2020-12-10 10:39:10', '', 0),
(1271, 'SPM0004', '', 'Carton-Golden-B12-1000 mcg', 900, '2020-12-10 10:39:10', '', 0),
(1272, 'SPM0005', '', 'Carton- Vartan- 80mg- 30 Cap', 6499, '2020-12-10 10:39:10', '', 0),
(1273, 'SPM0006', '', 'Carton Vartan- 160mg- 30 Cap', 5952, '2020-12-10 10:39:10', '', 0),
(1274, 'SPM0007', '', 'Leaflets-Vartan- (Caps-F.C.Tab)', 20722, '2020-12-10 10:39:10', '', 0),
(1275, 'SPM0008', '', 'Carton- Duogaste-30mg-20 Cap', 60393, '2020-12-10 10:39:10', '', 0),
(1276, 'SPM0009', '', 'Carton- Duogaste-15mg-20 Cap', 1166, '2020-12-10 10:39:10', '', 0),
(1277, 'SPM0010', '', 'Leaflets- Duogaste -Caps', 97257, '2020-12-10 10:39:10', '', 0),
(1278, 'SPM0011', '', 'Carton-Goldstat-120mg -20 Cap', 61974, '2020-12-10 10:39:10', '', 0),
(1279, 'SPM0012', '', 'Leaflets-Goldstat-Cap', 61812, '2020-12-10 10:39:10', '', 0),
(1280, 'SPM0013', '', 'Carton-F Z Gold -20 Cap', 59208, '2020-12-10 10:39:10', '', 0),
(1281, 'SPM0014', '', 'Leaflets-F Z Gold -Cap', 97424, '2020-12-10 10:39:10', '', 0),
(1282, 'SPM0015', '', 'Carton-Finaprost-5 mg -20 F.C.Tab', 14425, '2020-12-10 10:39:10', '', 0),
(1283, 'SPM0016', '', 'Leaflets- Finaprost- F.C.Tabs', 21634, '2020-12-10 10:39:11', '', 0),
(1284, 'SPM0017', '', 'Carton- Flocozol-200 mg-10 Cap', 31910, '2020-12-10 10:39:11', '', 0),
(1285, 'SPM0018', '', 'Carton -Flocozol-150 mg-10 Cap', 59364, '2020-12-10 10:39:11', '', 0),
(1286, 'SPM0019', '', 'Carton- Flocozol- 50 mg-10 Cap', 19151, '2020-12-10 10:39:11', '', 0),
(1287, 'SPM0020', '', 'Leaflets-Flocozol-Cap', 104065, '2020-12-10 10:39:11', '', 0),
(1288, 'SPM0021', '', 'Carton- Glucostop- 850 mg-Retard-30 F.C.Tab', 57269, '2020-12-10 10:39:11', '', 0),
(1289, 'SPM0022', '', 'Leaflets - Glucostop- (Tabs-CoatedTabs)', 346785, '2020-12-10 10:39:11', '', 0),
(1290, 'SPM0024', '', 'Box-White-Printed gmp on it-SIZE-19x36x22', 5456, '2020-12-10 10:39:11', '', 0),
(1291, 'SPM0025', '', 'Carton- Neurpain-20 E.C.Tab', 54300, '2020-12-10 10:39:11', '', 0),
(1292, 'SPM0026', '', 'Leaflets -Neurpain - (E.C.Tabs)', 1863, '2020-12-10 10:39:11', '', 0),
(1293, 'SPM0027', '', 'Carton- Diclocort B12-20F.C.Tab', 125600, '2020-12-10 10:39:11', '', 0),
(1294, 'SPM0028', '', 'Leaflets -Diclocort B12 - (F.C.Tabs)', 222030, '2020-12-10 10:39:11', '', 0),
(1295, 'SPM0029', '', 'Carton-Coronasyl-2.5 mg-30F.C.Tabs', 26480, '2020-12-10 10:39:11', '', 0),
(1296, 'SPM0030', '', 'Carton-Coronasyl-5 mg-30F.C.Tabs', 45440, '2020-12-10 10:39:11', '', 0),
(1297, 'SPM0031', '', 'Carton-Coronasyl-10 mg-30F.C.Tabs', 61907, '2020-12-10 10:39:11', '', 0),
(1298, 'SPM0032', '', 'Leaflets -Coronasyl- (F.C-CoatedTabs)', 110553, '2020-12-10 10:39:11', '', 0),
(1299, 'SPM0033', '', 'Box-White-Printed gmp on it -SIZE-42×37×25', 979, '2020-12-10 10:39:11', '', 0),
(1300, 'SPM0034', '', 'Box-White-Printed gmp on it-SIZE-35×40×27', 4117, '2020-12-10 10:39:11', '', 0),
(1301, 'SPM0035', '', 'Carton-Daflogold-30F.C.Tabs', 50702, '2020-12-10 10:39:11', '', 0),
(1302, 'SPM0036', '', 'Leaflets -Daflogpld - (F.C-CoatedTabs)', 56443, '2020-12-10 10:39:11', '', 0),
(1303, 'SPM0037', '', 'Carton-Coronasylplus-5/1.25 mg-30F.C.Tabs', 29776, '2020-12-10 10:39:11', '', 0),
(1304, 'SPM0038', '', 'Carton-Coronasylplus-2.5/0.625 mg-30F.C.Tabs', 45160, '2020-12-10 10:39:11', '', 0),
(1305, 'SPM0039', '', 'Carton-Coronasyl A M-5/5 mg-30F.C.Tabs', 39802, '2020-12-10 10:39:11', '', 0),
(1306, 'SPM0040', '', 'Carton-Coronasyl A M-5/10 mg-30F.C.Tabs', 61870, '2020-12-10 10:39:11', '', 0),
(1307, 'SPM0041', '', 'Carton-Coronasyl A M-10/5 mg-30F.C.Tabs', 22503, '2020-12-10 10:39:11', '', 0),
(1308, 'SPM0042', '', 'Carton-Coronasyl A M-10/10 mg-30F.C.Tabs', 31586, '2020-12-10 10:39:11', '', 0),
(1309, 'SPM0043', '', 'Carton-Busco gold-20F.C.Tabs', 25471, '2020-12-10 10:39:11', '', 0),
(1310, 'SPM0044', '', 'Leaflets -Coronasyl plus - (F.C-Tabs)', 121964, '2020-12-10 10:39:11', '', 0),
(1311, 'SPM0045', '', 'Leaflets -Coronasyl A M - (F.C-Tabs)', 178845, '2020-12-10 10:39:11', '', 0),
(1312, 'SPM0046', '', 'Leaflets -Busco gold plus - (F.C-CoatedTabs)', 80142, '2020-12-10 10:39:11', '', 0),
(1313, 'SPM0047', '', 'Carton-Neurpain-20E.C.Tab-fre medical sample', 3281, '2020-12-10 10:39:11', '', 0),
(1314, 'SPM0048', '', 'Carton-Glucostop-500mg-50 F.C.Tab', 322700, '2020-12-10 10:39:11', '', 0),
(1315, 'SPM0049', '', 'Carton-No Flu-Day-20Caplets', 96525, '2020-12-10 10:39:11', '', 0),
(1316, 'SPM0050', '', 'Carton-No Flu-Night-10Caplets', 99306, '2020-12-10 10:39:11', '', 0),
(1317, 'SPM0051', '', 'Carton-No Flu-Day&Night-30Caplets', 105521, '2020-12-10 10:39:11', '', 0),
(1318, 'SPM0052', '', 'Carton-No Flu HBP-20 F.C.Caplets', 135900, '2020-12-10 10:39:11', '', 0),
(1319, 'SPM0053', '', 'نشرات-نوفلوHBP', 213152, '2020-12-10 10:39:11', '', 0),
(1320, 'SPM0054', '', 'Carton -Sacuval-24/26mg-30F.C.Tab', 22349, '2020-12-10 10:39:11', '', 0),
(1321, 'SPM0055', '', 'Carton -Sacuval-49/51mg-30F.C.Tab', 27108, '2020-12-10 10:39:11', '', 0),
(1322, 'SPM0056', '', 'Carton -Sacuval-97/103mg-30F.C.Tab', 43509, '2020-12-10 10:39:11', '', 0),
(1323, 'SPM0057', '', 'Leaflets-Sacuval-F.C.Tablets', 54801, '2020-12-10 10:39:11', '', 0),
(1324, 'SPM0058', '', 'نشرات-نوفلو-ليلي-نهاري', 183310, '2020-12-10 10:39:11', '', 0),
(1325, 'SPM0059', '', 'Leaflets-Vartan Plus-F.C.TABLETS', 18009, '2020-12-10 10:39:11', '', 0),
(1326, 'SPM0060', '', 'Carton -Vartan Plus-10/160mg-30 F.c.Tab', 25900, '2020-12-10 10:39:11', '', 0),
(1327, 'SPM0061', '', 'Carton -Vartan Plus-10/320mg-30 F.c.Tab', 15850, '2020-12-10 10:39:11', '', 0),
(1328, 'SPM0062', '', 'Carton -Vartan Plus-5/160mg-30 F.c.Tab', 35700, '2020-12-10 10:39:11', '', 0),
(1329, 'SPM0063', '', 'كرتون-فارتانHCT 160', 45355, '2020-12-10 10:39:11', '', 0),
(1330, 'SPM0064', '', 'كرتون-فارتان80 HCT', 45790, '2020-12-10 10:39:11', '', 0),
(1331, 'SPM0065', '', 'كرتون-فارتان-بلس320/5', 15950, '2020-12-10 10:39:11', '', 0),
(1332, 'SPM0066', '', 'Leaflet-Dapagold10/5', 49719, '2020-12-10 10:39:11', '', 0),
(1333, 'SPM0067', '', 'carton-Dapagold-5mg', 29484, '2020-12-10 10:39:11', '', 0),
(1334, 'SPM0068', '', 'Carton-Dapagold-10mg', 84761, '2020-12-10 10:39:11', '', 0),
(1335, 'SPM0069', '', 'Leaflets-Vartan(80-160mg)HCT-F.C.Tab', 45252, '2020-12-10 10:39:11', '', 0),
(1336, 'SPM0071', '', 'كرتون ديكلورت ب 12 نموذج طبي', -130, '2020-12-10 10:39:11', '', 0),
(1337, 'SPM0072', '', 'كرتون سرغافينيك 100 نموذج طبي', 2457, '2020-12-10 10:39:11', '', 0),
(1338, 'SPM0073', '', 'كرتون بليتازول 100', 5898, '2020-12-10 10:39:11', '', 0),
(1339, 'SPM0074', '', 'كرتون بليتازول 50', 15383, '2020-12-10 10:39:11', '', 0),
(1340, 'SPM0075', '', 'كرتون-بنتوفاس-400ملغ', 10942, '2020-12-10 10:39:11', '', 0),
(1341, 'SPM0076', '', 'كرتون-سرغافينيك-100ملغ', 32133, '2020-12-10 10:39:11', '', 0),
(1342, 'SPM0077', '', 'نشرات بنتوفاس 400', 32546, '2020-12-10 10:39:11', '', 0),
(1343, 'SPM0078', '', 'نشرات سيرغافينيك', 38579, '2020-12-10 10:39:11', '', 0),
(1344, 'SPM0079', '', 'نشرات بليتازول', 22540, '2020-12-10 10:39:11', '', 0),
(1345, 'SPM0080', '', 'نشرات انتيكافير', 17764, '2020-12-10 10:39:11', '', 0),
(1346, 'SPM0081', '', 'نشرات هبرو فال', 140651, '2020-12-10 10:39:11', '', 0),
(1347, 'SPM0082', '', 'كرتون هبرو فال 40', 26400, '2020-12-10 10:39:11', '', 0),
(1348, 'SPM0083', '', 'كرتون هيبرو فال 80', 26400, '2020-12-10 10:39:11', '', 0),
(1349, 'SPM0084', '', 'كرتون هيبروفال 160', 24401, '2020-12-10 10:39:11', '', 0),
(1350, 'SPM0085', '', 'Carton-Glumolip 500/50', 6737, '2020-12-10 10:39:11', '', 0),
(1351, 'SPM0086', '', 'carton cholestor 5mg', 8925, '2020-12-10 10:39:11', '', 0),
(1352, 'SPM0087', '', 'carton cholestor 10mg', 2300, '2020-12-10 10:39:11', '', 0),
(1353, 'SPM0088', '', 'carton cgolestorb20mg', 11582, '2020-12-10 10:39:11', '', 0),
(1354, 'SPM0089', '', 'Carton Colestor 40 mg', 6235, '2020-12-10 10:39:11', '', 0),
(1355, 'SPM0090', '', 'نشرات غلوموليب', 82359, '2020-12-10 10:39:11', '', 0),
(1356, 'SPM0091', '', 'carton glumolip 50/1000', 69205, '2020-12-10 10:39:11', '', 0),
(1357, 'SPM0092', '', 'نشرات كوليستر -مضغوطات ملبسة بالغيلبم', 19488, '2020-12-10 10:39:11', '', 0),
(1358, 'SPM0093', '', 'نشرات بروستين - مضغوطات', 30024, '2020-12-10 10:39:11', '', 0),
(1359, 'SPM0094', '', 'كرتون انتيكافير غولدن-1ملغ-30 مضغوطة ملبسة بالفيلم', 9750, '2020-12-10 10:39:11', '', 0),
(1360, 'SPM0095', '', 'Carton prosten 1 mg', 8374, '2020-12-10 10:39:11', '', 0),
(1361, 'SPM0096', '', 'Carton prosten 2 mg', 2782, '2020-12-10 10:39:11', '', 0),
(1362, 'SPM0097', '', 'Carton Prosten 4 mg', 4310, '2020-12-10 10:39:11', '', 0),
(1363, 'SPM0098', '', 'Leaflets-Filamir-F.C.Tab', 4050, '2020-12-10 10:39:11', '', 0),
(1364, 'SPM0099', '', 'Carton-Filamir-400 mg -30 F.C.Tab', 7308, '2020-12-10 10:39:11', '', 0),
(1365, 'SPM0100', '', 'Carton-Filamir-800 mg 30F.C.Tab', 3704, '2020-12-10 10:39:11', '', 0),
(1366, 'SPM0101', '', 'Carton -Nurofen Fast-200mg-10 F.C.Tab', 15987, '2020-12-10 10:39:11', '', 0),
(1367, 'SPM0102', '', 'Leaflets-Nurofen Fast-F.C.Tab', 22175, '2020-12-10 10:39:11', '', 0),
(1368, 'SPM0103', '', 'Carton-Nurofen Fast-400mg-10 F.C.Tab', 21395, '2020-12-10 10:39:11', '', 0),
(1369, 'SPM0104', '', 'Carton-Bone Build -150 mg-3 F.C.Tab', 1050, '2020-12-10 10:39:11', '', 0),
(1370, 'SPM0105', '', 'leafllets-bone build-f.c.tab', 51580, '2020-12-10 10:39:11', '', 0),
(1371, 'SPM0106', '', 'كرتون غولد D3', 18702, '2020-12-10 10:39:11', '', 0),
(1372, 'SPM0107', '', 'نشرات Gold D3', 97955, '2020-12-10 10:39:11', '', 0),
(1373, 'SPM0113', '', 'كرتون انتيكافير غولدن 0.5 ملغ', 1079, '2020-12-10 10:39:11', '', 0),
(1374, 'SPM0114', '', 'كرتون Nouflu Hbpنموذج طبي مجاني', 349, '2020-12-10 10:39:11', '', 0),
(1375, 'SPM0115', '', 'Carton-Dapagold-5mg-sample', -100, '2020-12-10 10:39:11', '', 0),
(1376, 'SPM0116', '', 'Carton-Imodicon', 2950, '2020-12-10 10:39:11', '', 0),
(1377, 'SPM0117', '', 'Leaflet-Imodicon', 3305, '2020-12-10 10:39:11', '', 0),
(1378, 'SPM0118', '', 'Carton-Ironfree-125mg-30Dispersible Tablets', 3315, '2020-12-10 10:39:11', '', 0),
(1379, 'SPM0119', '', 'carton-Ironfree-250mg-30Dispersible Tablets', 2125, '2020-12-10 10:39:11', '', 0),
(1380, 'SPM0120', '', 'Carton-Ironfree-500mg-30Dispersible Tablets', 11146, '2020-12-10 10:39:11', '', 0),
(1381, 'SPM0123', '', 'Carton-Noflu Night-10 Caplets-Free medical sampl', 7415, '2020-12-10 10:39:11', '', 0),
(1382, 'SPM0124', '', 'كرتون -نوفلو نهاري-10 كابليت -نموذج طبي مجاني', 3983, '2020-12-10 10:39:11', '', 0),
(1383, 'SPM0125', '', 'Leaflets-Iron Free-Dispersible Tablets', 23755, '2020-12-10 10:39:11', '', 0),
(1384, 'SPM0127', '', 'Carton -F-Z Gold-20 Cap-Free medical sample', 32, '2020-12-10 10:39:11', '', 0),
(1385, 'SPM0128', '', 'لصاقة هولوغرام', 17593, '2020-12-10 10:39:11', '', 0),
(1386, 'SPM0129', '', 'Carton-Noflu Day & Night-30Caplets for yemen', 21901, '2020-12-10 10:39:11', '', 0),
(1387, 'SPM0130', '', 'Crton-Buscogold plus-20f.c.Tabs-for Yemen', 9969, '2020-12-10 10:39:11', '', 0),
(1388, 'SPM0131', '', 'Carton-Neurpain-20E.C.Tab-For yemen', 11145, '2020-12-10 10:39:11', '', 0),
(1389, 'SPM0132', '', 'Carton-DiclocortB12-20F.C.Tabs-For Yemen', 11286, '2020-12-10 10:39:11', '', 0),
(1390, 'SPM0133', '', 'Carton-Pletazol-50mg-30Tabs-For Yemen', 531, '2020-12-10 10:39:11', '', 0),
(1391, 'SPM0134', '', 'Carton-Pletazol-100mg-30Tabs-For Yemen', 2170, '2020-12-10 10:39:11', '', 0),
(1392, 'SPM0135', '', 'Carton-F-Z-Gold-20Caps-For Yemen', 14685, '2020-12-10 10:39:11', '', 0),
(1393, 'SPM0136', '', 'Carton-Gold D3-5000Iu-30F.C.Tab-Free Medical Sample', 136, '2020-12-10 10:39:11', '', 0),
(1394, 'SPM0137', '', 'Carton-Gold D3-5000 Iu-30 F.C.Tab-For Yemen', 8213, '2020-12-10 10:39:11', '', 0),
(1395, 'SPM0138', '', 'Carton-Finaprost-5mg20.F.C.Tab-For Yamen', 20100, '2020-12-10 10:39:11', '', 0),
(1396, 'SPM0139', '', 'Carton-Dapagold-10mg 30F.C.Tab-For Yemen', 2323, '2020-12-10 10:39:11', '', 0),
(1397, 'SPM0140', '', 'Carton-Dapagold-5mg 30F.C.Tab.For Yemen', 1391, '2020-12-10 10:39:11', '', 0),
(1398, 'SPM0141', '', 'Carton-Entecavire-Golden 0.5mg-30F.C.Tab-For Yemen', 12959, '2020-12-10 10:39:11', '', 0),
(1399, 'SPM0142', '', 'Carton-Pentovas-400mg-M.R.Tab-20Tablets-For-Yemen', 15708, '2020-12-10 10:39:11', '', 0),
(1400, 'SPM0143', '', 'Carton-Noflu-HBP-20-F.C.Caplets For Yemen', 23187, '2020-12-10 10:39:11', '', 0),
(1401, 'SPM0144', '', 'Carton-Nurofen Fast 200mg-10F.C.Tab For Yemen', 20093, '2020-12-10 10:39:11', '', 0),
(1402, 'SPM0145', '', 'Carton-nurofen fast 400 mg-10F.C.Tab Fo yemen', 9270, '2020-12-10 10:39:11', '', 0),
(1403, 'SPM0146', '', 'Carton-Iron Free-125mg-30 Dispersibie For yemen', 919, '2020-12-10 10:39:11', '', 0),
(1404, 'SPM0147', '', 'Carton-Iron Free-250mg-Dispersible For Yemen', 669, '2020-12-10 10:39:11', '', 0),
(1405, 'SPM0148', '', 'Carton-Iron Free-500mg-30Dispersible For yemen', 10653, '2020-12-10 10:39:11', '', 0),
(1406, 'SPM0149', '', 'Carton-Sacuval-24/26mg-30 F.C.Tab For yemen', 929, '2020-12-10 10:39:11', '', 0),
(1407, 'SPM0150', '', 'Carton-Sacuval-49/51mg-30F.C.Tab For yemen', 2059, '2020-12-10 10:39:11', '', 0),
(1408, 'SPM0151', '', 'Carton-Sacuval-97/103mg-30.F.C.Tab For Yemen', 534, '2020-12-10 10:39:11', '', 0),
(1409, 'SPM0152', '', 'Carton-Coronasyl-2.5mg-For Yemen', 85, '2020-12-10 10:39:11', '', 0),
(1410, 'SPM0155', '', 'Carton-Coronasyl Am5/5mg-30F.C.Tab For Yemen', 131, '2020-12-10 10:39:11', '', 0),
(1411, 'SPM0157', '', 'Carton-Coronasyl Am10/5mg-30-F.C.TabsFor yemen', 906, '2020-12-10 10:39:11', '', 0),
(1412, 'SPM0159', '', 'carton coronasyl plus 10/2.5 30.F.C.Tabs', 45575, '2020-12-10 10:39:11', '', 0),
(1413, 'SPM0160', '', 'Carton-Cipro Gold XR-500mg-10F.C.Tab', 6250, '2020-12-10 10:39:11', '', 0),
(1414, 'SPM0161', '', 'Carton Cipro Gold XR-1000mg-10-F.C.Tab', 22053, '2020-12-10 10:39:11', '', 0),
(1415, 'SPM0162', '', 'Leaflets-Ciprogold xr-F.C.Tab', 19762, '2020-12-10 10:39:11', '', 0),
(1416, 'SPM0164', '', 'Carton -Joint Build -120 F.C.Tablets', 23474, '2020-12-10 10:39:11', '', 0),
(1417, 'SPM0165', '', 'Carton -Gold D3-10000 IU 30 F.C.Tab', 349, '2020-12-10 10:39:11', '', 0),
(1418, 'SPM0166', '', 'Carton- Gold D3-20000 IU -30 F.C.Tab', 6105, '2020-12-10 10:39:11', '', 0),
(1419, 'SPM0167', '', 'Carton-Atorvamib-10/10mg-30 F.C.Tab', 27495, '2020-12-10 10:39:11', '', 0),
(1420, 'SPM0168', '', 'Carton-Atorvamib-10/20mg-30 F.C.Tab', 31590, '2020-12-10 10:39:11', '', 0),
(1421, 'SPM0169', '', 'Carton-Atorvamib 10/40mg -30 F.C.Tab', 21864, '2020-12-10 10:39:11', '', 0),
(1422, 'SPM0170', '', 'Carton-Atorvamib 10/80 mg -30 F.C.Tab', 19038, '2020-12-10 10:39:11', '', 0),
(1423, 'SPM0171', '', 'Carton -Bone Aid-30 Caplets', 11100, '2020-12-10 10:39:11', '', 0),
(1424, 'SPM0172', '', 'Label-Amino Acid Golden-300 Caplets', 0, '2020-12-10 10:39:11', '', 0),
(1425, 'SPM0173', '', 'Label-Creatine Golden -250 Capsules', 3500, '2020-12-10 10:39:11', '', 0),
(1426, 'SPM0174', '', 'Label- Glutamine Golden -250 Capsules', 7649, '2020-12-10 10:39:11', '', 0),
(1427, 'SPM0175', '', 'Label-Body Max B C A A -250 Capsules', -400, '2020-12-10 10:39:11', '', 0),
(1428, 'SPM0176', '', 'Carton -Imodicon-10 Tablets-For Yemen', -212, '2020-12-10 10:39:11', '', 0),
(1429, 'SPM0177', '', 'Carton-Denta Gold -20 F.C.Tab For Yemen', 1172, '2020-12-10 10:39:11', '', 0),
(1430, 'SPM0178', '', 'Leaflets-Bone Aid -Caplets', 37820, '2020-12-10 10:39:11', '', 0),
(1431, 'SPM0179', '', 'Carton-Denta Gold Fort-20 F.C.Tab For Yemen', 5, '2020-12-10 10:39:11', '', 0),
(1432, 'SPM0180', '', 'carton-omicarp-20/1100mg-10capsules', 29442, '2020-12-10 10:39:11', '', 0),
(1433, 'SPM0181', '', 'carton-omicarp-40/1100-10capsules', 33901, '2020-12-10 10:39:11', '', 0),
(1434, 'SPM0182', '', 'leaflets-omicarp-capsules', 12537, '2020-12-10 10:39:11', '', 0),
(1435, 'SPM0183', '', 'leaflets-dentagold-dentagold fort-f.c.tab for yemen', 1462, '2020-12-10 10:39:11', '', 0),
(1436, 'SPM0184', '', 'Carton-Platica-60 mg-30 F.C.Tab', 440, '2020-12-10 10:39:11', '', 0),
(1437, 'SPM0185', '', 'Carton-Platica-90mg-30 F.C.Tab', 350, '2020-12-10 10:39:11', '', 0),
(1438, 'SPM0186', '', 'leaflets-atorvamib f.c.tablets', 95520, '2020-12-10 10:39:11', '', 0),
(1439, 'SPM0187', '', 'Carton-Joint Build -90 F.C.Tablets', 13999, '2020-12-10 10:39:11', '', 0),
(1440, 'SPM0188', '', 'leaflets-joint build-f.c.tablets', 41435, '2020-12-10 10:39:11', '', 0),
(1441, 'SPM0189', '', 'Leaflets-Golden B12-Sublingual Tablets', 57000, '2020-12-10 10:39:11', '', 0),
(1442, 'SPM0190', '', 'Carton-Vomset-4mg-10 Orally-Disintegrating Tablets', 64, '2020-12-10 10:39:11', '', 0),
(1443, 'SPM0191', '', 'Carton-Vomset-4mg-20 Orally Disintegrating Tablets', 36261, '2020-12-10 10:39:11', '', 0),
(1444, 'SPM0192', '', 'Carton-Vomset-8mg-10 Orally Disinegrating Tablets', 63, '2020-12-10 10:39:11', '', 0),
(1445, 'SPM0193', '', 'Carton-Vomset-8mg-20 Orally Disintegrating Tablets', 43860, '2020-12-10 10:39:11', '', 0),
(1446, 'SPM0194', '', 'carton-Coronasyl Tri 2.5/0.625/5 mg-30 F.C.Tablets', 23346, '2020-12-10 10:39:11', '', 0),
(1447, 'SPM0195', '', 'Carton-Coronasyl Tri 5/1.25/5 mg -30 F.C.Tablets', 35925, '2020-12-10 10:39:11', '', 0),
(1448, 'SPM0196', '', 'Carton-Coronasyl Tri 5/1.25/10 mg-30 F.C.Tablets', 21787, '2020-12-10 10:39:11', '', 0),
(1449, 'SPM0197', '', 'Carton-Coronasyl Tri 10/2.5/5 mg -30 F.C.Tablets', 24136, '2020-12-10 10:39:11', '', 0),
(1450, 'SPM0198', '', 'Carton-Coronasyl Tri 10/2.5/10 mg -30F.C.Tablets', 31245, '2020-12-10 10:39:11', '', 0),
(1451, 'SPM0199', '', 'lab-joint build-90.f.c.tablets', 13821, '2020-12-10 10:39:11', '', 0),
(1452, 'SPM0200', '', 'lab-joint build-120.f.c.tablets', 22920, '2020-12-10 10:39:11', '', 0),
(1453, 'SPM0201', '', 'Carton-Vaxan-2.5 mg -10 F.C.Tab', 61, '2020-12-10 10:39:11', '', 0),
(1454, 'SPM0202', '', 'Carton-Vaxan-2.5 mg-30F.C.Tab', 11650, '2020-12-10 10:39:11', '', 0),
(1455, 'SPM0203', '', 'Carton-Vaxan-10 mg-10 F.C.Tab', 57, '2020-12-10 10:39:11', '', 0),
(1456, 'SPM0204', '', 'Carton-Vaxan-10 mg-30F.C.Tab', 42406, '2020-12-10 10:39:11', '', 0),
(1457, 'SPM0205', '', 'Carton-Vaxan-15 mg-10 F.C.Tab', 57, '2020-12-10 10:39:11', '', 0),
(1458, 'SPM0206', '', 'Carton-Vaxan-15 mg-30 F.C.Tab', 5750, '2020-12-10 10:39:11', '', 0),
(1459, 'SPM0207', '', 'Carton-Vaxan-20 mg-30F.C.Tab', 488, '2020-12-10 10:39:11', '', 0),
(1460, 'SPM0208', '', 'carton-vomend-40mg-1capsule', 61, '2020-12-10 10:39:11', '', 0),
(1461, 'SPM0209', '', 'carton-vomend-80mg-2capsules', 26900, '2020-12-10 10:39:11', '', 0),
(1462, 'SPM0210', '', 'carton-vomend-125mg-1capsules', 35122, '2020-12-10 10:39:11', '', 0),
(1463, 'SPM0211', '', 'carton-vomend-80/125mg-3capsules', 21525, '2020-12-10 10:39:11', '', 0),
(1464, 'SPM0212', '', 'Leaflets-Coronasyl Tri -(F.C.Tab)', 121882, '2020-12-10 10:39:11', '', 0),
(1465, 'SPM0213', '', 'carton-dapagoldplus 5/850mg-30f.c.tap', 18963, '2020-12-10 10:39:11', '', 0),
(1466, 'SPM0214', '', 'carton-dapagoldplus5/1000mg f.c.tab', 15405, '2020-12-10 10:39:11', '', 0),
(1467, 'SPM0215', '', 'Carton-Vomset 4 mg- Free medical sample', 0, '2020-12-10 10:39:11', '', 0),
(1468, 'SPM0216', '', 'Carton-Maxilans-60mg - 20 D.R.Capsules', 27889, '2020-12-10 10:39:11', '', 0),
(1469, 'SPM0217', '', 'Carton-Maxilans 30 mg - 20 D.R.Capsules', 9796, '2020-12-10 10:39:11', '', 0),
(1470, 'SPM0218', '', 'carton-vomset-8mg-free medical sample', 625, '2020-12-10 10:39:11', '', 0),
(1471, 'SPM0219', '', 'carton-vaxan-10mg 30 f-c-tab-free medical sample', 12934, '2020-12-10 10:39:11', '', 0),
(1472, 'SPM0220', '', 'carton-vaxan-15-mg 30f.c.tab-free medical sample', 19168, '2020-12-10 10:39:11', '', 0),
(1473, 'SPM0221', '', 'leaflats-vaxan-f.c.tab', 93240, '2020-12-10 10:39:11', '', 0),
(1474, 'SPM0222', '', 'leaflets-vomset-orlly-disintegrating tablets', 122550, '2020-12-10 10:39:11', '', 0),
(1476, 'SPM0224', '', 'Leaflets-Maxilans-D.R.Capsules', 42207, '2020-12-10 10:39:11', '', 0),
(1477, 'SPM0225', '', 'Leaflets-Dapagold Plus-F.C.Tab', 36700, '2020-12-10 10:39:11', '', 0),
(1478, 'SPM0226', '', 'carton-target-20mg-30 tablets', 100, '2020-12-10 10:39:11', '', 0),
(1480, 'SPM0228', '', 'carton-target-80mg-30 tablets', 100, '2020-12-10 10:39:11', '', 0),
(1488, 'XXX', 'XXX', 'XXX', 2, '2022-08-09 09:22:40', 'كغ', 3000);

-- --------------------------------------------------------

--
-- Table structure for table `materials_machines`
--

DROP TABLE IF EXISTS `materials_machines`;
CREATE TABLE IF NOT EXISTS `materials_machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `machine_id` int(11) NOT NULL,
  `mode_id` int(11) NOT NULL,
  `usage_duration` double NOT NULL,
  `exclusive` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `machine_id` (`machine_id`),
  KEY `material_id` (`material_id`),
  KEY `mode_id` (`mode_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `materials_machines`
--

INSERT INTO `materials_machines` (`id`, `material_id`, `machine_id`, `mode_id`, `usage_duration`, `exclusive`) VALUES
(2, 1, 1, 1, 5, 0),
(3, 2, 1, 2, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `material_moves`
--

DROP TABLE IF EXISTS `material_moves`;
CREATE TABLE IF NOT EXISTS `material_moves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `source_warehouse_entry_id` int(11) NOT NULL,
  `destination_warehouse_entry_id` int(11) NOT NULL,
  `source_warehouse` int(11) NOT NULL,
  `destination_warehouse` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit` int(11) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `source_warehouse` (`source_warehouse`),
  KEY `destination_warehouse` (`destination_warehouse`),
  KEY `unit` (`unit`),
  KEY `material_id` (`material_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `material_moves`
--

INSERT INTO `material_moves` (`id`, `material_id`, `source_warehouse_entry_id`, `destination_warehouse_entry_id`, `source_warehouse`, `destination_warehouse`, `quantity`, `unit`, `date`) VALUES
(4, 2, 0, 13, 6, 3, 1, 1, '2023-06-14');

-- --------------------------------------------------------

--
-- Table structure for table `mode_resources`
--

DROP TABLE IF EXISTS `mode_resources`;
CREATE TABLE IF NOT EXISTS `mode_resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mode_id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  `consumption_per_minute` double NOT NULL,
  `unit` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mode_id` (`mode_id`,`resource_id`),
  KEY `unit` (`unit`),
  KEY `resource_id` (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `mode_resources`
--

INSERT INTO `mode_resources` (`id`, `mode_id`, `resource_id`, `consumption_per_minute`, `unit`) VALUES
(1, 1, 1, 12, 4),
(5, 1, 2, 54, 5),
(6, 3, 1, 1, 5);

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
CREATE TABLE IF NOT EXISTS `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_id` int(11) DEFAULT NULL,
  `client_id` int(11) NOT NULL,
  `ammount` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `exchange_id` int(11) DEFAULT NULL,
  `equilivance` double NOT NULL,
  `date` date NOT NULL,
  `notes` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `currency_id` (`currency_id`),
  KEY `exchange_id` (`exchange_id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`id`, `invoice_id`, `client_id`, `ammount`, `currency_id`, `exchange_id`, `equilivance`, `date`, `notes`) VALUES
(51, 30, 4, 50, 1, NULL, 50, '2020-01-01', NULL),
(53, 31, 4, 50, 2, NULL, 50, '2020-01-01', NULL),
(56, NULL, 4, 50, 1, NULL, 50, '2020-01-01', NULL),
(57, 30, 4, 200, 2, 4, 100, '2000-01-01', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `payment_conditions`
--

DROP TABLE IF EXISTS `payment_conditions`;
CREATE TABLE IF NOT EXISTS `payment_conditions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_account_id` int(11) NOT NULL,
  `day_number` int(11) NOT NULL,
  `discount_percent` int(11) DEFAULT NULL,
  `discount_value` int(11) DEFAULT NULL,
  `discount_account_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `discount_account_id` (`discount_account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `percent_plans`
--

DROP TABLE IF EXISTS `percent_plans`;
CREATE TABLE IF NOT EXISTS `percent_plans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` int(11) NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '999999',
  `percent` double NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `percent_plans`
--

INSERT INTO `percent_plans` (`id`, `product`, `priority`, `percent`) VALUES
(1, 3, 1, 50),
(2, 4, 2, 25),
(4, 6, 999999, 25);

-- --------------------------------------------------------

--
-- Table structure for table `period_start_materials`
--

DROP TABLE IF EXISTS `period_start_materials`;
CREATE TABLE IF NOT EXISTS `period_start_materials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `quantity1` double NOT NULL,
  `unit1_id` int(11) NOT NULL,
  `quantity2` double NOT NULL,
  `unit2_id` int(11) NOT NULL,
  `quantity3` double NOT NULL,
  `unit3_id` int(11) NOT NULL,
  `unit_price` int(11) NOT NULL,
  `currency` int(11) NOT NULL,
  `warehouse_id` int(11) NOT NULL,
  `notes` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `currency` (`currency`),
  KEY `material_id` (`material_id`),
  KEY `unit1_id` (`unit1_id`),
  KEY `unit3_id` (`unit3_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `period_start_materials_ibfk_5` (`unit2_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `period_start_materials`
--

INSERT INTO `period_start_materials` (`id`, `material_id`, `quantity1`, `unit1_id`, `quantity2`, `unit2_id`, `quantity3`, `unit3_id`, `unit_price`, `currency`, `warehouse_id`, `notes`, `date`) VALUES
(1, 1, 10, 3, 10000, 1, 10000000, 4, 10, 1, 3, NULL, '2000-01-01'),
(2, 1, 10, 3, 10000, 1, 10000000, 4, 10, 1, 3, NULL, '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `plans`
--

DROP TABLE IF EXISTS `plans`;
CREATE TABLE IF NOT EXISTS `plans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` int(11) NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '999999',
  `percent` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10379 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `plans`
--

INSERT INTO `plans` (`id`, `product`, `priority`, `percent`) VALUES
(10369, 3, 1, 0),
(10370, 3, 999999, 0),
(10371, 3, 999999, 0),
(10372, 3, 999999, 0),
(10373, 3, 999999, 0),
(10374, 3, 999999, 0),
(10375, 3, 999999, 0),
(10376, 3, 999999, 0),
(10377, 3, 999999, 0),
(10378, 3, 999999, 0);

-- --------------------------------------------------------

--
-- Table structure for table `prices`
--

DROP TABLE IF EXISTS `prices`;
CREATE TABLE IF NOT EXISTS `prices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `price` varchar(50) NOT NULL,
  `locked` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `price` (`price`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `prices`
--

INSERT INTO `prices` (`id`, `price`, `locked`) VALUES
(1, 'المفرق', 1),
(2, 'الجملة', 1),
(3, 'نصف الجملة', 1),
(4, 'الموزع', 1),
(5, 'التصدير', 1),
(6, 'المستهلك', 1),
(7, 'اخر شراء', 1);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
CREATE TABLE IF NOT EXISTS `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `name_en` varchar(50) DEFAULT NULL,
  `quantity` double NOT NULL,
  `working_hours` double DEFAULT NULL,
  `pills` int(11) DEFAULT NULL,
  `code` varchar(50) DEFAULT NULL,
  `year_require` int(11) DEFAULT '0',
  `in_warehouse` int(11) DEFAULT '0',
  `price` double DEFAULT '0',
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `discount_1` double DEFAULT NULL,
  `discount_2` double DEFAULT NULL,
  `discount_3` double DEFAULT NULL,
  `discount_4` double DEFAULT NULL,
  `exchange` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=96 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `name_en`, `quantity`, `working_hours`, `pills`, `code`, `year_require`, `in_warehouse`, `price`, `date`, `discount_1`, `discount_2`, `discount_3`, `discount_4`, `exchange`) VALUES
(3, 'امينو اسيد غولدن', 'Amino Acid Golden -300 Caplet', 450, 6, 50000, 'FP-Tab01-0062', 6000, 7186, 10000, '2020-12-12 08:45:33', 10, 0, 0, 0, 6),
(4, 'Atorvamib-10/10 mg-30 F.C.Tab', 'اتورفاميب 10/10', 9000, 0, 0, 'FP-Tab01-0070', 12000, 0, 1500, '2020-12-12 08:45:33', 20, 0, 0, 0, 1),
(5, 'Atorvamib-10/20 mg-30 F.C.Tab', '', 6000, 0, 0, 'FP-Tab01-0071', 12000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(6, 'Atorvamib-10/40 mg-30 F.C.Tab', '', 2000, 0, 0, 'FP-Tab01-0072', 6000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(7, 'Atorvamib-10/80 mg-30 F.C.Tab', '', 1250, 0, 0, 'FP-Tab01-0073', 3000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(8, 'Body Max BCAA -250 Cap', '', 734, 0, 0, 'FP- Cap01-0026', 5040, 0, 50, '2020-12-12 08:45:33', 50, 0, 0, 0, 1),
(9, 'Bone Aid-30 Caplet', '', 2002, 0, 0, 'FP-Tab01-0060', 378000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(10, '', 'Buscogold plus - 20 F.C.Tabx', 8600, 20, 0, 'FP-Tab01-0012', 218400, 0, 500, '2020-12-12 08:45:33', 10, 0, 0, 0, 1),
(11, 'Cholestor-10 mg-30 F.C.Tab', '', 0, 0, 0, 'KFP-Tab01-0003', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(12, 'Cholestor-20 mg-30 F.C.Tab', 'كوليستور 20ملغ-30 مضغوطة ملبسة بالفيلم', 0, 0, 0, 'KFP-Tab01-0004', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(13, 'Cholestor-5 mg-30 F.C.Tab', '', 0, 0, 0, 'KFP-Tab01-0002', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(14, 'Ciprogold XR- 1000 mg-10 XR F.C.Tab', '', 7200, 0, 0, 'FP- Tab01-0032', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(15, 'Ciprogold XR- 500 mg-10 XR F.C.Tab', '', 10000, 0, 0, 'FP- Tab01-0031', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(16, 'Coronasyl AM- 5/10 mg-30 Tab', '', 3500, 0, 0, 'FP- Tab01-0034', 8000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(17, 'Coronasyl AM-10/10 mg-30 Tab', '', 2500, 0, 0, 'FP- Tab01-0036', 7000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(93, 'تجربة2', 'test2', 50, 24, 100, 't002', 50000, 25000, 200, '2021-01-23 09:47:23', 0, NULL, NULL, NULL, 1),
(19, 'Coronasyl AM-5/5 mg-30 Tab', '', 12000, 0, 0, 'FP- Tab01-0033', 32000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(20, 'Coronasyl Plus-10 /2.5 mg-30 F C Tab', '', 500, 0, 0, 'FP-Tab01-0076', 6000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(21, 'Coronasyl Plus-2.5 / 0.625 mg-30 F.C Tab', '', 500, 0, 0, 'FP-Tab01-0068', 7000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(22, 'Coronasyl Plus-5 /1.25 mg-30 F.CTab', '', 10000, 0, 0, 'FP-Tab01-0067', 16000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(23, 'Coronasyl Tri - 2.5/0.625/5 mg -30 F.C.Tab', '', 2500, 0, 0, 'FP-Tab01-0094', 4500, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(24, 'Coronasyl Tri - 5/1.25/10 mg-30 F.C.Tab', '', 2500, 0, 0, 'FP-Tab01-0096', 4000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(25, 'Coronasyl Tri - 5/1.25/5 mg-30 F.C.Tab', '', 6000, 0, 0, 'FP-Tab01-0095', 18000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(26, 'Coronasyl Tri -10/2.5/5 mg -30 F.C.Tab', '', 2500, 0, 0, 'FP-Tab01-0097', 6500, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(27, 'Coronasyl Tri-10/2.5/10 mg -30 F.C.Tab', '', 2000, 0, 0, 'FP-Tab01-0098', 5000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(28, 'Coronasyl- 10 mg- 30 F.C.Tab', '', 2000, 0, 0, 'FP-Tab01-0011', 6000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(29, 'Coronasyl- 2.5 mg- 30 F.C.Tab', '', 3000, 0, 0, 'FP-Tab01-0009', 9000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(30, 'Coronasyl- 5 mg- 30 F.C.Tab', '', 5000, 0, 0, 'FP-Tab01-0010', 20000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(31, 'Creatine Golden-250 Cap', '', 580, 0, 0, 'FP- Cap01-0028', 5760, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(32, 'Daflogold-30 F.C Tab', '', 1337, 0, 0, 'FP-Tab01-0015', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(33, 'Dapagold -10 mg-30 F.C.Tabs', '', 15000, 0, 0, 'FP-Tab01-0066', 60000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(34, 'Dapagold -5 mg-30 F.C.Tabs', '', 10000, 0, 0, 'FP-Tab01-0065', 32000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(35, 'Dapagold Plus-5/1000 mg-30 F.C.Tab', '', 2000, 0, 0, 'FP-Tab01-0113', 36000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(36, 'Dapagold Plus-5/850 mg-30 F.C.Tab', '', 3000, 0, 0, 'FP-Tab01-0112', 12000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(37, 'Dentazol Fort- 20 F.C.Tab', '', 593, 0, 0, 'FP-Tab01-0020', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(38, 'Diclocort B12-20 F.C.Tab', '', 30000, 0, 0, 'FP-Tab01-0064', 462000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(39, 'Duogaste -15 mg-20 Cap', '', 10000, 0, 0, 'KFP-Cap01-0007', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(40, 'Duogaste -30 mg-20 Cap', '', 14164, 0, 0, 'KFP-Cap01-0006', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(41, 'Entecavir-Golden-0.5 mg - 30 F.CTabs', '', 6000, 0, 0, 'FP-Tab01-0074', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(42, 'F-Z Gold - 20 Cap', '', 12000, 0, 0, 'FP-Cap01-0005', 126000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(43, 'Filamir-400 mg-30 F.C.Caplets', '', 6000, 0, 0, 'FP-Tab01-0100', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(44, 'Filamir-800 mg-30 F.C.Caplets', '', 3000, 0, 0, 'FP-Tab01-0101', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(45, 'Finaprost- 5 mg-20 F.C.Tab', '', 15000, 0, 0, 'FP-Tab01-0004', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(46, 'Flucozol - 50 mg-10 Cap', '', 5000, 0, 0, 'KFP-Cap01-0018', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(47, 'Flucozol -150 mg-10 Cap', '', 10000, 0, 0, 'KFP-Cap01-0019', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(48, 'Flucozol- 200 mg-10 Cap', '', 12500, 0, 0, 'KFP-Cap01-0017', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(49, 'Gluco Stop Retard-850 mg-30 F.C.Tab', '', 2825, 0, 0, 'KFP-Tab01-0021', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(50, 'Gluco Stop-500 mg-50 Tab', '', 3333, 0, 0, 'KFP-Tab01-0020', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(51, 'Glumolip -50/500 mg-30 F.C.Tab', '', 3333, 0, 0, 'KFP-Tab01-0023', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(52, 'Glumolip-50/1000 mg-30 F.C.Tab', '', 1666, 0, 0, 'KFP-Tab01-0022', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(53, 'Glutamine Golden-250 Cap', '', 620, 0, 0, 'FP- Cap01-0027', 3600, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(54, 'Gold D3-10000 IU -30 F.C.Tab', '', 10000, 0, 0, 'FP-Tab01-0082', 36000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(55, 'Gold D3-20000 IU -30 F.C.Tab', '', 5000, 0, 0, 'FP-Tab01-0083', 10800, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(56, 'Gold D3-5000 IU-30 F.C.Tab', '', 15000, 0, 0, 'FP-Tab01-0022', 72000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(57, 'Heproval -80 mg-30 F.C.Tab', '', 9500, 0, 0, 'FP-Tab01-0054', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(58, 'Imodicon-10 Tab', '', 15000, 0, 0, 'FP-Tab01-0044', 10500, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(59, 'Iron Free-125 mg-30 Dispersible Tab', '', 4500, 0, 0, 'FP-Tab01-0077', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(60, 'Iron Free-250 mg-30 Dispersible Tab', '', 4500, 0, 0, 'FP-Tab01-0078', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(61, 'Iron Free-500 mg-30 Dispersible Tab', '', 4500, 0, 0, 'FP-Tab01-0079', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(62, 'Joint Build -120 F.C.Tablets', '', 17550, 0, 0, 'FP- Tab01-0029', 9600, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(63, 'Joint Build -90 F.C.Tablets', '', 1800, 0, 0, 'FP-Tab02-0106', 9600, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(64, 'Maxilans-30 mg-20 D.R.Cap', '', 15000, 0, 0, 'FP-Cap01-0110', 43200, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(65, 'Maxilans-60 mg-20 D.R. Cap', '', 15000, 0, 0, 'FP-Cap01-0111', 30000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(66, 'Neurpain -20 E.C Tab', '', 7500, 0, 0, 'FP-Tab01-0038', 180000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(67, 'No Flu Day And Night - 30 Caplets', '', 8000, 0, 0, 'FP-Tab01-0050', 120000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(68, 'No Flu HBP -20 F.C Caplets', '', 5000, 0, 0, 'FP-Tab01-0049', 180000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(69, 'Nurofen Fast - 200 mg- 10 F.C Tab', '', 10000, 0, 0, 'FP-Tab01-0013', 9600, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(70, 'Nurofen Fast - 400 mg- 10 F.C Tab', '', 12000, 0, 0, 'FP-Tab01-0014', 43200, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(71, 'Omicarp - 20 mg-10 Cap', '', 10000, 0, 0, 'FP-Cap01-0045', 10500, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(72, 'Omicarp - 40 mg-10 Cap', '', 30000, 0, 0, 'FP-Cap01-0046', 21000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(73, 'Pentovas - 400 mg-20 M.R Tab', '', 3546, 0, 0, 'FP-Tab01-0039', 2400, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(74, 'pletazol - 100 mg-30 Tab', '', 10000, 0, 0, 'FP-Tab01-0048', 10000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(75, 'pletazol - 50 mg-30 Tab', '', 10000, 0, 0, 'FP-Tab01-0047', 10000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(76, 'Prosten- 2 mg-20 Tab', '', 25000, 0, 0, 'KFP-Tab01-0031', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(77, 'Prosten-1 mg-20 Tab', '', 25000, 0, 0, 'KFP-Tab01-0030', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(78, 'Prosten-4 mg-20 Tab', '', 25000, 0, 0, 'KFP-Tab01-0032', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(79, 'Sacuval- 24/26 mg-30F.C.Tab', '', 2400, 0, 0, 'FP-Tab01-0041', 18000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(80, 'Sacuval- 49/51 mg-30 F.C.Tab', '', 1200, 0, 0, 'FP-Tab01-0042', 8000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(81, 'Sacuval- 97/103mg-30F.C.Tab', '', 400, 0, 0, 'FP-Tab01-0043', 1600, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(82, 'Surgafenic- 100 mg- 30 Tab', '', 790, 0, 0, 'FP-Tab01-0021', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(83, 'Vartan-80 mg-30 Cap', '', 0, 0, 0, 'KFP-Cap01-0009', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(84, 'Vaxan-10 mg- 30 F.C.Tab', '', 12000, 0, 0, 'FP-Tab01-0088', 6000, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(87, 'Vaxan-20 mg- 30 F.C.Tab', '', 11500, 0, 0, 'FP-Tab01-0090', 1500, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(88, 'Vomend-40 mg- 1 Cap', '', 1000, 0, 0, 'FP-Cap01-0084', 0, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(90, 'Vomset-4 mg-20 Orally Disintegrating Tablets', '', 6250, 0, 0, 'FP-Tab02-0103', 14400, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(91, 'Vomset-8 mg-20 Orally Disintegrating Tablets', '', 30000, 0, 0, 'FP-Tab02-0105', 50400, 0, 0, '2020-12-12 08:45:33', 0, 0, 0, 0, 1),
(92, 'تتتت', 'ttt', 222, 12, 200, '25', 500, 444, 100, '2021-01-02 17:56:37', 10.5, NULL, NULL, NULL, 1),
(94, 'تجربة_ق', 'test_b', 500, 8, 6, 'test_b', 10000, 0, 250, '2021-07-05 18:35:15', 10, NULL, NULL, NULL, 5);

-- --------------------------------------------------------

--
-- Table structure for table `product_materials`
--

DROP TABLE IF EXISTS `product_materials`;
CREATE TABLE IF NOT EXISTS `product_materials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `mid` int(11) NOT NULL,
  `quantity` double NOT NULL,
  `unit` varchar(11) NOT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `product_materials`
--

INSERT INTO `product_materials` (`id`, `pid`, `mid`, `quantity`, `unit`, `date`) VALUES
(22, 5, 944, 2, 'كغ', '2021-03-06 19:36:42'),
(4, 3, 944, 1, 'كغ', '2020-12-12 09:31:46'),
(23, 3, 946, 50, 'كغ', '2021-03-06 20:36:21'),
(7, 3, 1120, 5.2, 'كغ', '2021-01-23 08:17:35'),
(8, 4, 988, 50, 'كغ', '2021-01-28 07:51:47'),
(9, 9, 944, 1, 'كغ', '2021-02-01 18:43:09'),
(10, 8, 967, 1, 'كغ', '2021-02-03 11:13:36'),
(21, 5, 945, 1, 'كغ', '2021-03-06 19:34:17'),
(24, 94, 1486, 10, 'كغ', '2022-08-09 09:21:58');

-- --------------------------------------------------------

--
-- Table structure for table `research`
--

DROP TABLE IF EXISTS `research`;
CREATE TABLE IF NOT EXISTS `research` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `element` int(11) NOT NULL,
  `quantity` float DEFAULT NULL,
  `unit` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `src` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `research`
--

INSERT INTO `research` (`id`, `element`, `quantity`, `unit`, `src`, `date`) VALUES
(4, 944, 2, 'كغ', 'raws', '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `resources`
--

DROP TABLE IF EXISTS `resources`;
CREATE TABLE IF NOT EXISTS `resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET latin1 NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `notes` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `resources`
--

INSERT INTO `resources` (`id`, `name`, `account_id`, `notes`) VALUES
(1, 'asda', 357, 'sfdfr'),
(2, 'asd', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `resources_costs`
--

DROP TABLE IF EXISTS `resources_costs`;
CREATE TABLE IF NOT EXISTS `resources_costs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resource_id` int(11) NOT NULL,
  `value` double NOT NULL,
  `currency_id` int(11) NOT NULL,
  `unit_id` int(11) NOT NULL,
  `notes` varchar(500) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `currency_id` (`currency_id`),
  KEY `unit_id` (`unit_id`),
  KEY `resources_costs_ibfk_2` (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `resources_costs`
--

INSERT INTO `resources_costs` (`id`, `resource_id`, `value`, `currency_id`, `unit_id`, `notes`, `date`) VALUES
(1, 1, 655, 1, 1, '', '2023-05-15 20:16:54'),
(2, 1, 12, 2, 4, '', '2023-05-16 20:31:47'),
(3, 2, 5, 1, 5, '', '2023-05-16 08:59:37');

-- --------------------------------------------------------

--
-- Table structure for table `sales_targets`
--

DROP TABLE IF EXISTS `sales_targets`;
CREATE TABLE IF NOT EXISTS `sales_targets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `month` int(11) NOT NULL,
  `location` varchar(50) DEFAULT NULL,
  `target` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `sales_targets`
--

INSERT INTO `sales_targets` (`id`, `product`, `year`, `month`, `location`, `target`) VALUES
(5, 3, 2021, 2, 'طرطوس', 10),
(2, 3, 2021, 2, 'حمص', 50),
(6, 3, 2021, 1, 'حمص', 5),
(8, 3, 2021, 3, '', 1),
(10, 3, 2044, 1, '', 20);

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
CREATE TABLE IF NOT EXISTS `settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `value` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=5878 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `name`, `value`) VALUES
(5877, 'default_capital_account', '408'),
(5809, 'output_gifts_opposite_account', NULL),
(5794, 'input_gifts_opposite_account', NULL),
(5779, 'sell_return_gifts_opposite_account', NULL),
(5764, 'buy_return_gifts_opposite_account', NULL),
(5749, 'sell_gifts_opposite_account', NULL),
(5734, 'buy_gifts_opposite_account', '406'),
(5870, 'output_affects_cost_price', NULL),
(5869, 'output_additions_affects_gain', NULL),
(5868, 'output_additions_affects_cost_price', NULL),
(5867, 'output_affects_last_buy_price', NULL),
(5866, 'output_discounts_affects_gain', NULL),
(5865, 'output_discounts_affects_cost_price', NULL),
(5862, 'input_affects_cost_price', NULL),
(5863, 'output_affects_materials_gain_loss', NULL),
(5864, 'output_affects_client_price', NULL),
(5861, 'input_additions_affects_gain', NULL),
(5860, 'input_additions_affects_cost_price', NULL),
(5859, 'input_affects_last_buy_price', NULL),
(5858, 'input_discounts_affects_gain', NULL),
(5857, 'input_discounts_affects_cost_price', NULL),
(5856, 'input_affects_client_price', NULL),
(5855, 'input_affects_materials_gain_loss', NULL),
(5854, 'sell_return_affects_cost_price', NULL),
(5853, 'sell_return_additions_affects_gain', NULL),
(5852, 'sell_return_additions_affects_cost_price', NULL),
(5851, 'sell_return_affects_last_buy_price', NULL),
(5850, 'sell_return_discounts_affects_gain', NULL),
(5849, 'sell_return_discounts_affects_cost_price', NULL),
(5847, 'sell_return_affects_materials_gain_loss', NULL),
(5848, 'sell_return_affects_client_price', NULL),
(5846, 'buy_return_affects_cost_price', NULL),
(5845, 'buy_return_additions_affects_gain', NULL),
(5844, 'buy_return_additions_affects_cost_price', NULL),
(5842, 'buy_return_discounts_affects_gain', NULL),
(5843, 'buy_return_affects_last_buy_price', NULL),
(5841, 'buy_return_discounts_affects_cost_price', NULL),
(5840, 'buy_return_affects_client_price', NULL),
(5839, 'buy_return_affects_materials_gain_loss', NULL),
(5838, 'sell_affects_cost_price', NULL),
(5837, 'sell_additions_affects_gain', NULL),
(5836, 'sell_additions_affects_cost_price', NULL),
(5835, 'sell_affects_last_buy_price', NULL),
(5834, 'sell_discounts_affects_gain', NULL),
(5833, 'sell_discounts_affects_cost_price', NULL),
(5832, 'sell_affects_client_price', NULL),
(5831, 'sell_affects_materials_gain_loss', NULL),
(5830, 'buy_affects_cost_price', NULL),
(5829, 'buy_additions_affects_gain', NULL),
(5828, 'buy_additions_affects_cost_price', NULL),
(5827, 'buy_affects_last_buy_price', NULL),
(5826, 'buy_discounts_affects_gain', NULL),
(5825, 'buy_discounts_affects_cost_price', NULL),
(5824, 'buy_affects_client_price', NULL),
(5823, 'buy_affects_materials_gain_loss', NULL),
(5822, 'output_currency', NULL),
(5820, 'output_warehouse', NULL),
(5821, 'output_cost_center', NULL),
(5819, 'output_gift_price', NULL),
(5818, 'output_cost_price', NULL),
(5817, 'output_invoice_price', NULL),
(5816, 'output_addition_account', NULL),
(5815, 'output_stock_account', NULL),
(5814, 'output_materials_account', NULL),
(5813, 'output_discounts_account', NULL),
(5812, 'output_cost_account', NULL),
(5811, 'output_gifts_account', NULL),
(5810, 'output_monetary_account', NULL),
(5671, 'output_gifts_return_account', NULL),
(5808, 'output_added_value_account', NULL),
(5807, 'input_currency', NULL),
(5806, 'input_cost_center', NULL),
(5805, 'input_warehouse', NULL),
(5804, 'input_gift_price', NULL),
(5803, 'input_cost_price', NULL),
(5802, 'input_invoice_price', NULL),
(5800, 'input_stock_account', NULL),
(5801, 'input_addition_account', NULL),
(5799, 'input_materials_account', NULL),
(5798, 'input_discounts_account', NULL),
(5796, 'input_gifts_account', NULL),
(5797, 'input_cost_account', NULL),
(5795, 'input_monetary_account', NULL),
(5656, 'input_gifts_return_account', NULL),
(5793, 'input_added_value_account', NULL),
(5792, 'sell_return_currency', NULL),
(5791, 'sell_return_cost_center', NULL),
(5790, 'sell_return_warehouse', NULL),
(5789, 'sell_return_gift_price', NULL),
(5788, 'sell_return_cost_price', NULL),
(5787, 'sell_return_invoice_price', NULL),
(5786, 'sell_return_addition_account', NULL),
(5785, 'sell_return_stock_account', NULL),
(5784, 'sell_return_materials_account', NULL),
(5783, 'sell_return_discounts_account', NULL),
(5782, 'sell_return_cost_account', NULL),
(5781, 'sell_return_gifts_account', NULL),
(5780, 'sell_return_monetary_account', NULL),
(5641, 'sell_return_gifts_return_account', NULL),
(5778, 'sell_return_added_value_account', NULL),
(5777, 'buy_return_currency', NULL),
(5776, 'buy_return_cost_center', NULL),
(5775, 'buy_return_warehouse', NULL),
(5774, 'buy_return_gift_price', NULL),
(5773, 'buy_return_cost_price', NULL),
(5772, 'buy_return_invoice_price', NULL),
(5771, 'buy_return_addition_account', NULL),
(5770, 'buy_return_stock_account', NULL),
(5769, 'buy_return_materials_account', NULL),
(5768, 'buy_return_discounts_account', NULL),
(5767, 'buy_return_cost_account', NULL),
(5766, 'buy_return_gifts_account', NULL),
(5765, 'buy_return_monetary_account', NULL),
(5626, 'buy_return_gifts_return_account', NULL),
(5763, 'buy_return_added_value_account', NULL),
(5762, 'sell_currency', NULL),
(5761, 'sell_cost_center', NULL),
(5760, 'sell_warehouse', NULL),
(5759, 'sell_gift_price', NULL),
(5758, 'sell_cost_price', NULL),
(5757, 'sell_invoice_price', NULL),
(5756, 'sell_addition_account', NULL),
(5755, 'sell_stock_account', NULL),
(5754, 'sell_materials_account', NULL),
(5752, 'sell_cost_account', NULL),
(5753, 'sell_discounts_account', NULL),
(5751, 'sell_gifts_account', NULL),
(5750, 'sell_monetary_account', NULL),
(5611, 'sell_gifts_return_account', NULL),
(5748, 'sell_added_value_account', NULL),
(5746, 'buy_cost_center', NULL),
(5747, 'buy_currency', NULL),
(5745, 'buy_warehouse', NULL),
(5742, 'buy_invoice_price', NULL),
(5743, 'buy_cost_price', NULL),
(5744, 'buy_gift_price', NULL),
(5741, 'buy_addition_account', '400'),
(5740, 'buy_stock_account', '404'),
(5739, 'buy_materials_account', '396'),
(5738, 'buy_discounts_account', '398'),
(5737, 'buy_cost_account', '403'),
(5736, 'buy_gifts_account', '405'),
(5735, 'buy_monetary_account', '401'),
(5596, 'buy_gifts_return_account', '406'),
(5733, 'buy_added_value_account', '402'),
(5876, 'operations_fixation', '2000-01-01'),
(5875, 'last_period', '2000-01-01'),
(5874, 'first_period', '2000-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `units`
--

DROP TABLE IF EXISTS `units`;
CREATE TABLE IF NOT EXISTS `units` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `units`
--

INSERT INTO `units` (`id`, `name`) VALUES
(3, 'طن'),
(4, 'غرام'),
(1, 'كغ'),
(5, 'ميجاطن');

-- --------------------------------------------------------

--
-- Table structure for table `units_conversion`
--

DROP TABLE IF EXISTS `units_conversion`;
CREATE TABLE IF NOT EXISTS `units_conversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unit1` int(11) NOT NULL,
  `unit2` int(11) NOT NULL,
  `value` double NOT NULL DEFAULT '1',
  `unit1_ordered` int(11) GENERATED ALWAYS AS (least(`unit1`,`unit2`)) VIRTUAL,
  `unit2_ordered` int(11) GENERATED ALWAYS AS (greatest(`unit2`,`unit1`)) VIRTUAL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unqBi_test` (`unit1_ordered`,`unit2_ordered`),
  KEY `unit1` (`unit1`),
  KEY `unit2` (`unit2`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `units_conversion`
--

INSERT INTO `units_conversion` (`id`, `unit1`, `unit2`, `value`) VALUES
(2, 3, 1, 1000),
(3, 1, 4, 1000),
(4, 3, 4, 1000000),
(5, 5, 3, 1000);

-- --------------------------------------------------------

--
-- Table structure for table `variables`
--

DROP TABLE IF EXISTS `variables`;
CREATE TABLE IF NOT EXISTS `variables` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable` varchar(11) DEFAULT NULL,
  `value` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `variables`
--

INSERT INTO `variables` (`id`, `variable`, `value`) VALUES
(1, 'api_prefix', 'api');

-- --------------------------------------------------------

--
-- Table structure for table `warehouse.a`
--

DROP TABLE IF EXISTS `warehouse.a`;
CREATE TABLE IF NOT EXISTS `warehouse.a` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT '0',
  `unit` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `production_batch_id` int(11) DEFAULT NULL,
  `invoice_item_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `warehouse.a`
--

INSERT INTO `warehouse.a` (`id`, `material_id`, `quantity`, `unit`, `production_batch_id`, `invoice_item_id`) VALUES
(5, 2, 9, '1', NULL, 1),
(9, 3, 10, '1', NULL, 3),
(10, 1, 1, '3', NULL, NULL),
(11, 1, 1, '3', NULL, 48),
(12, 1, 2, '3', NULL, 50);

-- --------------------------------------------------------

--
-- Table structure for table `warehouse.ags`
--

DROP TABLE IF EXISTS `warehouse.ags`;
CREATE TABLE IF NOT EXISTS `warehouse.ags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `material_id` int(11) NOT NULL,
  `quantity` double NOT NULL DEFAULT '0',
  `unit` int(11) DEFAULT NULL,
  `production_batch_id` int(11) DEFAULT NULL,
  `invoice_item_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_index` (`material_id`,`production_batch_id`,`invoice_item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `warehouse.ags`
--

INSERT INTO `warehouse.ags` (`id`, `material_id`, `quantity`, `unit`, `production_batch_id`, `invoice_item_id`) VALUES
(16, 2, 6, 1, NULL, 1),
(17, 2, 1, 3, 120, NULL),
(18, 1, 2, 3, NULL, 56),
(19, 1, 5, 3, NULL, 73);

-- --------------------------------------------------------

--
-- Table structure for table `warehouseslist`
--

DROP TABLE IF EXISTS `warehouseslist`;
CREATE TABLE IF NOT EXISTS `warehouseslist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `codename` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  `parent_warehouse` int(11) DEFAULT NULL,
  `account` int(11) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `manager` varchar(50) DEFAULT NULL,
  `notes` varchar(200) DEFAULT NULL,
  `capacity` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_warehouse` (`parent_warehouse`),
  KEY `account` (`account`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `warehouseslist`
--

INSERT INTO `warehouseslist` (`id`, `code`, `name`, `codename`, `date`, `parent_warehouse`, `account`, `address`, `manager`, `notes`, `capacity`) VALUES
(3, 'dss', 'asd', 'warehouse.ags', '2022-09-28 18:50:30', NULL, 408, NULL, NULL, NULL, NULL),
(6, 'a', 'a', 'warehouse.a', '2022-09-28 18:56:39', 3, 408, NULL, '33', NULL, NULL);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`parent_account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`final_account`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `cost_centers`
--
ALTER TABLE `cost_centers`
  ADD CONSTRAINT `cost_centers_ibfk_1` FOREIGN KEY (`parent`) REFERENCES `cost_centers` (`id`);

--
-- Constraints for table `cost_centers_aggregations_distributives`
--
ALTER TABLE `cost_centers_aggregations_distributives`
  ADD CONSTRAINT `cost_centers_aggregations_distributives_ibfk_1` FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`);

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`expense_type_id`) REFERENCES `expenses_types` (`id`);

--
-- Constraints for table `expenses_types`
--
ALTER TABLE `expenses_types`
  ADD CONSTRAINT `expenses_types_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `expenses_types_ibfk_2` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `groupped_materials_composition`
--
ALTER TABLE `groupped_materials_composition`
  ADD CONSTRAINT `groupped_materials_composition_ibfk_1` FOREIGN KEY (`composition_material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `groupped_materials_composition_ibfk_2` FOREIGN KEY (`groupped_material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `groupped_materials_composition_ibfk_3` FOREIGN KEY (`unit`) REFERENCES `units` (`id`);

--
-- Constraints for table `hr_additional_costs`
--
ALTER TABLE `hr_additional_costs`
  ADD CONSTRAINT `hr_additional_costs_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_additional_costs_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_additional_costs_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_additional_costs_ibfk_4` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`);

--
-- Constraints for table `hr_courses`
--
ALTER TABLE `hr_courses`
  ADD CONSTRAINT `hr_courses_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_courses_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_courses_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `hr_course_employees`
--
ALTER TABLE `hr_course_employees`
  ADD CONSTRAINT `hr_course_employees_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `hr_courses` (`id`),
  ADD CONSTRAINT `hr_course_employees_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_departments`
--
ALTER TABLE `hr_departments`
  ADD CONSTRAINT `hr_departments_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_departments_ibfk_2` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `hr_departments_finance`
--
ALTER TABLE `hr_departments_finance`
  ADD CONSTRAINT `hr_departments_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_departments_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_departments_finance_ibfk_3` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`),
  ADD CONSTRAINT `hr_departments_finance_ibfk_4` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `hr_departments_leaves`
--
ALTER TABLE `hr_departments_leaves`
  ADD CONSTRAINT `hr_departments_leaves_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`);

--
-- Constraints for table `hr_employees`
--
ALTER TABLE `hr_employees`
  ADD CONSTRAINT `hr_employees_ibfk_1` FOREIGN KEY (`employment_request_id`) REFERENCES `hr_employment_requests` (`id`);

--
-- Constraints for table `hr_employees_certificates`
--
ALTER TABLE `hr_employees_certificates`
  ADD CONSTRAINT `hr_employees_certificates_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_employees_salaries_additions_discounts`
--
ALTER TABLE `hr_employees_salaries_additions_discounts`
  ADD CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_employees_salaries_additions_discounts_payments`
--
ALTER TABLE `hr_employees_salaries_additions_discounts_payments`
  ADD CONSTRAINT `hr_employees_salaries_additions_discounts_payments_ibfk_1` FOREIGN KEY (`salaries_additions_discounts`) REFERENCES `hr_employees_salaries_additions_discounts` (`id`);

--
-- Constraints for table `hr_employees_transfers`
--
ALTER TABLE `hr_employees_transfers`
  ADD CONSTRAINT `hr_employees_transfers_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_employees_transfers_ibfk_2` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`),
  ADD CONSTRAINT `hr_employees_transfers_ibfk_3` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`);

--
-- Constraints for table `hr_employee_received_items`
--
ALTER TABLE `hr_employee_received_items`
  ADD CONSTRAINT `hr_employee_received_items_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `hr_employee_received_items_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `hr_employee_received_items_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `hr_employee_received_items_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_employment_request_certificates`
--
ALTER TABLE `hr_employment_request_certificates`
  ADD CONSTRAINT `hr_employment_request_certificates_ibfk_1` FOREIGN KEY (`employment_request_id`) REFERENCES `hr_employment_requests` (`id`);

--
-- Constraints for table `hr_extra`
--
ALTER TABLE `hr_extra`
  ADD CONSTRAINT `hr_extra_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_extra_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_extra_ibfk_3` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`),
  ADD CONSTRAINT `hr_extra_ibfk_4` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_extra_ibfk_5` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `hr_finance`
--
ALTER TABLE `hr_finance`
  ADD CONSTRAINT `hr_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_finance_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_finance_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_insurance_block_entries`
--
ALTER TABLE `hr_insurance_block_entries`
  ADD CONSTRAINT `hr_insurance_block_entries_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_insurance_block_entries_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_insurance_block_entries_ibfk_3` FOREIGN KEY (`insurance_block_id`) REFERENCES `hr_insurance_blocks` (`id`);

--
-- Constraints for table `hr_leaves`
--
ALTER TABLE `hr_leaves`
  ADD CONSTRAINT `hr_leaves_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_leaves_ibfk_2` FOREIGN KEY (`alternative_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_leaves_ibfk_3` FOREIGN KEY (`leave_type_id`) REFERENCES `hr_leave_types` (`id`);

--
-- Constraints for table `hr_loans`
--
ALTER TABLE `hr_loans`
  ADD CONSTRAINT `hr_loans_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_loans_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_loans_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_loans_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`);

--
-- Constraints for table `hr_loans_payment`
--
ALTER TABLE `hr_loans_payment`
  ADD CONSTRAINT `hr_loans_payment_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `hr_loans` (`id`),
  ADD CONSTRAINT `hr_loans_payment_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`);

--
-- Constraints for table `hr_positions_finance`
--
ALTER TABLE `hr_positions_finance`
  ADD CONSTRAINT `hr_positions_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_positions_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `hr_positions_finance_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `hr_positions_finance_ibfk_4` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`);

--
-- Constraints for table `hr_positions_leaves`
--
ALTER TABLE `hr_positions_leaves`
  ADD CONSTRAINT `hr_positions_leaves_ibfk_1` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`);

--
-- Constraints for table `hr_salary_blocks`
--
ALTER TABLE `hr_salary_blocks`
  ADD CONSTRAINT `hr_salary_blocks_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `hr_salary_block_entries`
--
ALTER TABLE `hr_salary_block_entries`
  ADD CONSTRAINT `hr_salary_block_entries_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_salary_block_entries_ibfk_2` FOREIGN KEY (`salary_block_id`) REFERENCES `hr_salary_blocks` (`id`),
  ADD CONSTRAINT `hr_salary_block_entries_ibfk_3` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`),
  ADD CONSTRAINT `hr_salary_block_entries_ibfk_4` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`);

--
-- Constraints for table `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`client`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_10` FOREIGN KEY (`monetary_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_11` FOREIGN KEY (`materials_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_12` FOREIGN KEY (`stock_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_13` FOREIGN KEY (`gifts_opposite_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`client_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_3` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_5` FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_6` FOREIGN KEY (`warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_7` FOREIGN KEY (`cost_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_8` FOREIGN KEY (`gifts_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_ibfk_9` FOREIGN KEY (`added_value_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `invoices_discounts_additions`
--
ALTER TABLE `invoices_discounts_additions`
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_1` FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_4` FOREIGN KEY (`exchange`) REFERENCES `exchange_prices` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_5` FOREIGN KEY (`opposite_account`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_6` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `invoices_discounts_additions_ibfk_7` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`);

--
-- Constraints for table `invoice_items`
--
ALTER TABLE `invoice_items`
  ADD CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`cost_center_id`) REFERENCES `cost_centers` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_3` FOREIGN KEY (`exchange_id`) REFERENCES `exchange_prices` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_4` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_5` FOREIGN KEY (`price_type_id`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_6` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_7` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_8` FOREIGN KEY (`item_discount_account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `invoice_items_ibfk_9` FOREIGN KEY (`item_addition_account`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `journal_entries`
--
ALTER TABLE `journal_entries`
  ADD CONSTRAINT `journal_entries_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`);

--
-- Constraints for table `journal_entries_items`
--
ALTER TABLE `journal_entries_items`
  ADD CONSTRAINT `journal_entries_items_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `journal_entries_items_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `journal_entries_items_ibfk_3` FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `journal_entries_items_ibfk_4` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `journal_entries_items_ibfk_5` FOREIGN KEY (`cost_center_id`) REFERENCES `cost_centers` (`id`);

--
-- Constraints for table `journal_entries_items_distributive_cost_center_values`
--
ALTER TABLE `journal_entries_items_distributive_cost_center_values`
  ADD CONSTRAINT `journal_entries_items_distributive_cost_center_values_ibfk_1` FOREIGN KEY (`cost_centers_aggregations_distributives_id`) REFERENCES `cost_centers_aggregations_distributives` (`id`),
  ADD CONSTRAINT `journal_entries_items_distributive_cost_center_values_ibfk_2` FOREIGN KEY (`journal_entry_item_id`) REFERENCES `journal_entries_items` (`id`);

--
-- Constraints for table `machines`
--
ALTER TABLE `machines`
  ADD CONSTRAINT `machines_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`),
  ADD CONSTRAINT `machines_ibfk_2` FOREIGN KEY (`estimated_waste_account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `machines_ibfk_3` FOREIGN KEY (`estimated_waste_currency`) REFERENCES `currencies` (`id`);

--
-- Constraints for table `machine_modes`
--
ALTER TABLE `machine_modes`
  ADD CONSTRAINT `machine_modes_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE;

--
-- Constraints for table `manufacture`
--
ALTER TABLE `manufacture`
  ADD CONSTRAINT `manufacture_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_2` FOREIGN KEY (`unit1`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_3` FOREIGN KEY (`unit2`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_4` FOREIGN KEY (`unit3`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_5` FOREIGN KEY (`warehouse`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_6` FOREIGN KEY (`mid_account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_7` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_8` FOREIGN KEY (`quantity_unit_expenses`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `manufacture_ibfk_9` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`);

--
-- Constraints for table `manufacture_halls`
--
ALTER TABLE `manufacture_halls`
  ADD CONSTRAINT `manufacture_halls_ibfk_1` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`);

--
-- Constraints for table `manufacture_machines`
--
ALTER TABLE `manufacture_machines`
  ADD CONSTRAINT `manufacture_machines_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`),
  ADD CONSTRAINT `manufacture_machines_ibfk_2` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`),
  ADD CONSTRAINT `manufacture_machines_ibfk_3` FOREIGN KEY (`manufacture_id`) REFERENCES `manufacture` (`id`);

--
-- Constraints for table `manufacture_materials`
--
ALTER TABLE `manufacture_materials`
  ADD CONSTRAINT `manufacture_materials_ibfk_1` FOREIGN KEY (`manufacture_id`) REFERENCES `manufacture` (`id`),
  ADD CONSTRAINT `manufacture_materials_ibfk_2` FOREIGN KEY (`composition_item_id`) REFERENCES `groupped_materials_composition` (`id`),
  ADD CONSTRAINT `manufacture_materials_ibfk_3` FOREIGN KEY (`unit`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `manufacture_materials_ibfk_4` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `manufacture_materials_ibfk_5` FOREIGN KEY (`warehouse_account_id`) REFERENCES `accounts` (`id`),
  ADD CONSTRAINT `manufacture_materials_ibfk_6` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`);

--
-- Constraints for table `manufacture_pullout_requests`
--
ALTER TABLE `manufacture_pullout_requests`
  ADD CONSTRAINT `manufacture_pullout_requests_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`);

--
-- Constraints for table `materials`
--
ALTER TABLE `materials`
  ADD CONSTRAINT `materials_ibfk_1` FOREIGN KEY (`price1_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_10` FOREIGN KEY (`group`) REFERENCES `groups` (`id`),
  ADD CONSTRAINT `materials_ibfk_11` FOREIGN KEY (`manufacture_hall`) REFERENCES `manufacture_halls` (`id`),
  ADD CONSTRAINT `materials_ibfk_2` FOREIGN KEY (`price2_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_3` FOREIGN KEY (`price3_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_4` FOREIGN KEY (`price4_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_5` FOREIGN KEY (`price5_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_6` FOREIGN KEY (`price6_desc`) REFERENCES `prices` (`id`),
  ADD CONSTRAINT `materials_ibfk_7` FOREIGN KEY (`unit1`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `materials_ibfk_8` FOREIGN KEY (`unit2`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `materials_ibfk_9` FOREIGN KEY (`unit3`) REFERENCES `units` (`id`);

--
-- Constraints for table `materials_machines`
--
ALTER TABLE `materials_machines`
  ADD CONSTRAINT `materials_machines_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`),
  ADD CONSTRAINT `materials_machines_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `materials_machines_ibfk_3` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`);

--
-- Constraints for table `material_moves`
--
ALTER TABLE `material_moves`
  ADD CONSTRAINT `material_moves_ibfk_1` FOREIGN KEY (`source_warehouse`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `material_moves_ibfk_2` FOREIGN KEY (`destination_warehouse`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `material_moves_ibfk_3` FOREIGN KEY (`unit`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `material_moves_ibfk_4` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`);

--
-- Constraints for table `mode_resources`
--
ALTER TABLE `mode_resources`
  ADD CONSTRAINT `mode_resources_ibfk_1` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `mode_resources_ibfk_2` FOREIGN KEY (`unit`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `mode_resources_ibfk_3` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`);

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`exchange_id`) REFERENCES `exchange_prices` (`id`),
  ADD CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  ADD CONSTRAINT `payments_ibfk_4` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);

--
-- Constraints for table `payment_conditions`
--
ALTER TABLE `payment_conditions`
  ADD CONSTRAINT `payment_conditions_ibfk_1` FOREIGN KEY (`discount_account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `period_start_materials`
--
ALTER TABLE `period_start_materials`
  ADD CONSTRAINT `period_start_materials_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `period_start_materials_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`),
  ADD CONSTRAINT `period_start_materials_ibfk_4` FOREIGN KEY (`unit1_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `period_start_materials_ibfk_5` FOREIGN KEY (`unit2_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `period_start_materials_ibfk_6` FOREIGN KEY (`unit3_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `period_start_materials_ibfk_8` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`);

--
-- Constraints for table `resources`
--
ALTER TABLE `resources`
  ADD CONSTRAINT `resources_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`);

--
-- Constraints for table `resources_costs`
--
ALTER TABLE `resources_costs`
  ADD CONSTRAINT `resources_costs_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`),
  ADD CONSTRAINT `resources_costs_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `resources_costs_ibfk_3` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `units_conversion`
--
ALTER TABLE `units_conversion`
  ADD CONSTRAINT `units_conversion_ibfk_1` FOREIGN KEY (`unit1`) REFERENCES `units` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `units_conversion_ibfk_2` FOREIGN KEY (`unit2`) REFERENCES `units` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `warehouseslist`
--
ALTER TABLE `warehouseslist`
  ADD CONSTRAINT `warehouseslist_ibfk_1` FOREIGN KEY (`parent_warehouse`) REFERENCES `warehouseslist` (`id`),
  ADD CONSTRAINT `warehouseslist_ibfk_2` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
