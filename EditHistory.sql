CREATE TABLE EditHistory AS
SELECT *
FROM (
	SELECT
	  pv.PostId AS PostId,
	  pv.PostTypeId AS PostTypeId,
	  PostHistoryId AS EventId,
	  CASE
		WHEN pv.PostHistoryTypeId=2 THEN "InitialBody"
		ELSE "BodyEdit"
	  END AS Event,
	  u.DisplayName AS UserName,
	  pv.CreationDate AS CreationDate,
	  ph.Text AS Text
	FROM PostVersion pv
	JOIN PostHistory ph ON pv.PostHistoryId = ph.Id
	JOIN Users u ON ph.UserId = u.Id
	UNION ALL
	SELECT
	  tv.PostId AS PostId,
	  tv.PostTypeId AS PostTypeId,
	  PostHistoryId AS EventId,
	  CASE
		WHEN tv.PostHistoryTypeId=1 THEN "InitialTitle"
		ELSE "TitleEdit"
	  END AS Event,
	  u.DisplayName AS UserName,
	  tv.CreationDate AS CreationDate,
	  ph.Text AS Text
	FROM TitleVersion tv
	JOIN PostHistory ph ON tv.PostHistoryId = ph.Id
	JOIN Users u ON ph.UserId = u.Id
	UNION ALL
	SELECT
	  PostId,
	  PostTypeId,
	  c.Id AS EventId,
	  "Comment" AS Event,
	  u.DisplayName AS UserName,
	  c.CreationDate AS CreationDate,
	  c.Text AS Text
	FROM Comments c
	JOIN Posts p ON c.PostId = p.Id
	JOIN Users u ON c.UserId = u.Id
) AS EditHistory;

CREATE INDEX EditHistoryPostIdIndex ON EditHistory(PostId);
CREATE INDEX EditHistoryEventIdIndex ON EditHistory(EventId);