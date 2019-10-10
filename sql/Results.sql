CREATE TABLE Results (
	QuestionId INTEGER,
	AnswerId INTEGER,
	CommentId INTEGER,
	QuestionAuthor TEXT,
	AnswerAuthor TEXT,
	CommentAuthor TEXT,
	AnswerScore INTEGER,
	Tags TEXT,
	CommentIndex INTEGER,
	CommentDate NUM,
	CommentScore INTEGER,
	Comment TEXT,
	CommentGroups TEXT,
	HasEditsAfter BOOLEAN,
	EditGroups TEXT,
	EditId INTEGER,
	EditAuthor TEXT,
	EditDate NUM,
	EditsAuthor INTEGER,
	EditsOthers INTEGER,
	CommentMentions TEXT
);
CREATE INDEX ResultsAnswerIdIndex ON Results(AnswerId);
