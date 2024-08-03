class LoanDaoQueries:
    @staticmethod
    def insert_new_loan():
        return "INSERT INTO Loan (book_id, member_id, loan_date,return_date) VALUES (?, ?, ?,?)"

    @staticmethod
    def get_all_loans():
        return "SELECT * FROM Loan"

    @staticmethod
    def get_loan_by_id():
        return "SELECT * FROM Loan WHERE id = ?"

    @staticmethod
    def update_loan_by_id():
        return "UPDATE Loan SET actual_return_date = ?, fine = ? WHERE id = ?"


    @staticmethod
    def delete_loan_by_id():
        return "DELETE FROM Loan WHERE id = ?"

