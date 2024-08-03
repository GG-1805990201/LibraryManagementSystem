
CREATE TABLE IF NOT EXISTS Members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL ,
    email TEXT NOT NULL,
    join_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    published_date DATE NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    number_of_pages INTEGER NOT NULL,
    cover_image TEXT,
    language TEXT NOT NULL,
    available_copies INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Loan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE,
    fine INTEGER DEFAULT 0,
    actual_return_date DATE,
    FOREIGN KEY (book_id) REFERENCES Book(id),
    FOREIGN KEY (member_id) REFERENCES Member(id)
);

CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    role TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Member(id)
);


