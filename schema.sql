--create table if the table is not exist in the database
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    title TEXT,
    firstName TEXT ,
    lastName TEXT,
    picture TEXT
);

--create post table if not exist
CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        userId TEXT,
        image TEXT,
        likes INTEGER,
        body TEXT,
        tags, TEXT,
        publishDate DATE,
        FOREIGN KEY (userId) REFERENCES users(id)
);