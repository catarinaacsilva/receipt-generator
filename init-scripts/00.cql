CREATE KEYSPACE IF NOT EXISTS dht
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };