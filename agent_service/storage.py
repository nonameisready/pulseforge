import os, sqlite3
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
SQLITE_PATH = os.environ.get("SQLITE_PATH", "data/pulseforge.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  created_at TEXT,
  tenant TEXT,
  channel TEXT,
  objective TEXT,
  product_name TEXT,
  audience TEXT,
  constraints_json TEXT
);
CREATE TABLE IF NOT EXISTS variants (
  id TEXT PRIMARY KEY,
  campaign_id TEXT,
  created_at TEXT,
  headline TEXT,
  primary_text TEXT,
  cta TEXT,
  angle_tag TEXT,
  score REAL,
  notes TEXT,
  raw_json TEXT,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);
"""

def connect():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    con = sqlite3.connect(SQLITE_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.executescript(SCHEMA)
    return con

def insert_campaign(campaign: Dict[str, Any]):
    con = connect()
    with con:
        con.execute(
            """INSERT INTO campaigns (id, created_at, tenant, channel, objective, product_name, audience, constraints_json)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                campaign["id"], campaign["created_at"], campaign.get("tenant","default"),
                campaign.get("channel","ads"), campaign.get("objective","conversion"),
                campaign.get("product_name",""), campaign.get("audience",""),
                campaign.get("constraints_json","{}"),
            ),
        )
    con.close()

def insert_variants(campaign_id: str, variants: List[Dict[str, Any]]):
    con = connect()
    with con:
        for v in variants:
            con.execute(
                """INSERT INTO variants (id, campaign_id, created_at, headline, primary_text, cta, angle_tag, score, notes, raw_json)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    v["id"], campaign_id, v["created_at"], v.get("headline",""),
                    v.get("primary_text",""), v.get("cta",""), v.get("angle_tag",""),
                    float(v.get("score", 0.0)), v.get("notes",""), v.get("raw_json","{}")
                ),
            )
    con.close()

def get_recent_variants(campaign_id: str, limit: int = 10):
    con = connect()
    cur = con.cursor()
    cur.execute(
        """SELECT headline, primary_text, cta, angle_tag, score, notes, created_at
             FROM variants WHERE campaign_id = ? ORDER BY created_at DESC LIMIT ?""",
        (campaign_id, limit)
    )
    rows = cur.fetchall()
    con.close()
    return rows
