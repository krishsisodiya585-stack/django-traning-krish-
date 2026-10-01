import pymysql
from django.conf import settings


def mirror_issue_to_mysql(issue):
	connection = pymysql.connect(**settings.LIBRARY_MYSQL_CONFIG)
	try:
		with connection.cursor() as cursor:
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS library_book_issue (
					id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
					local_issue_id BIGINT DEFAULT NULL UNIQUE,
					book_id VARCHAR(30) NOT NULL,
					book_name VARCHAR(160) NOT NULL,
					book_number VARCHAR(30) NOT NULL,
					student_name VARCHAR(120) NOT NULL,
					issue_date DATE NOT NULL,
					due_date DATE NOT NULL,
					issued_by VARCHAR(150) NOT NULL,
					created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
					KEY library_issue_user_date (issued_by, issue_date)
				) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
			''')
			cursor.execute('''
				INSERT INTO library_book_issue (
					local_issue_id, book_id, book_name, book_number, student_name,
					issue_date, due_date, issued_by
				) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE
					book_id = VALUES(book_id),
					book_name = VALUES(book_name),
					book_number = VALUES(book_number),
					student_name = VALUES(student_name),
					issue_date = VALUES(issue_date),
					due_date = VALUES(due_date),
					issued_by = VALUES(issued_by)
			''', (
				issue.pk,
				issue.book_id,
				issue.book_name,
				issue.book_number,
				issue.student_name,
				issue.issue_date,
				issue.due_date,
				issue.issued_by.get_username(),
			))
		connection.commit()
	finally:
		connection.close()