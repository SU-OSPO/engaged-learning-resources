-- Teaching Activities Platform - PostgreSQL Schema

-- material type enum
CREATE TYPE material_type_enum AS ENUM (
    'worksheet',
    'instructions',
    'example',
    'video'
);

-- category
CREATE TABLE category (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- activity
CREATE TABLE activity (
    id              BIGSERIAL PRIMARY KEY,
    category_id     BIGINT REFERENCES category(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_title ON activity(title);
CREATE INDEX idx_activity_category_id ON activity(category_id);

-- tag
CREATE TABLE tag (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE
);

CREATE INDEX idx_tag_name ON tag(name);

-- activity_tag (join table)
CREATE TABLE activity_tag (
    id              BIGSERIAL PRIMARY KEY,
    activity_id     BIGINT NOT NULL REFERENCES activity(id) ON DELETE CASCADE,
    tag_id          BIGINT NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, tag_id)
);

CREATE INDEX idx_activity_tag_activity_id ON activity_tag(activity_id);
CREATE INDEX idx_activity_tag_tag_id ON activity_tag(tag_id);

-- material
CREATE TABLE material (
    id              BIGSERIAL PRIMARY KEY,
    activity_id     BIGINT NOT NULL REFERENCES activity(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    file_path       VARCHAR(500) NOT NULL,
    material_type   material_type_enum NOT NULL,
    uploaded_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_activity_id ON material(activity_id);
CREATE INDEX idx_material_type ON material(material_type);

-- updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_category_updated_at
    BEFORE UPDATE ON category
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_activity_updated_at
    BEFORE UPDATE ON activity
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
