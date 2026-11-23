-- ============================================================
-- 拼音战机 · 数据库初始化脚本
-- 数据库: pinyin_war_game  |  MySQL 8.0  |  字符集 utf8mb4
-- 执行方式: mysql -u root -p < sql/init_db.sql
-- ============================================================

-- 1. 创建数据库（已存在则跳过，不覆盖数据）
CREATE DATABASE IF NOT EXISTS pinyin_war_game
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE pinyin_war_game;

-- 2. 用户表：存储账号信息，密码字段只存哈希值，绝不存明文
CREATE TABLE IF NOT EXISTS users (
  user_id     INT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键自增',
  username    VARCHAR(32)    NOT NULL                COMMENT '用户名，唯一',
  password_hash VARCHAR(255) NOT NULL                COMMENT '密码哈希（bcrypt），禁止明文',
  create_time DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  PRIMARY KEY (user_id),
  UNIQUE KEY  uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 3. 成绩表：每个(用户,难度)一条记录，同一玩家玩过多个难度就有多条，
--    因此在排行榜三个难度组里都能看到同一玩家。每条记录各自维护"该难度最近一局"与"该难度历史最高"。
CREATE TABLE IF NOT EXISTS game_records (
  record_id     INT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '记录ID，主键自增',
  user_id       INT UNSIGNED   NOT NULL                COMMENT '用户ID，外键关联 users.user_id',
  total_score   INT UNSIGNED   NOT NULL DEFAULT 0      COMMENT '该难度最近一局得分（每次覆盖）',
  difficulty    VARCHAR(10)    NOT NULL DEFAULT 'easy' COMMENT '难度(easy/normal/hard)，与 user_id 组成唯一键',
  best_score    INT UNSIGNED   NOT NULL DEFAULT 0      COMMENT '该难度历史最高分（只升不降）',
  best_difficulty VARCHAR(10)  NOT NULL DEFAULT 'easy' COMMENT '兼容字段，恒等于本行 difficulty',
  correct_rate  DECIMAL(5,2)   NOT NULL DEFAULT 0.00   COMMENT '最近一局正确率(百分比，如 92.50)',
  play_duration INT UNSIGNED   NOT NULL DEFAULT 0      COMMENT '最近一局游玩时长(秒)',
  play_time     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最近一局发生时间',
  PRIMARY KEY (record_id),
  UNIQUE KEY uk_user_difficulty (user_id, difficulty),
  CONSTRAINT fk_records_user FOREIGN KEY (user_id)
    REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩表（每人每难度一条：该难度最近得分 + 该难度最高分）';
