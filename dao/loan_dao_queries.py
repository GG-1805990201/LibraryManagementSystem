class LoanDaoQueries:
    @staticmethod
    def insert_new_loan():
        return "INSERT INTO Loans (book_id, user_id, issue_date) VALUES (?, ?, ?)"

    @staticmethod
    def get_all_loans():
        return "SELECT * FROM Loans"

    @staticmethod
    def get_loan_by_id():
        return "SELECT * FROM Loans WHERE id = ?"

    @staticmethod
    def update_loan_by_id():
        return "UPDATE Loans SET return_date = ? WHERE id = ?"

    @staticmethod
    def delete_loan_by_id():
        return "DELETE FROM Loans WHERE id = ?"

