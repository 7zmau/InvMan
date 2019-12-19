DROP TABLE IF EXISTS business;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS movement;
DROP TABLE IF EXISTS warehouse;

CREATE TABLE business (
  business_id TEXT PRIMARY KEY NOT NULL,
  business_name TEXT
);

CREATE TABLE product (
  product_id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  quantity INTEGER UNSIGNED NOT NULL,
  for_business TEXT NOT NULL,
  FOREIGN KEY (for_business) REFERENCES business (business_id)
);

CREATE TABLE location (
  location_id TEXT PRIMARY KEY,
  location_name TEXT NOT NULL,
  for_business TEXT NOT NULL,
  FOREIGN KEY (for_business) REFERENCES business (business_id)
);

CREATE TABLE warehouse (
  b_id TEXT NOT NULL,
  prod_id TEXT NOT NULL,
  qty INTEGER,
  loc_id TEXT NOT NULL,
  FOREIGN KEY (b_id) REFERENCES business (business_id),
  FOREIGN KEY (loc_id) REFERENCES location (location_id),
  FOREIGN KEY (prod_id) REFERENCES product (product_id)
);

CREATE TABLE movement (
  movement_id TEXT NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
  from_location TEXT,
  to_location TEXT,
  prod_id TEXT NOT NULL,
  qty INTEGER,
  b_id TEXT NOT NULL,
  FOREIGN KEY (prod_id) REFERENCES product (product_id),
  FOREIGN KEY (from_location) REFERENCES location (location_id),
  FOREIGN KEY (to_location) REFERENCES location (location_id),
  FOREIGN KEY (b_id) REFERENCES business (business_id)
);
