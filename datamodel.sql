CREATE TABLE campaigns (
  id TEXT PRIMARY KEY,
  tenant TEXT,
  channel TEXT,
  objective TEXT,
  audience TEXT,
  product_name TEXT,
  product_desc TEXT,
  brand_voice TEXT,
  created_at TIMESTAMPTZ
);

CREATE TABLE variants (
  id TEXT PRIMARY KEY,
  campaign_id TEXT REFERENCES campaigns(id),
  headline TEXT,
  primary_text TEXT,
  cta TEXT,
  angle_tag TEXT,
  score FLOAT,
  notes TEXT,
  raw_json JSONB,
  created_at TIMESTAMPTZ
);
