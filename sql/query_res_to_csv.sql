SELECT *
FROM records
INTO OUTFILE '~/Upload'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';