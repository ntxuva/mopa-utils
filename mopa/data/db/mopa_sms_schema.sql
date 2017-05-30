DROP TABLE IF EXISTS `mopa_sms`;
CREATE TABLE `mopa_sms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `direction` varchar(1) DEFAULT NULL,
  `sent_by` varchar(255) DEFAULT NULL,
  `sent_to` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `mopa_survey`;
CREATE TABLE `mopa_survey` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `survey_id` varchar(255) DEFAULT NULL,
  `survey_type` varchar(1) DEFAULT NULL,
  `district` varchar(255) DEFAULT NULL,
  `neighbourhood` varchar(255) DEFAULT NULL,
  `point` varchar(255) DEFAULT NULL,
  `question` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `mopa_survey_answers`;
CREATE TABLE `mopa_survey_answers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `survey_key` int(11) DEFAULT NULL,
  `survey_id` varchar(255) DEFAULT NULL,
  `answer` varchar(255) DEFAULT NULL,
  `answered_at` datetime DEFAULT NULL,
  `answered_by` varchar(255) DEFAULT NULL,
  `answer_sms_id` int(11) DEFAULT NULL,
  `neighbourhood` varchar(255) DEFAULT NULL,
  `quarter` varchar(255) DEFAULT NULL,
  `point` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `survey_key` (`survey_key`),
  KEY `answer_sms_id` (`answer_sms_id`),
  CONSTRAINT `mopa_survey_answers_ibfk_1` FOREIGN KEY (`survey_key`) REFERENCES `mopa_survey` (`id`),
  CONSTRAINT `mopa_survey_answers_ibfk_2` FOREIGN KEY (`answer_sms_id`) REFERENCES `mopa_sms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
