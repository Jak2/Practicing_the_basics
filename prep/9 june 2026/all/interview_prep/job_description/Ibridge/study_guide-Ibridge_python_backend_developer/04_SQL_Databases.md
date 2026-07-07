# 04 — SQL & Relational Databases
## HIGH PRIORITY — Live coding test very likely. This section can make or break the offer.

> **jak_ai_job_coach framing:** SQL is the great equalizer. Interviewers use it to separate candidates who understand data from those who just copy queries. For a senior role, they don't care if you can write SELECT — they want to see how you think about data, performance, and failure. Every question is really asking: "Have you operated a system that had to survive real load?" This guide gives you the mental models to answer like someone who has.

---

## The interviewer's real agenda

When they ask SQL questions, they are probing for:
1. **Correctness** — do you know the fundamentals cold?
2. **Performance instinct** — do you think about indexes and query plans without being asked?
3. **Production awareness** — have you seen things break, and do you know why?
4. **Communication** — can you reason out loud? Senior engineers narrate their thinking.
5. **AI-usage detection** — they will ask follow-ups until they find the edge of your real knowledge.

**Junior answer:** Recites the syntax correctly, stops there.
**Senior answer:** Gives the syntax, then immediately talks about edge cases, performance implications, and when you'd choose a different approach.

---

## SQL Under Pressure — Read This First

> **This is the meta-skill.** If you can't write perfect SQL in 30 seconds, you can still pass by thinking out loud like a senior engineer.

### What to say when you're stuck

Never go silent. Narrate:

- *"Let me think about what tables I need and what the join condition is before I write anything."*
- *"I'm going to start with the FROM clause and work outward — I find that cleaner than starting from SELECT."*
- *"I know I need a window function here. Let me first think about what the partition key should be."*
- *"My first instinct is a subquery, but a CTE (Common Table Expression) would be more readable. Let me use the CTE."*
- *"I'm going to write the basic version first, then add the performance considerations."*

### The "think out loud" framework for live SQL

1. **Restate the problem** in your own words: *"So you want one row per department, showing the employee with the second-highest salary?"*
2. **Identify the tables and join keys** before touching the keyboard.
3. **Name the operation** — aggregation, window, filter, anti-join — so they know you have a mental model.
4. **Write skeleton first**: FROM, JOIN, WHERE — then add SELECT and GROUP BY.
5. **Check your output shape**: "This should return N rows, one per X" — sanity-check before you submit.

### Common mistakes under pressure

- Writing `WHERE` when you need `HAVING` (forgetting execution order).
- Forgetting `GROUP BY` on all non-aggregated SELECT columns.
- Using `=` instead of `IS NULL` / `IS NOT NULL`.
- `RANK()` when you meant `DENSE_RANK()` for the Nth-highest pattern — be explicit about tie behavior.
- Aliasing a column in SELECT then referencing the alias in WHERE — it doesn't exist yet at WHERE time.

### When you make a mistake (and you will)

*"Good catch. I made the classic mistake of using the alias in WHERE — that alias doesn't exist in the execution order until after SELECT runs. Let me fix that."*

This is actually a senior signal — you caught it, you named the reason, you moved on.

---

## 1. Query Execution Order — The Foundation of Everything

**Written order vs logical execution order — this explains 80% of SQL "gotchas".**

Written order: `SELECT … FROM … JOIN … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`

**Logical execution order (how the DB actually processes it):**
```
FROM / JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  DISTINCT  →  ORDER BY  →  LIMIT
```

### Why this matters — and what the interviewer is really asking

When an interviewer asks "why can't you use a SELECT alias in a WHERE clause?" — they want to know if you understand execution order or if you just memorized the rule.

**Ready-to-say spoken answer:**

*"The WHERE clause executes before SELECT in the logical processing order. So when the database engine is evaluating WHERE, the alias you defined in SELECT literally doesn't exist yet — it hasn't been computed. This is the same reason you use HAVING instead of WHERE to filter on aggregate results: WHERE runs before aggregation happens, so you can't filter on COUNT(*) in WHERE. You have to filter in HAVING, which runs after GROUP BY."*

### The follow-up they always ask

"So why does ORDER BY allow you to use a SELECT alias?"

*"Because ORDER BY executes after SELECT in the logical order — it's one of the last operations. The alias exists by then. It's one of the few places where aliases work. PostgreSQL actually extends this slightly — it lets you reference SELECT aliases in GROUP BY as a convenience feature, but that's Postgres-specific and not standard SQL."*

---

## 2. JOINs — Know These Cold, Plus the Edge Cases

**What the interviewer is probing:** Do you understand set theory, or are you just pattern-matching keywords?

