CREATE TABLE EditHistory AS
    SELECT *
    FROM (
        SELECT
          pv.PostId AS PostId,
          p.ParentId AS ParentId,
          pv.PostTypeId AS PostTypeId,
          ph.Id AS EventId,
          CASE
            WHEN pv.PostHistoryTypeId=2 THEN "InitialBody"
            ELSE "BodyEdit"
          END AS Event,
          u.DisplayName AS UserName,
          pv.CreationDate AS CreationDate,
          p.Tags AS Tags,
          p.Score AS Score,
          ph.Text AS Text
        FROM PostVersion pv
        JOIN PostHistory ph ON pv.PostHistoryId = ph.Id
        JOIN Users u ON ph.UserId = u.Id
        JOIN Posts p ON pv.PostId = p.Id
        WHERE p.Id IN (SELECT DISTINCT pbv.PostId FROM PostBlockVersion pbv WHERE PostBlockTypeId = 2)
        UNION ALL
        SELECT
          p.Id AS PostId,
          p.ParentId AS ParentId,
          p.PostTypeId AS PostTypeId,
          c.Id AS EventId,
          "Comment" AS Event,
          u.DisplayName AS UserName,
          c.CreationDate AS CreationDate,
          p.Tags AS Tags,
          c.Score AS Score,
          c.Text AS Text
        FROM Comments c
        JOIN Posts p ON c.PostId = p.Id
        JOIN Users u ON c.UserId = u.Id
        WHERE p.Id IN (SELECT DISTINCT pbv.PostId FROM PostBlockVersion pbv WHERE PostBlockTypeId = 2)
    ) AS EditHistory;

    CREATE INDEX EditHistoryPostIdIndex ON EditHistory(PostId);
    CREATE INDEX EditHistoryEventIdIndex ON EditHistory(EventId);
