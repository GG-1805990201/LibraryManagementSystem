class BookDaoQueries:
    @staticmethod
    def get_all_books():
        return "SELECT * FROM Books"

    @staticmethod
    def get_book_by_id():
        return "SELECT * FROM Books WHERE id = ?"

    @staticmethod
    def insert_new_book():
        return "INSERT INTO Books (title, author, published_date, isbn, " \
               "number_of_pages, cover_image, language, available_copies) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    @staticmethod
    def update_book_by_id():
        return "UPDATE Books SET title = ?, author = ?, published_date = ?, isbn = ?, number_of_pages = ?, " \
               "cover_image = ?, language = ?, available_copies = ? WHERE id = ?"

    @staticmethod
    def delete_book_by_id():
        return "DELETE FROM Books WHERE id = ?"

    @staticmethod
    def get_available_copies():
        return "SELECT available_copies FROM Books WHERE id = ?"

    @staticmethod
    def update_available_copies_when_loaned():
        return "UPDATE Books SET available_copies = available_copies - 1 WHERE id = ?"

    @staticmethod
    def update_available_copies_when_returned():
        return "UPDATE Books SET available_copies = available_copies + 1 WHERE id = ?"