```
INNER JOIN    → rows with matches in BOTH tables
LEFT JOIN     → all left rows + matched right (NULL where no match)
RIGHT JOIN    → mirror of LEFT (almost never use this — just swap table order and LEFT JOIN)
FULL OUTER    → all rows from both, NULLs where no match
CROSS JOIN    → cartesian product (every row × every row) — rarely intentional
SELF JOIN     → table joined to itself (manager/employee hierarchies)
```

### The query they actually run in interviews

```sql
-- All users, showing their total order amount (NULL if no orders)
SELECT u.name, SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
ORDER BY total_spent DESC NULLS LAST;

-- Users with NO orders (anti-join pattern)
SELECT u.name
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

### Senior signal — the filter placement trap

**This is a classic interview trick and a real production bug source:**

```sql
-- WRONG INTENTION: "users who have orders over $100, plus all users with no orders"
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.amount > 100;  -- This KILLS the LEFT JOIN — NULL rows fail the WHERE check

-- RIGHT WAY: move the filter into the JOIN condition
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 100;
```

**Ready-to-say spoken answer for the trap:**

*"The difference between filtering in the WHERE clause versus in the ON condition matters a lot with outer joins. If you put a filter on the right table in the WHERE clause, you're implicitly converting your LEFT JOIN into an INNER JOIN — because NULL values fail the WHERE condition and those rows get eliminated. If you want to keep all left-side rows and just conditionally pull matching right-side rows, the filter belongs in the ON condition. I've seen this bug ship to production more than once."*

### The follow-up

"When would you use a CROSS JOIN intentionally?"

*"Generating a calendar table — you cross join a date series with a list of entities to get every date-entity combination as a scaffold, then LEFT JOIN your actual data onto it. That way you get rows for days with zero events, which you need for time-series reporting."*

---

## 3. Aggregations & GROUP BY

**What the interviewer is probing:** Do you understand the mechanics, or do you just know the keywords?

```sql
SELECT user_id,
       COUNT(*)          AS order_count,
       COUNT(coupon_id)  AS orders_with_coupon,  -- NULLs ignored
       SUM(amount)       AS total,
       AVG(amount)       AS avg_order,
       MIN(created_at)   AS first_order
FROM orders
WHERE status = 'paid'
GROUP BY user_id
HAVING SUM(amount) > 1000
ORDER BY total DESC;
```

### The subtle NULL trap interviewers love

*"COUNT(*) counts all rows including NULLs. COUNT(column_name) counts only non-NULL values in that column. This is almost never mentioned in tutorials but it bites people constantly. If you're counting optional fields, you need to decide which one you want — and you should state the choice explicitly."*

### WHERE vs HAVING — the answer they want to hear

**Junior answer:** "WHERE filters rows, HAVING filters groups."

**Senior answer:** *"WHERE runs before aggregation, so it operates on individual rows. HAVING runs after GROUP BY, so it operates on the aggregated result. In practice: use WHERE to reduce your dataset before the expensive aggregation work — it's a performance decision as much as a correctness one. If you filter in HAVING when you could have filtered in WHERE, you're aggregating rows you're just going to throw away."*

---

## 4. Window Functions — The Senior Differentiator

> **Interviewer framing:** This is the #1 question that separates senior from mid-level. If you can write a correct window function and explain it clearly, you've already outperformed 60% of candidates.

**The concept:** Window functions compute a value across a "window" of related rows without collapsing them. Unlike GROUP BY — which gives you one row per group — window functions give you one row per original row, with the computed value attached.

```sql
SELECT
  name,
  dept,
  salary,
  RANK()       OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk,
  DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dense_rnk,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn,
  AVG(salary)  OVER (PARTITION BY dept)                      AS dept_avg,
  salary - AVG(salary) OVER (PARTITION BY dept)             AS vs_dept_avg,
  SUM(salary)  OVER (ORDER BY hired_at ROWS UNBOUNDED PRECEDING) AS running_total
