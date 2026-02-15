-- ============================================================
-- 001_extensions.sql — 启用必要的 PostgreSQL 扩展
-- 执行顺序: 第 1 步 (在建表之前)
-- ============================================================

-- pgvector: 向量嵌入存储与相似度检索
CREATE EXTENSION IF NOT EXISTS vector;

-- uuid-ossp: UUID 生成函数 (uuid_generate_v4)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
