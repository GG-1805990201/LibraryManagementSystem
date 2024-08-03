from config.sqlite_config import get_db_connection
from dao.book_dao_queries import BookDaoQueries
from dao.loan_dao_queries import LoanDaoQueries
from datetime import datetime, timedelta

class LoanService:

    FINE_RATE = 30  # Fine of 30 rupees per day for overdue books

    @staticmethod
    def create_loan(data):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the book is available
        cursor.execute(BookDaoQueries.get_available_copies(), (data['book_id'],))
        book = cursor.fetchone()

        if book and book['available_copies'] > 0:
            # Reduce available copies by 1
            cursor.execute(BookDaoQueries.update_available_copies_when_loaned(), (data['book_id'],))

            # Set return_date to 15 days after loan_date
            loan_date = datetime.strptime(data['loan_date'], '%Y-%m-%d')
            return_date = loan_date + timedelta(days=15)

            # Create loan record
            cursor.execute(LoanDaoQueries.insert_new_loan(), (data['book_id'], data['member_id'],
                                                              data['loan_date'], return_date.strftime('%Y-%m-%d')))
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

        # Calculate fines for overdue loans
        loans_with_fines = []
        for loan in loans:
            loan_dict = dict(loan)
            loan_dict['fine'] = LoanService.calculate_fine(loan_dict['return_date'], loan_dict.get('actual_return_date'))
            loans_with_fines.append(loan_dict)

        return loans_with_fines

    @staticmethod
    def get_loan(loan_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_loan_by_id(), (loan_id,))
        loan = cursor.fetchone()
        conn.close()

        if loan:
            loan_dict = dict(loan)
            loan_dict['fine'] = LoanService.calculate_fine(loan_dict['return_date'], loan_dict.get('actual_return_date'))
            return loan_dict
        else:
            return None

    @staticmethod
    def update_loan(loan_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(LoanDaoQueries.get_loan_by_id(), (loan_id,))
        loan = cursor.fetchone()

        if loan:
            # Validate return_date is after loan_date
            if 'actual_return_date' in data and data['actual_return_date']:
                actual_return_date = datetime.strptime(data['actual_return_date'], '%Y-%m-%d')
                loan_date = datetime.strptime(loan['loan_date'], '%Y-%m-%d')
                return_date = datetime.strptime(loan['return_date'], '%Y-%m-%d')

                if actual_return_date < loan_date:
                    conn.close()
                    return {"message": "Actual return date must be after loan date"}, 400

                # Calculate fine for the overdue book
                fine = LoanService.calculate_fine(return_date.strftime('%Y-%m-%d'), data['actual_return_date'])

                # Update loan record with actual return date and fine
                cursor.execute(LoanDaoQueries.update_loan_by_id(), (data.get('actual_return_date'), fine, loan_id))
                # Increment available copies by 1 if book is being returned
                cursor.execute(BookDaoQueries.update_available_copies_when_returned(), (loan['book_id'],))

            else:
                # If actual return date is not provided, just update other details
                cursor.execute(LoanDaoQueries.update_loan_by_id(), (data.get('return_date'), 0 ,loan_id))

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

    @staticmethod
    def calculate_fine(return_date, actual_return_date):
        """Calculate fine based on overdue days."""
        if not actual_return_date:
            return 0

        return_date = datetime.strptime(return_date, '%Y-%m-%d')
        actual_return_date = datetime.strptime(actual_return_date, '%Y-%m-%d')

        if actual_return_date > return_date:
            overdue_days = (actual_return_date - return_date).days
            return overdue_days * LoanService.FINE_RATE  # Fine is 30 rupees per overdue day

        return 0