FROM employees;
```

### RANK vs DENSE_RANK vs ROW_NUMBER — always be explicit

| Function | Behavior on ties |
|---|---|
| ROW_NUMBER | Unique — arbitrary tiebreaking, no gaps |
| RANK | Ties get same rank, next rank skips (1,2,2,4) |
| DENSE_RANK | Ties get same rank, no skip (1,2,2,3) |

*"I always ask the interviewer or clarify in the comment: what should happen on a tie? For Nth highest salary, DENSE_RANK is usually more correct than RANK because RANK can give you 0 results if the tie lands on your target rank."*

---

### The "2nd Highest Salary Per Department" — Complete Worked Answer

**This is the most common window function interview question. Here is the exact SQL and the exact explanation.**

```sql
-- Method 1: Window function (preferred for readability and N-th generalization)
WITH ranked AS (
  SELECT
    name,
    dept,
    salary,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk
  FROM employees
)
SELECT name, dept, salary
FROM ranked
WHERE rnk = 2;
```

**Step-by-step spoken walkthrough — practice saying this out loud:**

*"I'll use a CTE with a window function. Inside the CTE, I partition the rows by department and rank them by salary descending using DENSE_RANK — I chose DENSE_RANK specifically because if two people share the top salary, I still want to find a second-highest value rather than getting no results. Then in the outer query I simply filter WHERE rnk = 2. The CTE makes this readable and also easy to parameterize — if you want Nth highest, you change one number.*

*If asked about performance: this does a full table scan plus a sort, which is O(n log n). For a large employees table, an index on (dept, salary DESC) would help the sort operation. But for interview purposes, this is the clean, correct answer."*

**Alternate method (subquery — show you know both):**

```sql
-- Method 2: Subquery (works in older SQL dialects without window support)
SELECT name, dept, salary
FROM employees e1
WHERE salary = (
  SELECT MAX(salary)
  FROM employees e2
  WHERE e2.dept = e1.dept
    AND e2.salary < (SELECT MAX(salary) FROM employees e3 WHERE e3.dept = e1.dept)
);
-- Note: This is a correlated subquery — N+1 behavior, slow on large tables. 
-- Mention this limitation unprompted. It's a senior signal.
```

### LAG/LEAD — time-series patterns

```sql
-- Month-over-month revenue change
SELECT
  month,
  revenue,
  LAG(revenue, 1) OVER (ORDER BY month)               AS prev_month,
  revenue - LAG(revenue, 1) OVER (ORDER BY month)     AS change,
  ROUND(
    100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY month))
    / NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0),
    2
  ) AS pct_change
FROM monthly_revenue;
```

*"The NULLIF around the denominator prevents division by zero when the previous month was zero revenue — a production bug I've hit before."*

---

## 5. Subqueries & CTEs

**CTEs are almost always the right choice in an interview.** They show you can write readable code, not just correct code.

```sql
-- CTE: who earns more than their department average?
WITH dept_avg AS (
  SELECT dept, AVG(salary) AS avg_sal
  FROM employees
  GROUP BY dept
)
SELECT e.name, e.salary, d.avg_sal
FROM employees e
JOIN dept_avg d ON e.dept = d.dept
WHERE e.salary > d.avg_sal
ORDER BY e.salary DESC;
```

### EXISTS vs IN vs JOIN — the performance conversation

**Junior answer:** "They all do the same thing."

**Senior answer:**

*"They're semantically similar but behave differently at scale. EXISTS short-circuits — as soon as it finds one matching row, it stops. So for 'does this user have any orders at all', EXISTS is efficient regardless of how many orders exist. IN with a subquery materializes the full result set, which can be slow if the subquery returns millions of rows. For large datasets, I usually rewrite IN as an EXISTS or a JOIN. A JOIN also gives the optimizer more flexibility — it can choose hash join, merge join, or nested loop depending on the data distribution. EXISTS is often the right semantic choice when you care about existence, not the values."*

---

## 6. Indexes — Production Performance Knowledge

> **Interviewer framing:** This is where they separate people who have operated databases from people who have only written queries. Every question here has a production story behind it.

### B-tree index mechanics

A B-tree index is a sorted tree structure. A lookup goes from root to leaf in O(log n) instead of O(n) for a full table scan. **The cost:** every write (INSERT/UPDATE/DELETE) must also update the index. Ten indexes on a table means eleven writes per row change.

**Ready-to-say spoken answer — "what is an index?":**

*"An index is a separate data structure — usually a B-tree — that the database maintains alongside your table. It stores a sorted copy of the indexed column values with pointers back to the heap. A lookup on an indexed column is O(log n) instead of O(n) for a full scan. The trade-off is write amplification: every index adds overhead to inserts, updates, and deletes. I've seen tables with 15 indexes where bulk inserts were 10x slower than expected because the index maintenance was dominating the write time."*

### Composite index — the leftmost prefix rule

```sql
-- Index on (dept, salary) helps these:
WHERE dept = 'Engineering'                          -- uses index
WHERE dept = 'Engineering' AND salary > 80000       -- uses index
ORDER BY dept, salary                               -- uses index

-- But NOT:
WHERE salary > 80000                                -- cannot use this index alone
                                                    -- (no leftmost prefix match)
