-- MySQL dump 10.13  Distrib 5.6.24, for osx10.9 (x86_64)
--
-- Host: localhost    Database: mopa_sms
-- ------------------------------------------------------
-- Server version	5.6.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mopa_sms`
--

DROP TABLE IF EXISTS `mopa_sms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mopa_sms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `direction` varchar(1) DEFAULT NULL,
  `sent_by` varchar(255) DEFAULT NULL,
  `sent_to` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mopa_sms`
--

LOCK TABLES `mopa_sms` WRITE;
/*!40000 ALTER TABLE `mopa_sms` DISABLE KEYS */;
INSERT INTO `mopa_sms` VALUES (1,'2015-08-13 13:01:02','2015-08-13 13:01:02','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(2,'2015-08-13 13:01:02','2015-08-13 13:01:02','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(3,'2015-08-13 13:01:02','2015-08-13 13:01:02','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(4,'2015-08-13 13:01:02','2015-08-13 13:01:02','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(5,'2015-08-13 13:01:04','2015-08-13 13:01:04','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(6,'2015-08-13 13:01:04','2015-08-13 13:01:04','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(7,'2015-08-13 13:01:05','2015-08-13 13:01:05','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(8,'2015-08-13 13:01:05','2015-08-13 13:01:05','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(9,'2015-08-13 13:01:05','2015-08-13 13:01:05','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(10,'2015-08-13 13:01:05','2015-08-13 13:01:05','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(11,'2015-08-13 13:01:06','2015-08-13 13:01:06','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(12,'2015-08-13 13:01:06','2015-08-13 13:01:06','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(13,'2015-08-13 13:01:07','2015-08-13 13:01:07','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(14,'2015-08-13 13:01:07','2015-08-13 13:01:07','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(15,'2015-08-13 13:01:08','2015-08-13 13:01:08','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(16,'2015-08-13 13:01:08','2015-08-13 13:01:08','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(17,'2015-08-13 13:01:09','2015-08-13 13:01:09','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(18,'2015-08-13 13:01:09','2015-08-13 13:01:09','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(19,'2015-08-13 13:01:10','2015-08-13 13:01:10','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(20,'2015-08-13 13:01:10','2015-08-13 13:01:10','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(21,'2015-08-13 13:01:10','2015-08-13 13:01:10','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(22,'2015-08-13 13:01:11','2015-08-13 13:01:11','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(23,'2015-08-13 13:01:11','2015-08-13 13:01:11','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(24,'2015-08-13 13:01:12','2015-08-13 13:01:12','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(25,'2015-08-13 13:01:12','2015-08-13 13:01:12','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(26,'2015-08-13 13:01:13','2015-08-13 13:01:13','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(27,'2015-08-13 13:01:13','2015-08-13 13:01:13','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(28,'2015-08-13 13:01:13','2015-08-13 13:01:13','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(29,'2015-08-13 13:01:13','2015-08-13 13:01:13','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(30,'2015-08-13 13:01:14','2015-08-13 13:01:14','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(31,'2015-08-13 13:01:14','2015-08-13 13:01:14','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(32,'2015-08-13 13:01:15','2015-08-13 13:01:15','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(33,'2015-08-13 13:01:16','2015-08-13 13:01:16','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(34,'2015-08-13 13:01:17','2015-08-13 13:01:17','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(35,'2015-08-13 13:01:18','2015-08-13 13:01:18','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(36,'2015-08-13 13:01:18','2015-08-13 13:01:18','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(37,'2015-08-13 13:01:19','2015-08-13 13:01:19','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(38,'2015-08-13 13:01:19','2015-08-13 13:01:19','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(39,'2015-08-13 13:01:20','2015-08-13 13:01:20','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(40,'2015-08-13 13:01:20','2015-08-13 13:01:20','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(41,'2015-08-13 13:01:20','2015-08-13 13:01:20','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(42,'2015-08-13 13:01:20','2015-08-13 13:01:20','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(43,'2015-08-13 13:01:21','2015-08-13 13:01:21','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(44,'2015-08-13 13:01:21','2015-08-13 13:01:21','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(45,'2015-08-13 13:01:22','2015-08-13 13:01:22','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(46,'2015-08-13 13:01:22','2015-08-13 13:01:22','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(47,'2015-08-13 13:01:23','2015-08-13 13:01:23','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(48,'2015-08-13 13:01:23','2015-08-13 13:01:23','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(49,'2015-08-13 13:01:24','2015-08-13 13:01:24','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(50,'2015-08-13 13:01:24','2015-08-13 13:01:24','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(51,'2015-08-13 13:01:25','2015-08-13 13:01:25','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(52,'2015-08-13 13:01:25','2015-08-13 13:01:25','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(53,'2015-08-13 13:01:25','2015-08-13 13:01:25','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(54,'2015-08-13 13:01:26','2015-08-13 13:01:26','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(55,'2015-08-13 13:01:26','2015-08-13 13:01:26','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(56,'2015-08-13 13:01:28','2015-08-13 13:01:28','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(57,'2015-08-13 13:01:28','2015-08-13 13:01:28','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(58,'2015-08-13 13:01:29','2015-08-13 13:01:29','O','Mopa','821847184','MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(59,'2015-08-13 13:01:35','2015-08-13 13:01:35','I','821847184','Mopa','s'),(60,'2015-08-13 13:07:08','2015-08-13 13:07:08','O','Mopa','848504509','Lamentamos nao ter recebido o seu contributo, se o tiver enviado, por favor entre em contacto com a Livaningo, caso contrario pode envia-lo agora.'),(61,'2015-08-13 15:46:49','2015-08-13 15:46:49','O','Mopa','821847184','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F responda 3| s ou n'),(62,'2015-08-13 15:52:28','2015-08-13 15:52:28','O','Mopa','821847184','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F responda 4| s ou n'),(63,'2015-08-13 16:01:29','2015-08-13 16:01:29','O','Mopa','821847184','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F responda 5| s ou n'),(64,'2015-08-13 16:02:36','2015-08-13 16:02:36','O','Mopa','821847184','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F responda 6| s ou n'),(65,'2015-08-13 16:03:14','2015-08-13 16:03:14','O','Mopa','821847184','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F responda 7| s ou n'),(66,'2015-08-13 16:31:50','2015-08-13 16:31:50','I','821847184','Mopa','7|n'),(67,'2015-08-13 16:32:55','2015-08-13 16:32:55','I','821847184','Mopa','7|n'),(68,'2015-08-13 16:33:25','2015-08-13 16:33:25','I','821847184','Mopa','7|n'),(69,'2015-08-13 16:40:19','2015-08-13 16:40:19','I','848504509','Mopa','n');
/*!40000 ALTER TABLE `mopa_sms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mopa_survey`
--

DROP TABLE IF EXISTS `mopa_survey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mopa_survey`
--

LOCK TABLES `mopa_survey` WRITE;
/*!40000 ALTER TABLE `mopa_survey` DISABLE KEYS */;
INSERT INTO `mopa_survey` VALUES (1,'2015-08-13 13:01:00','2015-08-13 13:01:00','1','G',NULL,NULL,NULL,'MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(2,'2015-08-13 13:01:00','2015-08-13 13:01:00','2','G',NULL,NULL,NULL,'MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao.'),(3,'2015-08-13 15:46:48','2015-08-13 15:46:48','3','I','1','Maxaquene A','Contentor do Baltazar','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F'),(4,'2015-08-13 15:52:27','2015-08-13 15:52:27','4','I','1','Polana Canico B','Lixeira Informal, Mercado de Xiquelene','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F'),(5,'2015-08-13 16:01:24','2015-08-13 16:01:24','5','I','1','Polana Canico B','Lixeira Informal, Mercado de Xiquelene','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F'),(6,'2015-08-13 16:02:36','2015-08-13 16:02:36','6','I','1','Polana Canico B','Lixeira Informal, Mercado de Xiquelene','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F'),(7,'2015-08-13 16:03:13','2015-08-13 16:03:13','7','I','1','Polana Canico B','Lixeira Informal, Mercado de Xiquelene','O%20contentor%20esta%20cheio%20no%20teu%20quarteirao%3F');
/*!40000 ALTER TABLE `mopa_survey` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mopa_survey_answers`
--

DROP TABLE IF EXISTS `mopa_survey_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mopa_survey_answers`
--

LOCK TABLES `mopa_survey_answers` WRITE;
/*!40000 ALTER TABLE `mopa_survey_answers` DISABLE KEYS */;
INSERT INTO `mopa_survey_answers` VALUES (1,'2015-08-13 13:01:35','2015-08-13 13:01:35',1,'1','s','2015-08-13 11:01:35','821847184',59,NULL,NULL,NULL),(2,'2015-08-13 16:32:55','2015-08-13 16:32:55',7,'7','n','2015-08-13 14:32:56','821847184',67,NULL,NULL,NULL),(3,'2015-08-13 16:33:25','2015-08-13 16:33:25',7,'7','n','2015-08-13 14:33:26','821847184',68,NULL,NULL,NULL),(4,'2015-08-13 16:40:19','2015-08-13 16:40:19',1,'1','n','2015-08-13 14:40:19','848504509',69,NULL,NULL,NULL);
/*!40000 ALTER TABLE `mopa_survey_answers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-08-14 14:10:46
