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
        return {"message": "Book created successfully", "book_id": book_id}

    @staticmethod
    def get_books(author=None, published_start=None, published_end=None, page=1, limit=10, search=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build the SQL query dynamically based on filters and search
        query = BookDaoQueries.get_all_books()
        params = []

        if author:
            query += " WHERE author = ?"
            params.append(author)

        if published_start:
            if 'WHERE' in query:
                query += " AND published_date >= ?"
            else:
                query += " WHERE published_date >= ?"
            params.append(published_start)

        if published_end:
            if 'WHERE' in query:
                query += " AND published_date <= ?"
            else:
                query += " WHERE published_date <= ?"
            params.append(published_end)

        # Add search functionality
        if search:
            search_query = f"%{search}%"
            if 'WHERE' in query:
                query += " AND (title LIKE ? OR author LIKE ?)"
            else:
                query += " WHERE (title LIKE ? OR author LIKE ?)"
            params.extend([search_query, search_query])

        # Add pagination
        query += " ORDER BY published_date ASC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])

        # Execute the query
        cursor.execute(query, params)
        books = cursor.fetchall()

        # Get the total number of books matching the filters and search (without pagination)
        total_query = "SELECT COUNT(*) FROM (" + query.replace(" ORDER BY published_date ASC LIMIT ? OFFSET ?", "") + ")"
        cursor.execute(total_query, params[:-2])  # Remove pagination params for count
        total = cursor.fetchone()[0]

        conn.close()
        return [dict(book) for book in books], total

    @staticmethod
    def get_book(book_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.get_book_by_id(), (book_id,))
        book = cursor.fetchone()
        conn.close()
        return dict(book) if book else None

    @staticmethod
    def update_book(book_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.update_book_by_id(), (data['title'], data['author'], data['published_date'],
                                                            data['isbn'], data['number_of_pages'], data['cover_image'],
                                                            data['language'], data['available_copies'], book_id))
        conn.commit()
        conn.close()
        return {"message": "Book updated successfully"}

    @staticmethod
    def delete_book(book_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(BookDaoQueries.delete_book_by_id(), (book_id,))
        conn.commit()
        conn.close()
        return {"message": "Book deleted successfully"}
