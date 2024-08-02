from config.sqlite_config import get_db_connection
from dao.book_dao_queries import BookDaoQueries
from dao.loan_dao_queries import LoanDaoQueries
from datetime import datetime


class LoanService:

    @staticmethod
    def create_loan(data):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the book is available
        cursor.execute(BookDaoQueries.get_available_copies(), (data['book_id'],))
        book = cursor.fetchone()

        if book and book['available_copies'] > 0:
            # Reduce available copies by 1
            cursor.execute(BookDaoQueries.update_available_copies(), (data['book_id'],))

            # Create loan record
            cursor.execute(LoanDaoQueries.insert_new_loan(), (data['book_id'], data['member_id'],
                                                              data['loan_date']))
            conn.commit()
            loan_id = cursor.lastrowid
            conn.close()
            return {"message": "Loan created successfully", "loan_id": loan_id}, 201
        else:
            conn.close()
            return {"message": "Book not available"}, 400

    @staticmethod
    def get_loans():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_all_loans())
        loans = cursor.fetchall()
        conn.close()
        return [dict(loan) for loan in loans]

    @staticmethod
    def get_loan(loan_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_loan_by_id(), (loan_id,))
        loan = cursor.fetchone()
        conn.close()
        return dict(loan) if loan else None

    @staticmethod
    def update_loan(loan_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_loan_by_id(), (loan_id,))
        loan = cursor.fetchone()

        if loan:
            # Validate return_date is after loan_date
            if 'return_date' in data and data['return_date']:
                return_date = datetime.strptime(data['return_date'], '%Y-%m-%d')
                loan_date = datetime.strptime(loan['loan_date'], '%Y-%m-%d')

                if return_date <= loan_date:
                    conn.close()
                    return {"message": "Return date must be after loan date"}, 400

                # Increment available copies by 1 if book is being returned
                cursor.execute(BookDaoQueries.update_available_copies_when_returned(), (loan['book_id'],))

            # Update loan record
            cursor.execute(LoanDaoQueries.update_loan_by_id(), (data.get('return_date'), loan_id))
            conn.commit()
            conn.close()
            return {"message": "Loan updated successfully"}, 200
        else:
            conn.close()
            return {"message": "Loan not found"}, 404

    @staticmethod
    def delete_loan(loan_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_loan_by_id(), (loan_id,))
        loan = cursor.fetchone()

        if loan:
            # Increment available copies by 1 if the loan is being deleted and the book hasn't been returned
            if not loan['return_date']:
                cursor.execute(BookDaoQueries.update_available_copies_when_returned(), (loan['book_id'],))

            cursor.execute(LoanDaoQueries.delete_loan_by_id(), (loan_id,))
            conn.commit()
            conn.close()
            return {"message": "Loan deleted successfully"}, 200
        else:
            conn.close()
            return {"message": "Loan not found"}, 404


