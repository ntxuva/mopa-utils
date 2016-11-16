CREATE TABLE ntxuva_sms(
	id INT AUTOINCREMENT, -- a unique ID for the row
	neighborhood VARCHAR(255), -- The neighborhood name contained in JSON neighborhood config file(name field), Ex. Maxaquene A
	quarter VARCHAR(255), -- The quarter name contained in JSON neighborhood config file (name field), Ex. Quarteirao 39
	question_id INT -- The question id contained in JSON messages config file
	question VARCHAR(255), -- The question text contained in JSON messages config file
	sent_at DATETIME, -- The date the SMS was sent
	survey_id INT, -- Each question should have a unique identifier per week or day basis, so we'll increment and reset the count programmatically and populate it here
	answer VARCHAR(255), -- The answer to the question
	answered_at DATETIME -- The date and time at which the answer was received
);