```

**Why this matters:** *"I once spent an hour debugging a slow query only to find the composite index existed but the WHERE clause used the second column first. The index was completely ignored. Adding a single-column index on the second column fixed it."*

### How to debug a slow query — the complete answer

*"My process: first I run EXPLAIN ANALYZE to get the actual execution plan with real row counts and timing. I look for sequential scans on large tables — that's usually the smoking gun. I check whether indexes exist and whether they're being used. Sometimes an index exists but the planner won't use it — that happens when the table statistics are stale and the planner thinks a seq scan is cheaper, which means you need ANALYZE to refresh stats. I also look for nested loop joins on large tables where a hash join would be more appropriate. Then I look at the query itself — is there a function call in the WHERE clause that's defeating the index? Something like WHERE date_trunc('month', created_at) = '2024-01-01' prevents index use on created_at. You'd rewrite that as a range: WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01'."*

### Reading EXPLAIN ANALYZE output — what to say

```
Seq Scan on orders  (cost=0.00..4521.00 rows=150000 width=42)
                    (actual time=0.042..89.3 rows=150000 loops=1)
  Filter: (status = 'paid')
  Rows Removed by Filter: 12000
```

*"The first number in cost is startup cost, second is total cost — these are planner estimates. The 'actual time' shows real milliseconds. 'rows' is the estimated vs actual row count. When estimated rows differ wildly from actual, that means your table statistics are stale and the planner made a bad plan based on bad data. The fix is ANALYZE on the table, or adjusting autovacuum settings. I've fixed queries that were 100x slower than they should be just by running ANALYZE after a large data load."*

```
Index Scan using idx_orders_user_id on orders
Hash Join  (cost=... rows=...)
Nested Loop  (cost=... rows=...)  ← danger when inner table is large
```

*"A Nested Loop on large tables is usually a red flag. If you see it, check whether the join columns are indexed on both sides."*

---

## 7. Normalization & Schema Design

**What the interviewer is probing:** Can you design a schema that survives real usage, or do you just bolt columns onto tables?

### Normal forms — the short version that works in an interview

- **1NF**: Atomic columns — no comma-separated lists, no arrays of values in one cell. Each column holds one value.
- **2NF**: No partial dependency — every non-key column depends on the whole primary key, not just part of it.
- **3NF**: No transitive dependency — non-key columns don't depend on other non-key columns.

**Ready-to-say answer:**

*"I think about normalization pragmatically. 3NF is the right default for transactional data — it minimizes write anomalies and keeps your data consistent. But I don't normalize blindly. If you're building read-heavy reporting queries that join 7 tables, sometimes the right answer is a denormalized summary table or a materialized view. The question I always ask is: what's the write pattern and what's the read pattern? OLTP (Online Transaction Processing) systems lean normalized, analytical systems often need denormalization or columnar storage."*

### Constraints — the underused defense layer

```sql
CREATE TABLE orders (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  amount      NUMERIC(10,2) NOT NULL CHECK (amount > 0),
  status      VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'paid', 'cancelled')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Senior signal:** *"I use CHECK constraints aggressively. An invalid status that sneaks into the database will cause bugs you find six months later. Constraints are free — they run at write time and they're in the schema where everyone can see them. I've inherited systems where every validation was in application code, and invariably some code path bypassed it and the database was full of garbage data."*

### Many-to-many: junction table pattern

```sql
-- Example: ads can belong to multiple campaigns, campaigns have multiple ads
CREATE TABLE campaign_ads (
  campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  ad_id       INTEGER NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
  added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (campaign_id, ad_id)  -- composite PK prevents duplicate associations
);
```

*"The composite primary key on the junction table is doing double duty — it enforces uniqueness of the association and creates an index for lookups in both directions."*

---

## 8. Transactions & ACID

**What the interviewer is probing:** Do you understand concurrency, or have you only written single-threaded code?

### ACID in plain English

```
Atomicity    — all-or-nothing. If any step fails, the whole transaction rolls back.
Consistency  — the DB moves from one valid state to another. Constraints never violated mid-transaction.
Isolation    — concurrent transactions don't see each other's intermediate state.
Durability   — committed data survives crashes. Written to WAL (write-ahead log) before confirming.
```

**Ready-to-say answer:**

*"ACID is about what guarantees the database gives you under concurrent load and failure. The one people underestimate is Isolation. At the default Read Committed level in PostgreSQL, two reads in the same transaction can see different data if another transaction commits between them — that's a non-repeatable read. Most application bugs I've seen from concurrent access were actually isolation level issues. The fix isn't always to raise the isolation level — sometimes you just need to redesign the operation to be idempotent."*

### Isolation levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| Read Uncommitted | possible | possible | possible |
| Read Committed (PG default) | prevented | possible | possible |
| Repeatable Read | prevented | prevented | possible |
| Serializable | prevented | prevented | prevented |

### Deadlock production war story

