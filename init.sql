CREATE TABLE blog (
  id        INT AUTO_INCREMENT,
  title     TEXT,
  content   TEXT,
  posted_on DATETIME,
  PRIMARY KEY (id)
);

DROP TABLE url;
CREATE TABLE url (
  id        INT AUTO_INCREMENT,
  url     TEXT,
  uid     TEXT,
  posted_on DATETIME,
  status  TEXT,
  PRIMARY KEY (id)
);