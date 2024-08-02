from flask import url_for
from config.sqlite_config import get_db_connection
from dao.book_dao_queries import BookDaoQueries


class BookService:
    @staticmethod
    def create_book(data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.insert_new_book(), (data['title'], data['author'], data['published_date'],
                                                          data['isbn'], data['number_of_pages'], data['cover_image'],
                                                          data['language'], data['available_copies']))
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()

        # Add HATEOAS links
        response = {
            "message": "Book added successfully",
            "book_id": book_id,
            "_links": {
                "self": url_for('books.get_book', book_id=book_id, _external=True),
                "update": url_for('books.update_book', book_id=book_id, _external=True),
                "delete": url_for('books.delete_book', book_id=book_id, _external=True),
                "list": url_for('books.get_books', _external=True)
            }
        }
        return response

    @staticmethod
    def get_books():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.get_all_books())
        books = cursor.fetchall()
        conn.close()

        # Add HATEOAS links to each book
        books_with_links = []
        for book in books:
            book_dict = dict(book)
            book_dict["_links"] = {
                "self": url_for('books.get_book', book_id=book['id'], _external=True),
                "update": url_for('books.update_book', book_id=book['id'], _external=True),
                "delete": url_for('books.delete_book', book_id=book['id'], _external=True)
            }
            books_with_links.append(book_dict)

        # Add a link to create a new book
        links = {"create": url_for('books.create_book', _external=True)}

        return {"books": books_with_links, "_links": links}

    @staticmethod
    def get_book(book_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.get_book_by_id(), (book_id,))
        book = cursor.fetchone()
        conn.close()

        if book:
            # Add HATEOAS links
            book_dict = dict(book)
            book_dict["_links"] = {
                "self": url_for('books.get_book', book_id=book_id, _external=True),
                "update": url_for('books.update_book', book_id=book_id, _external=True),
                "delete": url_for('books.delete_book', book_id=book_id, _external=True),
                "list": url_for('books.get_books', _external=True)
            }
            return book_dict
        else:
            return None

    @staticmethod
    def update_book(book_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.update_book_by_id(), (data['title'], data['author'], data['published_date'],
                                                            data['isbn'], data['number_of_pages'], data['cover_image'],
                                                            data['language'], data['available_copies'], book_id))
        conn.commit()
        conn.close()

        # Add HATEOAS links
        response = {
            "message": "Book updated successfully",
            "_links": {
                "self": url_for('books.get_book', book_id=book_id, _external=True),
                "delete": url_for('books.delete_book', book_id=book_id, _external=True),
                "list": url_for('books.get_books', _external=True)
            }
        }
        return response

    @staticmethod
    def delete_book(book_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.delete_book_by_id(), (book_id,))
        conn.commit()
        conn.close()

        # Add HATEOAS link to list books
        response = {
            "message": "Book deleted successfully",
            "_links": {
                "list": url_for('books.get_books', _external=True)
            }
        }
        return response