*"We had a deadlock in production between two API endpoints that both updated the user balance and the transaction log. One endpoint locked user first then transaction, the other locked transaction first then user. Under concurrent load, they'd hit each other and PostgreSQL would kill one transaction. The fix was simple: enforce consistent lock ordering — always acquire locks in the same table order everywhere in the codebase. We added a comment in the transaction helper to document the required ordering. After that, zero deadlocks."*

### Optimistic vs pessimistic locking

```sql
-- Pessimistic: lock the row while you work on it
BEGIN;
SELECT * FROM inventory WHERE product_id = 42 FOR UPDATE;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 42;
COMMIT;

-- Optimistic: check version, fail if someone else changed it
UPDATE inventory
SET quantity = quantity - 1, version = version + 1
WHERE product_id = 42 AND version = :expected_version;
-- If 0 rows updated: someone else got there first, retry
```

*"Pessimistic locking is safe but reduces concurrency — that row is locked while your code runs. Optimistic locking scales better for low-contention scenarios but requires retry logic in the application. For inventory systems with high contention I use pessimistic; for things like user profile updates where conflicts are rare, optimistic."*

---

## 9. PostgreSQL vs MySQL vs SQL Server

**The honest, senior answer:**

*"My deepest experience is PostgreSQL, which is what I've used in production. The SQL fundamentals — joins, aggregations, window functions, transactions — transfer directly. The differences are mostly in ecosystem and edge features: PostgreSQL has excellent JSONB support, very standards-compliant SQL, and a more sophisticated query planner. MySQL has historically prioritized read throughput and is more permissive about things like implicit type coercions, which can mask bugs. SQL Server uses T-SQL syntax with some differences like TOP instead of LIMIT, and has excellent tooling integration with the Microsoft stack. For any of them, the first thing I'd do on a new project is check the version and look up what features are available — query behavior can vary between versions."*

---

## 10. N+1 Problem & SQLAlchemy — The ORM Section

> **Interviewer framing:** This is a direct filter for "have you operated a real application" vs "have you only done tutorials." N+1 is the most common production performance bug from ORMs (Object-Relational Mappers).

### What N+1 actually looks like

```python
# The N+1 problem in SQLAlchemy
users = session.query(User).all()       # 1 query
for user in users:
    print(user.orders)                  # N queries, one per user
                                        # 100 users = 101 queries to the DB
```

**Ready-to-say spoken answer:**

*"N+1 happens when you fetch a list of N items and then the ORM lazily loads a related object for each one, generating N additional queries. With 100 users that's 101 database round-trips instead of 2. The fix is eager loading — in SQLAlchemy that's selectinload or joinedload on the relationship. Selectinload issues a second query with WHERE user_id IN (...) — one round-trip for all the related data. Joinedload does a SQL JOIN in the first query. I prefer selectinload for most cases because it avoids row multiplication when the relationship has many items. The key habit is: before you go to code review, check your ORM queries for lazy relationship access inside loops."*

```python
# Fixed with eager loading
from sqlalchemy.orm import selectinload

users = session.query(User).options(selectinload(User.orders)).all()
# Now: 2 queries total, regardless of number of users
```

### How to detect N+1 in production

*"I configure SQLAlchemy to log all queries during development — you can see the N+1 immediately. In production I look at the database slow query log for patterns: if I see the same query repeated hundreds of times with different parameter values in a short window, that's N+1. APM tools like Datadog also flag this automatically."*

### Raw SQL vs ORM — the honest trade-off

*"ORM for CRUD operations and simple queries — it handles parameterization, connection pooling, and the migration story with Alembic. Raw SQL for complex analytics queries, anything involving window functions, or when I need to tune the execution plan. I've never seen a complex reporting query that was more readable as ORM than as SQL. The anti-pattern is using ORM chaining to build queries so complex that no one can read what SQL will be generated — at that point just write the SQL."*

---

## 11. Production War Stories — What You Only Know If You Operated It

> These are the stories that make interviewers lean forward. Practice one of these for each major topic.

### The slow query that hit production at 2am

*"We deployed a feature that added a dashboard showing all orders for an admin user. Worked fine in testing with 50 rows. In production with 2 million orders, the page took 45 seconds and started timing out. EXPLAIN ANALYZE showed a sequential scan on the orders table — the filter was on created_at but we'd used date_trunc() in the WHERE clause, which wrapped the column in a function call and defeated the index. Rewrote it as a range condition, added a partial index on status, query went from 45s to 80ms. The lesson: never wrap an indexed column in a function in a WHERE clause."*

### The missing index on a foreign key

*"PostgreSQL doesn't automatically create indexes on foreign key columns — that's a MySQL thing. We had a users table and an orders table. The query `SELECT * FROM orders WHERE user_id = ?` was fast because we'd indexed user_id. But `DELETE FROM users WHERE id = ?` was doing a full scan of the orders table to check the FK constraint. Took us a while to realize the delete was the slow operation, not the read. Added the index on orders.user_id and deletes went from 2 seconds to 1ms."*

