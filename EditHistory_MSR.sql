CREATE TABLE IF NOT EXISTS EditHistory_MSR (
	PostId INTEGER NOT NULL,
	ParentId INTEGER,
	PostTypeId INTEGER NOT NULL,
	EventId INTEGER NOT NULL,
	Event TEXT NOT NULL,
	UserName TEXT NOT NULL,
	CreationDate TEXT NOT NULL,
	Tags TEXT,
	Score INTEGER,
	Text TEXT
);

INSERT INTO EditHistory_MSR(PostId, ParentId, PostTypeId, EventId, Event, UserName, CreationDate, Tags, Score, Text) 
SELECT eh.PostId, 
eh.ParentId, 
eh.PostTypeId, 
eh.EventId, 
eh.Event, 
eh.UserName, 
eh.CreationDate, 
eh.Tags, 
eh.Score, 
GROUP_CONCAT(pbv.Content, '') AS Text 
FROM PostBlockVersion pbv 
JOIN EditHistory eh ON eh.EventId = pbv.PostHistoryId 
WHERE eh.PostTypeId = 2 
AND pbv.PostBlockTypeId = 2 
AND eh.Event = 'InitialBody' 
GROUP BY eh.EventId;

INSERT INTO EditHistory_MSR(PostId, ParentId, PostTypeId, EventId, Event, UserName, CreationDate, Tags, Score, Text) 
SELECT eh.PostId, 
eh.ParentId, 
eh.PostTypeId, 
eh.EventId, 
eh.Event, 
eh.UserName, 
eh.CreationDate, 
eh.Tags, 
eh.Score, 
'' AS Text
FROM EditHistory eh
WHERE PostId NOT IN (
SELECT eh.PostId
FROM PostBlockVersion pbv 
JOIN EditHistory eh ON eh.EventId = pbv.PostHistoryId 
WHERE eh.PostTypeId = 2 
AND pbv.PostBlockTypeId = 2 
AND eh.Event = 'InitialBody' 
GROUP BY eh.EventId
) AND Event = 'InitialBody';

INSERT INTO EditHistory_MSR(PostId, ParentId, PostTypeId, EventId, Event, UserName, CreationDate, Tags, Score, Text) 
SELECT *
FROM EditHistory eh
WHERE eh.PostTypeId = 2 
AND eh.Event = 'Comment';

INSERT INTO EditHistory_MSR(PostId, ParentId, PostTypeId, EventId, Event, UserName, CreationDate, Tags, Score, Text) 
SELECT eh.PostId, 
eh.ParentId, 
eh.PostTypeId, 
eh.EventId, 
eh.Event, 
eh.UserName, 
eh.CreationDate, 
eh.Tags, 
eh.Score, 
GROUP_CONCAT(pbv.Content, '') AS Text 
FROM PostBlockVersion pbv JOIN EditHistory eh ON eh.EventId = pbv.PostHistoryId 
WHERE eh.PostTypeId = 2 
AND pbv.PostBlockTypeId = 2 
AND eh.Event = 'BodyEdit'
GROUP BY eh.EventId;
