A recursive query in SQL is a query that repeatedly executes a part of itself to process hierarchical or tree-structured data. It's often used to navigate relationships where a parent-child structure exists, such as organizational charts, bill of materials, or file systems.

The most common way to write a recursive query is by using a **Common Table Expression (CTE)** with the `WITH` clause. A recursive CTE consists of two parts:

1.  **Anchor Member**: The initial query that establishes the base result set. This part is non-recursive and provides the starting point for the recursion.
2.  **Recursive Member**: The part that references the CTE itself and repeatedly joins with the result of the previous execution. This process continues until an empty result set is returned, which terminates the recursion.

-----

### Simple Example: Employee Hierarchy 🧑‍💼

Imagine a table named `employees` that stores information about an employee's ID, name, and their manager's ID. You can use a recursive CTE to find all employees who report to a specific manager, no matter how many levels deep the hierarchy goes.

**Table Schema:**

| employee\_id | employee\_name | manager\_id |
| :---------- | :------------ | :--------- |
| 1           | Alice         | NULL       |
| 2           | Bob           | 1          |
| 3           | Charlie       | 1          |
| 4           | David         | 2          |
| 5           | Eve           | 3          |

**Problem:** Find all employees who report to Alice (employee\_id = 1).

**Recursive Query:**

```sql
WITH RECURSIVE subordinates AS (
  -- Anchor Member: Find the direct subordinates of the target manager.
  SELECT employee_id, employee_name, manager_id
  FROM employees
  WHERE manager_id = 1
  
  UNION ALL
  
  -- Recursive Member: Join the CTE with the employees table to find the next level of subordinates.
  SELECT e.employee_id, e.employee_name, e.manager_id
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.employee_id
)

-- Final SELECT statement to retrieve the results.
SELECT * FROM subordinates;
```

-----

### How It Works 🤯

1.  **Anchor Member**: The first `SELECT` statement runs and finds the direct subordinates of manager ID 1. The result set is Bob (ID 2) and Charlie (ID 3). This is the initial "subordinates" table.

2.  **Recursive Member (First Iteration)**: The `UNION ALL` part takes the result from the previous step (Bob and Charlie) and joins it with the `employees` table.

      * It finds employees whose `manager_id` is either 2 (Bob) or 3 (Charlie).
      * This returns David (ID 4) and Eve (ID 5).
      * This new result set is added to the "subordinates" table.

3.  **Recursive Member (Second Iteration)**: The process repeats. The query now looks for managers with IDs 4 and 5. Since no employees report to them, the result set is empty.

4.  **Termination**: The recursion stops because the recursive part of the query returned an empty set.

5.  **Final Result**: The `SELECT * FROM subordinates` returns the complete list of all employees found during the process: Bob, Charlie, David, and Eve.