### The transaction deadlock under load

*"Described in the ACID section above — two code paths acquiring locks in different orders. The thing I learned: in PostgreSQL, when a deadlock occurs it shows up in the logs with both transaction traces. The key diagnostic is looking at the lock wait graph. Once you see it, the fix is always the same: consistent ordering."*

### The N+1 that took down staging

*"New feature loaded a user's activity feed — 50 posts per page. Each post loaded the author's profile. That's 51 queries per page load. With 20 concurrent users during a demo, the database hit connection limit and started rejecting connections. Fixed in 10 minutes with selectinload, but the demo was already ruined. After that we added a test that asserts query count for any endpoint that renders a list."*

---

## 12. AI-Assisted Dev Traps — Questions That Catch AI-Copilot Users

> **These questions are specifically designed to probe whether you understand what you've shipped. If you used AI to write your SQL, be prepared for these.**

### "Walk me through what this query is doing."

The interviewer shows you a query and asks you to explain it. The trap: they show you something *similar* to what an AI would generate but with a subtle bug (wrong join type, missing NULL handling, wrong aggregation scope).

**How to handle it:** Read it line by line out loud. "The CTE computes... the outer query joins on... the WHERE clause is filtering... wait, this is a LEFT JOIN but the WHERE is filtering on the right table column, which would turn it into an inner join. Is that intentional?"

### "Why is this query slow?"

They show you a query and an EXPLAIN ANALYZE output. They want to see if you can read an execution plan.

**What to look for:**
- Seq Scan on large tables (missing index)
- Row estimate wildly off from actual (stale statistics)
- Nested Loop with large inner table (should be Hash Join)
- Sort operation with no index (can it be covered?)
- Function call on indexed column in WHERE

### "What does this execution plan tell you?"

*"I look at the actual time vs estimated time first — if they're very different, the planner had bad information. Then I look at the node types: Seq Scan means no index was used. I check the rows estimate vs actual — a large mismatch means table statistics need refreshing. Then I look for the most expensive node by cost and ask why it's expensive."*

### "Your query works — what happens when this table grows to 100 million rows?"

This is the scale-thinking probe. They want to hear: index coverage, partitioning, potential for archiving, whether the query is doing unnecessary work.

*"At that scale I'd check: does the WHERE clause have proper index coverage? Is there a sequential scan anywhere? Could we partition the table by date to keep the hot partition small? Is the query doing any full-table operations we could avoid with a smarter schema design?"*

### "You mentioned you used SQLAlchemy — show me the ORM code for this and tell me what SQL it generates."

*"The ORM code would be... and SQLAlchemy would generate a query that looks like... The thing I always check is whether it's doing any implicit lazy loads — I'd add selectinload on any relationship I access in the result loop to make sure I'm not hitting N+1."*

---

## 13. Practice Drills — Write From Scratch Before Interview Day

Practice these with pen and paper or a blank SQL editor. No autocomplete.

1. **2nd highest salary per department** (window function — full worked answer in Section 4)
2. **Users with no orders** (anti-join: LEFT JOIN + WHERE right.id IS NULL)
3. **Top 3 products by revenue per category** (window + filter rnk <= 3)
4. **Duplicate emails** (`GROUP BY email HAVING COUNT(*) > 1`)
5. **Running monthly revenue total** (`SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING)`)
6. **Customers who ordered in every month of a quarter** (GROUP BY customer, month, then HAVING COUNT(DISTINCT month) = 3)
7. **Three-table join with aggregation** (users → orders → products: total spend per user per product category)
8. **Month-over-month growth %** (LAG + NULLIF for zero-division safety)
9. **Delete duplicates keeping the row with lowest id** (DELETE FROM ... WHERE id NOT IN (SELECT MIN(id) FROM ... GROUP BY email))
10. **Median salary per department** (PERCENTILE_CONT(0.5) WITHIN GROUP ... — shows PostgreSQL-specific knowledge)

---

## 14. Likely Interview Questions — With Full Spoken Answers

### Q1: INNER vs LEFT JOIN — give an example

*"INNER JOIN returns only rows where the join condition matches in both tables. LEFT JOIN returns all rows from the left table plus matched rows from the right — NULLs fill in where there's no match. Classic example: users LEFT JOIN orders gives you all users, including those who've never placed an order. INNER JOIN would silently drop those users. For reporting, you almost always want LEFT JOIN so you can count zero-order users. The gotcha is putting a filter on the right table in the WHERE clause — that silently converts your LEFT JOIN to an INNER JOIN because NULL fails the comparison."*

