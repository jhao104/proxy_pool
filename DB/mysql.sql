/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 50720
 Source Host           : localhost:3306
 Source Schema         : proxy

 Target Server Type    : MySQL
 Target Server Version : 50720
 File Encoding         : 65001

 Date: 31/07/2018 21:34:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for raw_proxy
-- ----------------------------
DROP TABLE IF EXISTS `raw_proxy`;
CREATE TABLE `raw_proxy`  (
  `proxy` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`proxy`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for useful_proxy
-- ----------------------------
DROP TABLE IF EXISTS `useful_proxy`;
CREATE TABLE `useful_proxy`  (
  `proxy` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`proxy`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
