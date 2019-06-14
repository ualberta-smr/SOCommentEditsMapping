CREATE TABLE EditHistory AS
    SELECT *
    FROM (
        SELECT
          pv.PostId AS PostId,
          pv.PostTypeId AS PostTypeId,
          ph.Id AS EventId,
          CASE
            WHEN pv.PostHistoryTypeId=2 THEN "InitialBody"
            ELSE "BodyEdit"
          END AS Event,
          u.DisplayName AS UserName,
          pv.CreationDate AS CreationDate,
          p.Tags AS Tags,
          ph.Text AS Text
        FROM PostVersion pv
        JOIN PostHistory ph ON pv.PostHistoryId = ph.Id
        JOIN Users u ON ph.UserId = u.Id
        JOIN Posts p ON pv.PostId = p.Id
        WHERE p.Id IN (SELECT PostId FROM PostBlockVersion WHERE PostBlockTypeId = 2)
        UNION ALL
        SELECT
          PostId,
          PostTypeId,
          c.Id AS EventId,
          "Comment" AS Event,
          u.DisplayName AS UserName,
          c.CreationDate AS CreationDate,
          p.Tags As Tags,
          c.Text AS Text
        FROM Comments c
        JOIN Posts p ON c.PostId = p.Id
        JOIN Users u ON c.UserId = u.Id
    ) AS EditHistory;

    CREATE INDEX EditHistoryPostIdIndex ON EditHistory(PostId);
    CREATE INDEX EditHistoryEventIdIndex ON EditHistory(EventId);