### Q2: WHERE vs HAVING

*"WHERE runs before aggregation — it filters individual rows. HAVING runs after GROUP BY — it filters aggregate results. Performance implication: always filter in WHERE when possible to reduce the rows going into the aggregation. You can only use HAVING for conditions that involve aggregate functions like COUNT(*) or SUM()."*

### Q3: Write 2nd highest salary

See Section 4 — use the CTE + DENSE_RANK approach, walk through it out loud.

### Q4: What is an index, when does it hurt?

*"An index is a sorted auxiliary data structure that makes reads faster at the cost of slower writes. It helps when you're filtering or joining on the indexed column. It hurts when you over-index: every index adds write overhead on insert/update/delete. I've seen batch insert jobs that were 10x slower than expected because the table had 12 indexes. You also don't want indexes on very low-cardinality columns — a boolean column that's 90% true has terrible selectivity and the planner will often ignore the index anyway and do a seq scan. The other trap is indexing columns that are always accessed through a function — the index won't be used."*

### Q5: How would you debug a slow query?

Full answer in Section 6 — EXPLAIN ANALYZE, execution plan reading, stale statistics, function-in-WHERE trap.

### Q6: Explain ACID and isolation levels

Full answer in Section 8 — use the deadlock war story.

### Q7: Normalization vs denormalization

*"Normalize for write-heavy transactional systems — it prevents update anomalies and keeps data consistent. Denormalize for read-heavy analytical systems or when join cost becomes a bottleneck. I've done both: built 3NF schemas for the transactional core, then materialized views or summary tables for the reporting layer. The key is being intentional — denormalize deliberately with documentation, not accidentally because it was easier to add a column."*

### Q8: How do you prevent SQL injection?

*"Always use parameterized queries — never string-format values into SQL. In SQLAlchemy, the ORM handles this automatically for ORM queries; for raw SQL you use `text()` with bound parameters. I also apply the principle of least privilege — the DB user the application connects as should only have SELECT/INSERT/UPDATE/DELETE on the tables it needs, never DDL permissions. Defense in depth: parameterized queries are the first line, DB permissions are the second."*

### Q9: Window function vs GROUP BY

*"GROUP BY collapses rows — you get one row per group. Window functions don't collapse — you get one row per original row, with the computed value attached. If you need 'each employee plus their department average', you can't do that with GROUP BY without a self-join. A window function does it in one pass. The trade-off: window functions can be more expensive because the optimizer has less freedom to restructure the query. For aggregation where you don't need the individual rows, GROUP BY is more efficient."*

### Q10: N+1 problem

Full answer in Section 10 — use the production story, explain the eager loading fix.

---

## 15. The Mental Model for the Day

**When they ask a SQL question, run this checklist in your head before you speak:**

1. What is the correct answer?
2. What breaks at scale?
3. What's the common mistake / gotcha?
4. What's the production story?
5. When would you choose a different approach?

If you can hit 3 of those 5, you're answering like a senior engineer, not a tutorial-learner.

**The single sentence that separates senior from junior in SQL interviews:**

After you give your answer, add: *"The thing I'd watch out for in production is..."*

That sentence tells them everything.

---

## 16. CTEs — Common Table Expressions (GAP FILL)

**Why this matters:** CTEs are asked in nearly every senior SQL round. A 5-year engineer who fumbles a CTE looks junior.

### What is a CTE?

A CTE is a named temporary result set defined with `WITH` at the top of a query. It makes complex SQL readable by breaking it into named steps.

```sql
-- Basic CTE: find all orders over £1000, then count by customer
WITH big_orders AS (
    SELECT customer_id, order_id, total
    FROM orders
    WHERE total > 1000
)
SELECT customer_id, COUNT(*) AS big_order_count
FROM big_orders
GROUP BY customer_id
ORDER BY big_order_count DESC;
```

### CTE vs subquery — when to use which?

| | CTE | Subquery |
|---|---|---|
| Readability | High — named, reusable | Low for nested |
| Reuse same result | Yes (reference by name) | No (must repeat) |
| Performance | Same in most DBs (no materialization by default in PG) | Same |
| Debugging | Easier — SELECT from CTE alone | Harder |

**Use a CTE when:** the intermediate result has a meaningful name, when you need the same result more than once, or when nesting would be 3+ levels deep.

### Chained CTEs

```sql
-- Step 1 → Step 2 → final query (readable pipeline)
WITH
active_users AS (
    SELECT user_id FROM users WHERE last_login > NOW() - INTERVAL '30 days'
),
user_revenue AS (
    SELECT o.user_id, SUM(o.total) AS revenue
    FROM orders o
    JOIN active_users a ON o.user_id = a.user_id
    GROUP BY o.user_id
)
SELECT user_id, revenue
FROM user_revenue
WHERE revenue > 500
ORDER BY revenue DESC;
```

### Recursive CTE (know the shape, not the code by heart)

Used for tree structures (org charts, parent-child hierarchies, file paths). The shape:

```sql
WITH RECURSIVE tree AS (
    -- Base case: start at root
    SELECT id, name, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    -- Recursive step: join children
    SELECT c.id, c.name, c.parent_id, t.depth + 1
    FROM categories c
    JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth;
```

**Interview spoken answer:**
> "A CTE is a WITH clause that names a subquery so you can reference it later. The main benefit over a nested subquery is readability — you give the intermediate result a meaningful name and you can chain multiple CTEs like a pipeline. Performance is generally the same in PostgreSQL since CTEs aren't automatically materialized. I use them whenever a query would be more than 2 levels deep or when the intermediate result has a clear semantic meaning. Recursive CTEs I use for hierarchical data — org charts, category trees — where you don't know the depth ahead of time."

---

## 17. Upserts — INSERT ... ON CONFLICT (GAP FILL)

**Why this matters:** Practical PostgreSQL question. Shows you know real production patterns.

### The pattern

```sql
-- Insert a user; if email already exists, update last_login
INSERT INTO users (email, name, last_login)
VALUES ('user@example.com', 'Jaya', NOW())
ON CONFLICT (email)
DO UPDATE SET last_login = EXCLUDED.last_login;
```

`EXCLUDED` refers to the row that *would have been inserted* — the values from the VALUES clause.

### DO NOTHING variant

```sql
-- Insert if not exists; silently skip if duplicate
INSERT INTO event_log (event_id, payload, created_at)
VALUES ('evt-123', '{"type": "click"}', NOW())
ON CONFLICT (event_id)
DO NOTHING;
```

Use `DO NOTHING` for idempotent event ingestion — calling it twice is safe.

### Idempotency with upserts

```sql
-- Idempotent job status update (Celery task runner pattern)
INSERT INTO job_status (job_id, status, updated_at)
VALUES ('job-abc', 'processing', NOW())
ON CONFLICT (job_id)
DO UPDATE SET
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at
WHERE job_status.status != 'completed';  -- don't overwrite terminal states
```

**Interview spoken answer:**
> "Upsert is `INSERT ... ON CONFLICT` — PostgreSQL's way to atomically say 'insert this row, and if the unique constraint fires, do this instead.' The two variants are `DO NOTHING` — which just silently skips the duplicate — and `DO UPDATE SET` — which lets you update specific columns using the `EXCLUDED` alias for the values you tried to insert. I use this heavily for idempotent API patterns: a client can safely retry a request and the second call won't create a duplicate, it'll just update the relevant fields. It's also the right pattern for cache-miss materializations where multiple workers might try to insert the same computed row simultaneously."

---

## 18. PostgreSQL JSONB (GAP FILL)

**Why this matters:** Brane's schema used `brief JSONB` and `result JSONB` columns. Direct resume tie-in.

### Basics

JSONB stores JSON in decomposed binary form — indexable, queryable, faster than JSON (which stores as plain text).

```sql
-- Store
INSERT INTO jobs (job_id, brief) VALUES ('j1', '{"brand": "Nike", "tone": "bold"}');

-- Query into JSONB
SELECT * FROM jobs WHERE brief->>'brand' = 'Nike';

-- Operators
brief->'brand'        -- returns JSON value (preserves type): "Nike"
brief->>'brand'       -- returns text: Nike
brief#>'{meta,size}'  -- nested path, JSON value
brief#>>'{meta,size}' -- nested path, text
```

### Containment operator (powerful)

```sql
-- Find all jobs where brief contains this subset
SELECT * FROM jobs WHERE brief @> '{"tone": "bold"}';
```

### Indexing JSONB (important for production)

```sql
-- GIN index — makes @> containment and key existence fast
CREATE INDEX idx_jobs_brief ON jobs USING GIN (brief);

-- Or index a specific key if always queried
CREATE INDEX idx_jobs_brand ON jobs ((brief->>'brand'));
```

**Interview spoken answer:**
> "In Brane, we stored the ad brief and generation result as JSONB columns because the schema of those objects varied per brand — different fields, different nested structures. JSONB is stored in binary format so PostgreSQL can index into it and query individual keys without parsing the whole string each time. The key operators are `->` for JSON value, `->>` for text value, and `@>` for containment — 'does this JSONB object contain this subset.' You create a GIN index on the column to make containment queries fast. The trade-off is writes are slightly slower than a plain JSON column because of the decomposition step, but for read-heavy analytical use it's always worth it."
