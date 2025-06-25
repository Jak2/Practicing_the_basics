questions and answers separated for each SQL function. 

---

### SELECT, WHERE, ORDER BY, GROUP BY, HAVING

#### SELECT Questions
1. How do you retrieve all columns from the employees table?
2. How can you get only the employee_id and name from the employees table?
3. How do you select unique department_ids from the employees table?
4. How can you alias a column name in a SELECT statement?
5. How do you select the top 5 rows from the sales table?
6. How can you combine text in a SELECT statement?
7. How do you select data with a specific condition on a date?
8. How can you use SELECT to calculate a value?
9. How do you select rows with NULL values in a column?
10. How can you limit the number of rows returned?

#### SELECT Answers
1. `SELECT * FROM employees;`
2. `SELECT employee_id, name FROM employees;`
3. `SELECT DISTINCT department_id FROM employees;`
4. `SELECT employee_id AS emp_id FROM employees;`
5. `SELECT TOP 5 * FROM sales;`
6. `SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM employees;`
7. `SELECT * FROM orders WHERE order_date = '2025-06-25';`
8. `SELECT salary * 1.1 AS increased_salary FROM employees;`
9. `SELECT * FROM employees WHERE manager_id IS NULL;`
10. `SELECT * FROM employees LIMIT 10;`

#### WHERE Questions
1. How do you filter employees with a salary greater than 50000?
2. How can you filter rows with multiple conditions?
3. How do you find employees hired after January 1, 2024?
4. How can you use WHERE with a LIKE operator?
5. How do you filter rows where a column is NOT NULL?
6. How can you use BETWEEN in a WHERE clause?
7. How do you filter with an IN clause?
8. How can you exclude specific values with NOT IN?
9. How do you use WHERE with a subquery?
10. How can you filter with a range of dates?

#### WHERE Answers
1. `SELECT * FROM employees WHERE salary > 50000;`
2. `SELECT * FROM sales WHERE region = 'West' AND sale_amount > 1000;`
3. `SELECT * FROM employees WHERE hire_date > '2024-01-01';`
4. `SELECT * FROM customers WHERE name LIKE 'A%';`
5. `SELECT * FROM employees WHERE commission IS NOT NULL;`
6. `SELECT * FROM orders WHERE order_amount BETWEEN 100 AND 1000;`
7. `SELECT * FROM employees WHERE department_id IN (10, 20, 30);`
8. `SELECT * FROM products WHERE category NOT IN ('electronics', 'clothing');`
9. `SELECT * FROM employees WHERE department_id IN (SELECT department_id FROM departments WHERE location = 'Pune');`
10. `SELECT * FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

#### ORDER BY Questions
1. How do you sort employees by salary in descending order?
2. How can you sort by multiple columns?
3. How do you sort employees by hire_date in ascending order?
4. How can you order by a calculated column?
5. How do you sort with a specific column alias?
6. How can you order by a column index?
7. How do you sort NULL values last?
8. How can you order by a case-sensitive column?
9. How do you sort with a custom order?
10. How can you limit sorted results?

#### ORDER BY Answers
1. `SELECT * FROM employees ORDER BY salary DESC;`
2. `SELECT * FROM sales ORDER BY region, sale_date DESC;`
3. `SELECT * FROM employees ORDER BY hire_date ASC;`
4. `SELECT employee_id, salary * 1.1 AS new_salary FROM employees ORDER BY new_salary;`
5. `SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM employees ORDER BY full_name;`
6. `SELECT employee_id, name, salary FROM employees ORDER BY 3 DESC;`
7. `SELECT * FROM employees ORDER BY COALESCE(salary, 0) DESC;`
8. `SELECT * FROM products ORDER BY BINARY product_name;`
9. `SELECT * FROM orders ORDER BY CASE status WHEN 'completed' THEN 1 WHEN 'pending' THEN 2 ELSE 3 END;`
10. `SELECT * FROM sales ORDER BY sale_amount DESC LIMIT 5;`

#### GROUP BY Questions
1. How do you count employees per department?
2. How can you calculate the total sales per region?
3. How do you find the average salary per department?
4. How can you group by multiple columns?
5. How do you group with a rolled-up total?
6. How can you group by a calculated column?
7. How do you group by with a date part?
8. How can you group with a CUBE operator?
9. How do you group by with a string function?
10. How can you group with a subquery?

#### GROUP BY Answers
1. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;`
2. `SELECT region, SUM(sale_amount) FROM sales GROUP BY region;`
3. `SELECT department_id, AVG(salary) FROM employees GROUP BY department_id;`
4. `SELECT region, sale_date, COUNT(*) FROM sales GROUP BY region, sale_date;`
5. `SELECT region, COUNT(*) FROM sales GROUP BY ROLLUP(region);`
6. `SELECT CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END AS salary_level, COUNT(*) FROM employees GROUP BY CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END;`
7. `SELECT YEAR(sale_date), SUM(sale_amount) FROM sales GROUP BY YEAR(sale_date);`
8. `SELECT region, product_id, COUNT(*) FROM sales GROUP BY CUBE(region, product_id);`
9. `SELECT LEFT(product_name, 1), COUNT(*) FROM products GROUP BY LEFT(product_name, 1);`
10. `SELECT department_id, COUNT(*) FROM (SELECT * FROM employees WHERE hire_date > '2024-01-01') e GROUP BY department_id;`

#### HAVING Questions
1. How do you filter groups with more than 5 employees?
2. How can you find regions with total sales over 10000?
3. How do you filter departments with average salary above 60000?
4. How can you use HAVING with multiple conditions?
5. How do you filter groups with the minimum sale amount above 100?
6. How can you use HAVING with a subquery?
7. How do you filter groups with maximum salary below 80000?
8. How can you use HAVING with a date function?
9. How do you filter groups with no NULL values?
10. How can you combine HAVING with ORDER BY?

#### HAVING Answers
1. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > 5;`
2. `SELECT region, SUM(sale_amount) FROM sales GROUP BY region HAVING SUM(sale_amount) > 10000;`
3. `SELECT department_id, AVG(salary) FROM employees GROUP BY department_id HAVING AVG(salary) > 60000;`
4. `SELECT product_id, COUNT(*) FROM sales GROUP BY product_id HAVING COUNT(*) > 10 AND SUM(sale_amount) > 5000;`
5. `SELECT product_id, MIN(sale_amount) FROM sales GROUP BY product_id HAVING MIN(sale_amount) > 100;`
6. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > (SELECT AVG(count) FROM (SELECT department_id, COUNT(*) AS count FROM employees GROUP BY department_id) t);`
7. `SELECT department_id, MAX(salary) FROM employees GROUP BY department_id HAVING MAX(salary) < 80000;`
8. `SELECT YEAR(sale_date), SUM(sale_amount) FROM sales GROUP BY YEAR(sale_date) HAVING SUM(sale_amount) > 5000;`
9. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) = COUNT(salary);`
10. `SELECT region, SUM(sale_amount) FROM sales GROUP BY region HAVING SUM(sale_amount) > 10000 ORDER BY SUM(sale_amount) DESC;`

---

### JOIN, INNER, LEFT, RIGHT, FULL

#### JOIN Questions
1. How do you combine employees and departments tables?
2. How can you join sales with products?
3. How do you join with a condition?
4. How can you join with multiple columns?
5. How do you join with a subquery?
6. How can you join with an alias?
7. How do you join with a WHERE clause?
8. How can you join with GROUP BY?
9. How do you join with a HAVING clause?
10. How can you join with ORDER BY?

#### JOIN Answers
1. `SELECT e.employee_id, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id;`
2. `SELECT s.sale_id, p.product_name FROM sales s JOIN products p ON s.product_id = p.product_id;`
3. `SELECT e.name, d.location FROM employees e JOIN departments d ON e.department_id = d.department_id WHERE d.location = 'Pune';`
4. `SELECT a.order_id, b.customer_id FROM orders a JOIN order_details b ON a.order_id = b.order_id AND a.customer_id = b.customer_id;`
5. `SELECT e.employee_id, d.avg_salary FROM employees e JOIN (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) d ON e.department_id = d.department_id;`
6. `SELECT a.employee_id, b.dept_name FROM employees a JOIN departments b ON a.department_id = b.department_id;`
7. `SELECT e.name, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id WHERE e.salary > 50000;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
9. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name HAVING COUNT(e.employee_id) > 5;`
10. `SELECT e.employee_id, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id ORDER BY d.department_name;`

#### INNER Questions
1. How do you get matching records from employees and departments?
2. How can you filter inner join results?
3. How do you use INNER JOIN with a condition?
4. How can you join with multiple tables?
5. How do you use INNER JOIN with GROUP BY?
6. How can you order INNER JOIN results?
7. How do you use INNER JOIN with a subquery?
8. How can you filter with HAVING after INNER JOIN?
9. How do you join with a calculated column?
10. How can you use INNER JOIN with a date condition?

#### INNER Answers
1. `SELECT e.employee_id, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;`
2. `SELECT e.name, d.location FROM employees e INNER JOIN departments d ON e.department_id = d.department_id WHERE d.location = 'Pune';`
3. `SELECT e.employee_id, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id WHERE e.salary > 50000;`
4. `SELECT e.employee_id, d.department_name, m.manager_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id INNER JOIN managers m ON e.manager_id = m.manager_id;`
5. `SELECT d.department_name, COUNT(e.employee_id) FROM employees e INNER JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name;`
6. `SELECT e.employee_id, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id ORDER BY d.department_name;`
7. `SELECT e.employee_id, d.avg_salary FROM employees e INNER JOIN (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) d ON e.department_id = d.department_id;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM employees e INNER JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name HAVING COUNT(e.employee_id) > 5;`
9. `SELECT e.employee_id, d.department_name, e.salary * 1.1 AS new_salary FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;`
10. `SELECT e.employee_id, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id WHERE e.hire_date > '2024-01-01';`

#### LEFT Questions
1. How do you get all employees with their departments?
2. How can you filter LEFT JOIN results?
3. How do you use LEFT JOIN with a condition?
4. How can you join with multiple tables using LEFT JOIN?
5. How do you use LEFT JOIN with GROUP BY?
6. How can you order LEFT JOIN results?
7. How do you use LEFT JOIN with a subquery?
8. How can you filter with HAVING after LEFT JOIN?
9. How do you join with a calculated column using LEFT JOIN?
10. How can you use LEFT JOIN with a date condition?

#### LEFT Answers
1. `SELECT e.employee_id, d.department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id;`
2. `SELECT e.name, d.location FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id WHERE d.location IS NOT NULL;`
3. `SELECT e.employee_id, d.department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id WHERE e.salary > 50000;`
4. `SELECT e.employee_id, d.department_name, m.manager_name FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id LEFT JOIN managers m ON e.manager_id = m.manager_id;`
5. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d LEFT JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
6. `SELECT e.employee_id, d.department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id ORDER BY d.department_name;`
7. `SELECT e.employee_id, d.avg_salary FROM employees e LEFT JOIN (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) d ON e.department_id = d.department_id;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d LEFT JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name HAVING COUNT(e.employee_id) > 0;`
9. `SELECT e.employee_id, d.department_name, e.salary * 1.1 AS new_salary FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id;`
10. `SELECT e.employee_id, d.department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id WHERE e.hire_date > '2024-01-01';`

#### RIGHT Questions
1. How do you get all departments with their employees?
2. How can you filter RIGHT JOIN results?
3. How do you use RIGHT JOIN with a condition?
4. How can you join with multiple tables using RIGHT JOIN?
5. How do you use RIGHT JOIN with GROUP BY?
6. How can you order RIGHT JOIN results?
7. How do you use RIGHT JOIN with a subquery?
8. How can you filter with HAVING after RIGHT JOIN?
9. How do you join with a calculated column using RIGHT JOIN?
10. How can you use RIGHT JOIN with a date condition?

#### RIGHT Answers
1. `SELECT d.department_name, e.employee_id FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id;`
2. `SELECT d.location, e.name FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id WHERE d.location IS NOT NULL;`
3. `SELECT d.department_name, e.employee_id FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id WHERE e.salary > 50000;`
4. `SELECT d.department_name, e.employee_id, m.manager_name FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id RIGHT JOIN managers m ON e.manager_id = m.manager_id;`
5. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
6. `SELECT d.department_name, e.employee_id FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id ORDER BY d.department_name;`
7. `SELECT d.department_name, e.avg_salary FROM departments d RIGHT JOIN (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) e ON d.department_id = e.department_id;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name HAVING COUNT(e.employee_id) > 0;`
9. `SELECT d.department_name, e.employee_id, e.salary * 1.1 AS new_salary FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id;`
10. `SELECT d.department_name, e.employee_id FROM departments d RIGHT JOIN employees e ON d.department_id = e.department_id WHERE e.hire_date > '2024-01-01';`

#### FULL Questions
1. How do you get all employees and departments, including unmatched rows?
2. How can you filter FULL JOIN results?
3. How do you use FULL JOIN with a condition?
4. How can you join with multiple tables using FULL JOIN?
5. How do you use FULL JOIN with GROUP BY?
6. How can you order FULL JOIN results?
7. How do you use FULL JOIN with a subquery?
8. How can you filter with HAVING after FULL JOIN?
9. How do you join with a calculated column using FULL JOIN?
10. How can you use FULL JOIN with a date condition?

#### FULL Answers
1. `SELECT e.employee_id, d.department_name FROM employees e FULL JOIN departments d ON e.department_id = d.department_id;`
2. `SELECT e.name, d.location FROM employees e FULL JOIN departments d ON e.department_id = d.department_id WHERE d.location IS NOT NULL;`
3. `SELECT e.employee_id, d.department_name FROM employees e FULL JOIN departments d ON e.department_id = d.department_id WHERE e.salary > 50000;`
4. `SELECT e.employee_id, d.department_name, m.manager_name FROM employees e FULL JOIN departments d ON e.department_id = d.department_id FULL JOIN managers m ON e.manager_id = m.manager_id;`
5. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d FULL JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
6. `SELECT e.employee_id, d.department_name FROM employees e FULL JOIN departments d ON e.department_id = d.department_id ORDER BY d.department_name;`
7. `SELECT e.employee_id, d.avg_salary FROM employees e FULL JOIN (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) d ON e.department_id = d.department_id;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d FULL JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name HAVING COUNT(e.employee_id) > 0;`
9. `SELECT e.employee_id, d.department_name, e.salary * 1.1 AS new_salary FROM employees e FULL JOIN departments d ON e.department_id = d.department_id;`
10. `SELECT e.employee_id, d.department_name FROM employees e FULL JOIN departments d ON e.department_id = d.department_id WHERE e.hire_date > '2024-01-01';`

---

### COUNT, SUM, AVG, MIN, MAX

#### COUNT Questions
1. How do you count all employees in the table?
2. How can you count employees per department?
3. How do you count non-NULL salaries?
4. How can you count orders by customer?
5. How do you count distinct product IDs?
6. How can you count with a WHERE clause?
7. How do you count rows with a specific condition?
8. How can you count with a JOIN?
9. How do you count with HAVING?
10. How can you count with a subquery?

#### COUNT Answers
1. `SELECT COUNT(*) FROM employees;`
2. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;`
3. `SELECT COUNT(salary) FROM employees;`
4. `SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;`
5. `SELECT COUNT(DISTINCT product_id) FROM sales;`
6. `SELECT COUNT(*) FROM employees WHERE hire_date > '2024-01-01';`
7. `SELECT COUNT(*) FROM sales WHERE sale_amount > 1000;`
8. `SELECT d.department_name, COUNT(e.employee_id) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
9. `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > 5;`
10. `SELECT COUNT(*) FROM (SELECT * FROM employees WHERE salary > 50000) AS high_paid;`

#### SUM Questions
1. How do you calculate the total salary of all employees?
2. How can you sum sales per region?
3. How do you sum with a WHERE clause?
4. How can you sum with a JOIN?
5. How do you sum with HAVING?
6. How can you sum distinct values?
7. How do you sum with a calculated column?
8. How can you sum with a date range?
9. How do you sum with a subquery?
10. How can you sum with ORDER BY?

#### SUM Answers
1. `SELECT SUM(salary) FROM employees;`
2. `SELECT region, SUM(sale_amount) FROM sales GROUP BY region;`
3. `SELECT SUM(sale_amount) FROM sales WHERE sale_date = '2025-06-25';`
4. `SELECT d.department_name, SUM(e.salary) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
5. `SELECT region, SUM(sale_amount) FROM sales GROUP BY region HAVING SUM(sale_amount) > 10000;`
6. `SELECT SUM(DISTINCT sale_amount) FROM sales;`
7. `SELECT SUM(salary * 1.1) AS total_increase FROM employees;`
8. `SELECT SUM(sale_amount) FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`
9. `SELECT SUM(total) FROM (SELECT customer_id, SUM(sale_amount) AS total FROM sales GROUP BY customer_id) AS customer_totals;`
10. `SELECT product_id, SUM(sale_amount) FROM sales GROUP BY product_id ORDER BY SUM(sale_amount) DESC;`

#### AVG Questions
1. How do you calculate the average salary of employees?
2. How can you average sales per region?
3. How do you average with a WHERE clause?
4. How can you average with a JOIN?
5. How do you average with HAVING?
6. How can you average distinct values?
7. How do you average with a calculated column?
8. How can you average with a date range?
9. How do you average with a subquery?
10. How can you average with ORDER BY?

#### AVG Answers
1. `SELECT AVG(salary) FROM employees;`
2. `SELECT region, AVG(sale_amount) FROM sales GROUP BY region;`
3. `SELECT AVG(sale_amount) FROM sales WHERE sale_date = '2025-06-25';`
4. `SELECT d.department_name, AVG(e.salary) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
5. `SELECT department_id, AVG(salary) FROM employees GROUP BY department_id HAVING AVG(salary) > 60000;`
6. `SELECT AVG(DISTINCT sale_amount) FROM sales;`
7. `SELECT AVG(salary * 1.1) AS avg_increase FROM employees;`
8. `SELECT AVG(sale_amount) FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`
9. `SELECT AVG(total) FROM (SELECT customer_id, AVG(sale_amount) AS total FROM sales GROUP BY customer_id) AS customer_avgs;`
10. `SELECT product_id, AVG(sale_amount) FROM sales GROUP BY product_id ORDER BY AVG(sale_amount) DESC;`

#### MIN Questions
1. How do you find the minimum salary among employees?
2. How can you find the earliest sale date per region?
3. How do you find the minimum with a WHERE clause?
4. How can you find the minimum with a JOIN?
5. How do you find the minimum with HAVING?
6. How can you find the minimum distinct value?
7. How do you find the minimum with a calculated column?
8. How can you find the minimum with a date range?
9. How do you find the minimum with a subquery?
10. How can you find the minimum with ORDER BY?

#### MIN Answers
1. `SELECT MIN(salary) FROM employees;`
2. `SELECT region, MIN(sale_date) FROM sales GROUP BY region;`
3. `SELECT MIN(sale_amount) FROM sales WHERE sale_date = '2025-06-25';`
4. `SELECT d.department_name, MIN(e.salary) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
5. `SELECT product_id, MIN(sale_amount) FROM sales GROUP BY product_id HAVING MIN(sale_amount) > 100;`
6. `SELECT MIN(DISTINCT sale_amount) FROM sales;`
7. `SELECT MIN(salary * 1.1) AS min_increase FROM employees;`
8. `SELECT MIN(sale_amount) FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`
9. `SELECT MIN(total) FROM (SELECT customer_id, MIN(sale_amount) AS total FROM sales GROUP BY customer_id) AS customer_mins;`
10. `SELECT product_id, MIN(sale_amount) FROM sales GROUP BY product_id ORDER BY MIN(sale_amount);`

#### MAX Questions
1. How do you find the maximum salary among employees?
2. How can you find the latest sale date per region?
3. How do you find the maximum with a WHERE clause?
4. How can you find the maximum with a JOIN?
5. How do you find the maximum with HAVING?
6. How can you find the maximum distinct value?
7. How do you find the maximum with a calculated column?
8. How can you find the maximum with a date range?
9. How do you find the maximum with a subquery?
10. How can you find the maximum with ORDER BY?

#### MAX Answers
1. `SELECT MAX(salary) FROM employees;`
2. `SELECT region, MAX(sale_date) FROM sales GROUP BY region;`
3. `SELECT MAX(sale_amount) FROM sales WHERE sale_date = '2025-06-25';`
4. `SELECT d.department_name, MAX(e.salary) FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
5. `SELECT product_id, MAX(sale_amount) FROM sales GROUP BY product_id HAVING MAX(sale_amount) > 1000;`
6. `SELECT MAX(DISTINCT sale_amount) FROM sales;`
7. `SELECT MAX(salary * 1.1) AS max_increase FROM employees;`
8. `SELECT MAX(sale_amount) FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`
9. `SELECT MAX(total) FROM (SELECT customer_id, MAX(sale_amount) AS total FROM sales GROUP BY customer_id) AS customer_maxs;`
10. `SELECT product_id, MAX(sale_amount) FROM sales GROUP BY product_id ORDER BY MAX(sale_amount) DESC;`

---

### ROW_NUMBER, RANK, LAG, LEAD

#### ROW_NUMBER Questions
1. How do you assign a row number to employees by salary?
2. How can you partition row numbers by department?
3. How do you use ROW_NUMBER with a WHERE clause?
4. How can you limit rows using ROW_NUMBER?
5. How do you order by row number?
6. How can you use ROW_NUMBER with a JOIN?
7. How do you use ROW_NUMBER with a subquery?
8. How can you use ROW_NUMBER with HAVING?
9. How do you use ROW_NUMBER with a calculated column?
10. How can you use ROW_NUMBER with a date?

#### ROW_NUMBER Answers
1. `SELECT employee_id, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num FROM employees;`
2. `SELECT employee_id, department_id, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS row_num FROM employees;`
3. `SELECT employee_id, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num FROM employees WHERE department_id = 10;`
4. `SELECT * FROM (SELECT employee_id, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num FROM employees) t WHERE row_num <= 5;`
5. `SELECT employee_id, salary, ROW_NUMBER() OVER (ORDER BY hire_date) AS row_num FROM employees ORDER BY row_num;`
6. `SELECT e.employee_id, d.department_name, ROW_NUMBER() OVER (ORDER BY e.salary DESC) AS row_num FROM employees e JOIN departments d ON e.department_id = d.department_id;`
7. `SELECT * FROM (SELECT employee_id, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num FROM employees) t WHERE row_num = 1;`
8. `SELECT department_id, MAX(row_num) FROM (SELECT department_id, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary) AS row_num FROM employees) t GROUP BY department_id HAVING MAX(row_num) > 5;`
9. `SELECT employee_id, salary * 1.1 AS new_salary, ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num FROM employees;`
10. `SELECT employee_id, hire_date, ROW_NUMBER() OVER (ORDER BY hire_date) AS row_num FROM employees;`

#### RANK Questions
1. How do you rank employees by salary?
2. How can you rank within departments?
3. How do you use RANK with a WHERE clause?
4. How can you limit top ranks?
5. How do you order by rank?
6. How can you use RANK with a JOIN?
7. How do you use RANK with a subquery?
8. How can you use RANK with HAVING?
9. How do you use RANK with a calculated column?
10. How can you use RANK with a date?

#### RANK Answers
1. `SELECT employee_id, salary, RANK() OVER (ORDER BY salary DESC) AS rank_num FROM employees;`
2. `SELECT employee_id, department_id, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_num FROM employees;`
3. `SELECT employee_id, salary, RANK() OVER (ORDER BY salary DESC) AS rank_num FROM employees WHERE department_id = 10;`
4. `SELECT * FROM (SELECT employee_id, salary, RANK() OVER (ORDER BY salary DESC) AS rank_num FROM employees) t WHERE rank_num <= 3;`
5. `SELECT employee_id, salary, RANK() OVER (ORDER BY hire_date) AS rank_num FROM employees ORDER BY rank_num;`
6. `SELECT e.employee_id, d.department_name, RANK() OVER (ORDER BY e.salary DESC) AS rank_num FROM employees e JOIN departments d ON e.department_id = d.department_id;`
7. `SELECT * FROM (SELECT employee_id, salary, RANK() OVER (ORDER BY salary DESC) AS rank_num FROM employees) t WHERE rank_num = 1;`
8. `SELECT department_id, MAX(rank_num) FROM (SELECT department_id, RANK() OVER (PARTITION BY department_id ORDER BY salary) AS rank_num FROM employees) t GROUP BY department_id HAVING MAX(rank_num) > 5;`
9. `SELECT employee_id, salary * 1.1 AS new_salary, RANK() OVER (ORDER BY salary DESC) AS rank_num FROM employees;`
10. `SELECT employee_id, hire_date, RANK() OVER (ORDER BY hire_date) AS rank_num FROM employees;`

#### LAG Questions
1. How do you get the previous sale amount?
2. How can you partition LAG by region?
3. How do you use LAG with a WHERE clause?
4. How can you calculate the difference with LAG?
5. How do you order by LAG result?
6. How can you use LAG with a JOIN?
7. How do you use LAG with a subquery?
8. How can you use LAG with HAVING?
9. How do you use LAG with a calculated column?
10. How can you use LAG with a date range?

#### LAG Answers
1. `SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount FROM sales;`
2. `SELECT sale_date, region, sale_amount, LAG(sale_amount) OVER (PARTITION BY region ORDER BY sale_date) AS prev_amount FROM sales;`
3. `SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount FROM sales WHERE region = 'West';`
4. `SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount, sale_amount - LAG(sale_amount) OVER (ORDER BY sale_date) AS diff FROM sales;`
5. `SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount FROM sales ORDER BY prev_amount;`
6. `SELECT s.sale_date, s.sale_amount, LAG(s.sale_amount) OVER (ORDER BY s.sale_date) AS prev_amount FROM sales s JOIN products p ON s.product_id = p.product_id;`
7. `SELECT * FROM (SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount FROM sales) t WHERE prev_amount IS NOT NULL;`
8. `SELECT product_id, MAX(diff) FROM (SELECT product_id, sale_amount, LAG(sale_amount) OVER (PARTITION BY product_id ORDER BY sale_date) AS prev_amount, sale_amount - LAG(sale_amount) OVER (PARTITION BY product_id ORDER BY sale_date) AS diff FROM sales) t GROUP BY product_id HAVING MAX(diff) > 100;`
9. `SELECT sale_date, sale_amount * 1.1 AS adj_amount, LAG(sale_amount * 1.1) OVER (ORDER BY sale_date) AS prev_adj FROM sales;`
10. `SELECT sale_date, sale_amount, LAG(sale_amount) OVER (ORDER BY sale_date) AS prev_amount FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

#### LEAD Questions
1. How do you get the next sale amount?
2. How can you partition LEAD by region?
3. How do you use LEAD with a WHERE clause?
4. How can you calculate the difference with LEAD?
5. How do you order by LEAD result?
6. How can you use LEAD with a JOIN?
7. How do you use LEAD with a subquery?
8. How can you use LEAD with HAVING?
9. How do you use LEAD with a calculated column?
10. How can you use LEAD with a date range?

#### LEAD Answers
1. `SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount FROM sales;`
2. `SELECT sale_date, region, sale_amount, LEAD(sale_amount) OVER (PARTITION BY region ORDER BY sale_date) AS next_amount FROM sales;`
3. `SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount FROM sales WHERE region = 'West';`
4. `SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) - sale_amount AS diff FROM sales;`
5. `SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount FROM sales ORDER BY next_amount;`
6. `SELECT s.sale_date, s.sale_amount, LEAD(s.sale_amount) OVER (ORDER BY s.sale_date) AS next_amount FROM sales s JOIN products p ON s.product_id = p.product_id;`
7. `SELECT * FROM (SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount FROM sales) t WHERE next_amount IS NOT NULL;`
8. `SELECT product_id, MAX(diff) FROM (SELECT product_id, sale_amount, LEAD(sale_amount) OVER (PARTITION BY product_id ORDER BY sale_date) AS next_amount, LEAD(sale_amount) OVER (PARTITION BY product_id ORDER BY sale_date) - sale_amount AS diff FROM sales) t GROUP BY product_id HAVING MAX(diff) > 100;`
9. `SELECT sale_date, sale_amount * 1.1 AS adj_amount, LEAD(sale_amount * 1.1) OVER (ORDER BY sale_date) AS next_adj FROM sales;`
10. `SELECT sale_date, sale_amount, LEAD(sale_amount) OVER (ORDER BY sale_date) AS next_amount FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

---

### CASE, COALESCE

#### CASE Questions
1. How do you categorize salaries as 'High' or 'Low'?
2. How can you assign status based on hire date?
3. How do you use CASE with multiple conditions?
4. How can you use CASE with a JOIN?
5. How do you use CASE with GROUP BY?
6. How can you use CASE with a WHERE clause?
7. How do you use CASE with ORDER BY?
8. How can you use CASE with a subquery?
9. How do you use CASE with HAVING?
10. How can you use CASE with a calculated column?

#### CASE Answers
1. `SELECT employee_id, CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END AS salary_level FROM employees;`
2. `SELECT employee_id, CASE WHEN hire_date < '2024-01-01' THEN 'Senior' ELSE 'Junior' END AS status FROM employees;`
3. `SELECT employee_id, CASE WHEN salary > 70000 THEN 'Senior' WHEN salary > 50000 THEN 'Mid' ELSE 'Junior' END AS level FROM employees;`
4. `SELECT e.employee_id, CASE WHEN d.location = 'Pune' THEN 'Local' ELSE 'Remote' END AS location_type FROM employees e JOIN departments d ON e.department_id = d.department_id;`
5. `SELECT CASE WHEN AVG(salary) > 60000 THEN 'High Pay' ELSE 'Low Pay' END AS pay_level, COUNT(*) FROM employees GROUP BY CASE WHEN AVG(salary) > 60000 THEN 'High Pay' ELSE 'Low Pay' END;`
6. `SELECT employee_id, CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END AS salary_level FROM employees WHERE department_id = 10;`
7. `SELECT employee_id, CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END AS salary_level FROM employees ORDER BY CASE WHEN salary > 50000 THEN 'High' ELSE 'Low' END;`
8. `SELECT employee_id, CASE WHEN salary > (SELECT AVG(salary) FROM employees) THEN 'Above Avg' ELSE 'Below Avg' END AS status FROM employees;`
9. `SELECT department_id, CASE WHEN AVG(salary) > 60000 THEN 'High Pay' ELSE 'Low Pay' END AS pay_level FROM employees GROUP BY department_id HAVING AVG(salary) > 50000;`
10. `SELECT employee_id, CASE WHEN salary * 1.1 > 55000 THEN 'High' ELSE 'Low' END AS new_level FROM employees;`

#### COALESCE Questions
1. How do you replace NULL manager_ids with employee_id?
2. How can you handle NULL order dates?
3. How do you use COALESCE with a JOIN?
4. How can you sum with COALESCE for NULL values?
5. How do you use COALESCE with a WHERE clause?
6. How can you use COALESCE with GROUP BY?
7. How do you use COALESCE with ORDER BY?
8. How can you use COALESCE with a subquery?
9. How do you use COALESCE with HAVING?
10. How can you use COALESCE with a calculated column?

#### COALESCE Answers
1. `SELECT COALESCE(manager_id, employee_id) AS responsible_id FROM employees;`
2. `SELECT COALESCE(order_date, '1900-01-01') AS effective_date FROM orders;`
3. `SELECT e.employee_id, COALESCE(m.manager_name, 'No Manager') FROM employees e LEFT JOIN managers m ON e.manager_id = m.manager_id;`
4. `SELECT SUM(COALESCE(bonus, 0)) AS total_bonus FROM employees;`
5. `SELECT employee_id, COALESCE(bonus, 0) AS bonus_amount FROM employees WHERE COALESCE(bonus, 0) > 1000;`
6. `SELECT department_id, SUM(COALESCE(salary, 0)) FROM employees GROUP BY department_id;`
7. `SELECT employee_id, COALESCE(salary, 0) AS effective_salary FROM employees ORDER BY effective_salary DESC;`
8. `SELECT employee_id, COALESCE((SELECT avg_salary FROM (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) t WHERE t.department_id = e.department_id), 0) AS dept_avg FROM employees e;`
9. `SELECT department_id, SUM(COALESCE(bonus, 0)) AS total_bonus FROM employees GROUP BY department_id HAVING SUM(COALESCE(bonus, 0)) > 5000;`
10. `SELECT employee_id, COALESCE(salary * 1.1, 0) AS adjusted_salary FROM employees;`

---

### PIVOT, UNPIVOT, EXPLAIN

#### PIVOT Questions
1. How do you pivot sale amounts by date?
2. How can you pivot with a WHERE clause?
3. How do you pivot with multiple aggregates?
4. How can you pivot with a JOIN?
5. How do you pivot with GROUP BY?
6. How can you order pivot results?
7. How do you pivot with a subquery?
8. How can you use HAVING with PIVOT?
9. How do you pivot with a calculated column?
10. How can you pivot with a date range?

#### PIVOT Answers
1. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales) AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
2. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales WHERE region = 'West') AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
3. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales) AS Source PIVOT (MAX(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
4. `SELECT * FROM (SELECT p.product_name, s.sale_date, s.sale_amount FROM sales s JOIN products p ON s.product_id = p.product_id) AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
5. `SELECT * FROM (SELECT department_id, hire_date, salary FROM employees GROUP BY department_id, hire_date, salary) AS Source PIVOT (AVG(salary) FOR hire_date IN ('2024-01-01', '2024-02-01')) AS PivotTable;`
6. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales) AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable ORDER BY product_id;`
7. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM (SELECT * FROM sales WHERE sale_amount > 100) s) AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
8. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales GROUP BY product_id, sale_date, sale_amount) AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable HAVING SUM(sale_amount) > 1000;`
9. `SELECT * FROM (SELECT product_id, sale_date, sale_amount * 1.1 AS adj_amount FROM sales) AS Source PIVOT (SUM(adj_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`
10. `SELECT * FROM (SELECT product_id, sale_date, sale_amount FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30') AS Source PIVOT (SUM(sale_amount) FOR sale_date IN ('2025-06-25', '2025-06-26')) AS PivotTable;`

#### UNPIVOT Questions
1. How do you unpivot sales data by date columns?
2. How can you unpivot with a WHERE clause?
3. How do you unpivot with a JOIN?
4. How can you order unpivot results?
5. How do you unpivot with a subquery?
6. How can you use GROUP BY with UNPIVOT?
7. How do you unpivot with a WHERE clause after?
8. How can you use HAVING with UNPIVOT?
9. How do you unpivot with a calculated column?
10. How can you unpivot with a date range?

#### UNPIVOT Answers
1. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales) AS p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt;`
2. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales WHERE region = 'West') p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt;`
3. `SELECT u.product_id, u.sale_date, u.sale_amount FROM (SELECT p.product_name, '2025-06-25' AS d1, '2025-06-26' AS d2 FROM sales s JOIN products p ON s.product_id = p.product_id) p UNPIVOT (sale_amount FOR sale_date IN (d1, d2)) AS u;`
4. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales) p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt ORDER BY product_id;`
5. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS d1, '2025-06-26' AS d2 FROM (SELECT * FROM sales WHERE sale_amount > 100) s) p UNPIVOT (sale_amount FOR sale_date IN (d1, d2)) AS unpvt;`
6. `SELECT sale_date, SUM(sale_amount) FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales) p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt GROUP BY sale_date;`
7. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS d1, '2025-06-26' AS d2 FROM sales) p UNPIVOT (sale_amount FOR sale_date IN (d1, d2)) AS unpvt WHERE sale_amount > 100;`
8. `SELECT sale_date, SUM(sale_amount) FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales) p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt GROUP BY sale_date HAVING SUM(sale_amount) > 500;`
9. `SELECT product_id, sale_date, sale_amount * 1.1 AS adj_amount FROM (SELECT product_id, '2025-06-25' AS sale_date_1, '2025-06-26' AS sale_date_2 FROM sales) p UNPIVOT (sale_amount FOR sale_date IN (sale_date_1, sale_date_2)) AS unpvt;`
10. `SELECT product_id, sale_date, sale_amount FROM (SELECT product_id, '2025-06-25' AS d1, '2025-06-26' AS d2 FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30') p UNPIVOT (sale_amount FOR sale_date IN (d1, d2)) AS unpvt;`

#### EXPLAIN Questions
1. How do you analyze the execution plan for a simple query?
2. How can you explain a query with a WHERE clause?
3. How do you explain a query with a JOIN?
4. How can you explain a query with ORDER BY?
5. How do you explain a query with GROUP BY?
6. How can you explain a query with a subquery?
7. How do you explain a query with HAVING?
8. How can you explain a query with multiple joins?
9. How do you explain a query with a calculated column?
10. How can you explain a query with a date range?

#### EXPLAIN Answers
1. `EXPLAIN SELECT * FROM employees;`
2. `EXPLAIN SELECT * FROM employees WHERE department_id = 10;`
3. `EXPLAIN SELECT e.employee_id, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id;`
4. `EXPLAIN SELECT * FROM sales ORDER BY sale_date;`
5. `EXPLAIN SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;`
6. `EXPLAIN SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);`
7. `EXPLAIN SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > 5;`
8. `EXPLAIN SELECT e.employee_id, d.department_name, m.manager_name FROM employees e JOIN departments d ON e.department_id = d.department_id JOIN managers m ON e.manager_id = m.manager_id;`
9. `EXPLAIN SELECT employee_id, salary * 1.1 AS new_salary FROM employees;`
10. `EXPLAIN SELECT * FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

---

### WITH, OVER, PARTITION BY

#### WITH Questions
1. How do you use a CTE to calculate total salary per employee?
2. How can you use WITH with a JOIN?
3. How do you use WITH with a WHERE clause?
4. How can you use WITH with GROUP BY?
5. How do you use WITH with HAVING?
6. How can you use WITH with ORDER BY?
7. How do you use WITH with a subquery?
8. How can you use WITH with multiple CTEs?
9. How do you use WITH with a calculated column?
10. How can you use WITH with a date range?

#### WITH Answers
1. `WITH cte AS (SELECT employee_id, SUM(salary) AS total_salary FROM employees GROUP BY employee_id) SELECT * FROM cte;`
2. `WITH cte AS (SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id) SELECT e.employee_id, c.avg_salary FROM employees e JOIN cte c ON e.department_id = c.department_id;`
3. `WITH cte AS (SELECT employee_id, salary FROM employees WHERE hire_date > '2024-01-01') SELECT * FROM cte;`
4. `WITH cte AS (SELECT department_id, SUM(salary) AS total_salary FROM employees GROUP BY department_id) SELECT * FROM cte;`
5. `WITH cte AS (SELECT product_id, SUM(sale_amount) AS total_sales FROM sales GROUP BY product_id) SELECT product_id, total_sales FROM cte HAVING total_sales > 5000;`
6. `WITH cte AS (SELECT employee_id, salary FROM employees) SELECT * FROM cte ORDER BY salary DESC;`
7. `WITH cte AS (SELECT * FROM (SELECT employee_id, salary FROM employees WHERE salary > 50000) t) SELECT * FROM cte;`
8. `WITH cte1 AS (SELECT department_id FROM employees), cte2 AS (SELECT department_id, AVG(salary) FROM employees GROUP BY department_id) SELECT * FROM cte1 JOIN cte2 ON cte1.department_id = cte2.department_id;`
9. `WITH cte AS (SELECT employee_id, salary * 1.1 AS new_salary FROM employees) SELECT * FROM cte;`
10. `WITH cte AS (SELECT sale_date, SUM(sale_amount) FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30' GROUP BY sale_date) SELECT * FROM cte;`

#### OVER Questions
1. How do you calculate a running total of salaries?
2. How can you use OVER with a WHERE clause?
3. How do you use OVER with a JOIN?
4. How can you use OVER with GROUP BY?
5. How do you use OVER with HAVING?
6. How can you use OVER with ORDER BY?
7. How do you use OVER with a subquery?
8. How can you use OVER with multiple windows?
9. How do you use OVER with a calculated column?
10. How can you use OVER with a date range?

#### OVER Answers
1. `SELECT employee_id, salary, SUM(salary) OVER (ORDER BY hire_date) AS running_total FROM employees;`
2. `SELECT employee_id, salary, SUM(salary) OVER (ORDER BY hire_date) AS running_total FROM employees WHERE department_id = 10;`
3. `SELECT e.employee_id, d.department_name, SUM(e.salary) OVER () AS total_salary FROM employees e JOIN departments d ON e.department_id = d.department_id;`
4. `SELECT department_id, salary, SUM(salary) OVER () AS total_salary FROM employees GROUP BY department_id, salary;`
5. `SELECT department_id, SUM(salary) OVER () AS total_salary FROM employees GROUP BY department_id HAVING SUM(salary) > 100000;`
6. `SELECT employee_id, sale_date, SUM(sale_amount) OVER (ORDER BY sale_date) AS running_total FROM sales ORDER BY sale_date;`
7. `SELECT * FROM (SELECT employee_id, salary, SUM(salary) OVER () AS total_salary FROM employees) t WHERE total_salary > 500000;`
8. `SELECT employee_id, salary, SUM(salary) OVER (ORDER BY hire_date) AS running_total, AVG(salary) OVER () AS avg_salary FROM employees;`
9. `SELECT employee_id, salary * 1.1 AS new_salary, SUM(salary * 1.1) OVER () AS total_new_salary FROM employees;`
10. `SELECT sale_date, sale_amount, SUM(sale_amount) OVER (ORDER BY sale_date) AS running_total FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

#### PARTITION BY Questions
1. How do you rank employees within each department?
2. How can you partition by region for sales totals?
3. How do you use PARTITION BY with a WHERE clause?
4. How can you partition with a JOIN?
5. How do you use PARTITION BY with GROUP BY?
6. How can you use PARTITION BY with HAVING?
7. How do you use PARTITION BY with ORDER BY?
8. How can you use PARTITION BY with a subquery?
9. How do you use PARTITION BY with a calculated column?
10. How can you use PARTITION BY with a date range?

#### PARTITION BY Answers
1. `SELECT employee_id, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_in_dept FROM employees;`
2. `SELECT sale_date, region, sale_amount, SUM(sale_amount) OVER (PARTITION BY region ORDER BY sale_date) AS running_total FROM sales;`
3. `SELECT employee_id, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_in_dept FROM employees WHERE hire_date > '2024-01-01';`
4. `SELECT e.employee_id, d.department_name, RANK() OVER (PARTITION BY d.department_name ORDER BY e.salary DESC) AS rank_salary FROM employees e JOIN departments d ON e.department_id = d.department_id;`
5. `SELECT department_id, AVG(salary) AS dept_avg, RANK() OVER (PARTITION BY department_id ORDER BY AVG(salary) DESC) AS rank_dept FROM employees GROUP BY department_id;`
6. `SELECT department_id, MAX(rank_num) FROM (SELECT department_id, RANK() OVER (PARTITION BY department_id ORDER BY salary) AS rank_num FROM employees) t GROUP BY department_id HAVING MAX(rank_num) > 5;`
7. `SELECT employee_id, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_in_dept FROM employees ORDER BY department_id;`
8. `SELECT * FROM (SELECT employee_id, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank_in_dept FROM employees) t WHERE rank_in_dept = 1;`
9. `SELECT employee_id, department_id, salary * 1.1 AS new_salary, RANK() OVER (PARTITION BY department_id ORDER BY salary * 1.1 DESC) AS rank_in_dept FROM employees;`
10. `SELECT sale_date, region, sale_amount, SUM(sale_amount) OVER (PARTITION BY region ORDER BY sale_date) AS running_total FROM sales WHERE sale_date BETWEEN '2025-06-01' AND '2025-06-30';`

---

### STRING_AGG, JSON_QUERY, TRY_CAST

#### STRING_AGG Questions
1. How do you concatenate employee names by department?
2. How can you use STRING_AGG with a WHERE clause?
3. How do you use STRING_AGG with a JOIN?
4. How can you order STRING_AGG results?
5. How do you use STRING_AGG with GROUP BY?
6. How can you use STRING_AGG with HAVING?
7. How do you use STRING_AGG with a subquery?
8. How can you use STRING_AGG with a calculated column?
9. How do you use STRING_AGG with ORDER BY?
10. How can you use STRING_AGG with a date range?

#### STRING_AGG Answers
1. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM employees GROUP BY department_id;`
2. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM employees WHERE hire_date > '2024-01-01' GROUP BY department_id;`
3. `SELECT d.department_name, STRING_AGG(e.employee_name, '; ') AS employee_list FROM departments d JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name;`
4. `SELECT department_id, STRING_AGG(employee_name, ', ') WITHIN GROUP (ORDER BY employee_name) AS employee_list FROM employees GROUP BY department_id;`
5. `SELECT region, STRING_AGG(city, '; ') AS city_list FROM locations GROUP BY region;`
6. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM employees GROUP BY department_id HAVING COUNT(*) > 5;`
7. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM (SELECT * FROM employees WHERE salary > 50000) e GROUP BY department_id;`
8. `SELECT department_id, STRING_AGG(CONCAT(employee_name, ' (', salary, ')'), ', ') AS employee_list FROM employees GROUP BY department_id;`
9. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM employees GROUP BY department_id ORDER BY department_id;`
10. `SELECT department_id, STRING_AGG(employee_name, ', ') AS employee_list FROM employees WHERE hire_date BETWEEN '2024-01-01' AND '2025-06-25' GROUP BY department_id;`

#### JSON_QUERY Questions
1. How do you extract the 'details' field from a JSON column?
2. How can you use JSON_QUERY with a WHERE clause?
3. How do you use JSON_QUERY with a JOIN?
4. How can you order JSON_QUERY results?
5. How do you use JSON_QUERY with GROUP BY?
6. How can you use JSON_QUERY with HAVING?
7. How do you use JSON_QUERY with a subquery?
8. How can you use JSON_QUERY with a calculated column?
9. How do you use JSON_QUERY with ORDER BY?
10. How can you use JSON_QUERY with a date condition?

#### JSON_QUERY Answers
1. `SELECT JSON_QUERY(data, '$.details') AS details FROM json_table WHERE id = 1;`
2. `SELECT JSON_QUERY(data, '$.contact') AS contact_info FROM json_table WHERE JSON_QUERY(data, '$.status') = '"active"';`
3. `SELECT j.data, JSON_QUERY(j.data, '$.address') AS address FROM json_table j JOIN employees e ON j.id = e.employee_id;`
4. `SELECT JSON_QUERY(data, '$.name') AS name FROM json_table ORDER BY JSON_QUERY(data, '$.name');`
5. `SELECT JSON_QUERY(data, '$.category') AS category, COUNT(*) FROM json_table GROUP BY JSON_QUERY(data, '$.category');`
6. `SELECT JSON_QUERY(data, '$.category') AS category, COUNT(*) FROM json_table GROUP BY JSON_QUERY(data, '$.category') HAVING COUNT(*) > 2;`
7. `SELECT * FROM (SELECT id, JSON_QUERY(data, '$.details') AS details FROM json_table WHERE id > 0) t WHERE details IS NOT NULL;`
8. `SELECT id, JSON_QUERY(data, '$.name') AS name, LENGTH(JSON_QUERY(data, '$.name')) AS name_length FROM json_table;`
9. `SELECT id, JSON_QUERY(data, '$.name') AS name FROM json_table ORDER BY JSON_QUERY(data, '$.name');`
10. `SELECT JSON_QUERY(data, '$.details') AS details FROM json_table WHERE CAST(JSON_QUERY(data, '$.date') AS DATE) = '2025-06-25';`

#### TRY_CAST Questions
1. How do you cast a column to an integer safely?
2. How can you use TRY_CAST with a WHERE clause?
3. How do you use TRY_CAST with a JOIN?
4. How can you order TRY_CAST results?
5. How do you use TRY_CAST with GROUP BY?
6. How can you use TRY_CAST with HAVING?
7. How do you use TRY_CAST with a subquery?
8. How can you use TRY_CAST with a calculated column?
9. How do you use TRY_CAST with ORDER BY?
10. How can you use TRY_CAST with a date?

#### TRY_CAST Answers
1. `SELECT TRY_CAST(column_value AS INT) AS int_value FROM data_table;`
2. `SELECT TRY_CAST(sale_amount AS DECIMAL(10,2)) AS decimal_amount FROM sales WHERE TRY_CAST(sale_amount AS DECIMAL(10,2)) IS NOT NULL;`
3. `SELECT e.employee_id, TRY_CAST(j.data AS INT) AS data_value FROM employees e JOIN json_table j ON e.employee_id = j.id;`
4. `SELECT TRY_CAST(sale_amount AS DECIMAL(10,2)) AS decimal_amount FROM sales ORDER BY decimal_amount DESC;`
5. `SELECT TRY_CAST(sale_amount AS INT) AS int_amount, COUNT(*) FROM sales GROUP BY TRY_CAST(sale_amount AS INT);`
6. `SELECT TRY_CAST(sale_amount AS INT) AS int_amount, COUNT(*) FROM sales GROUP BY TRY_CAST(sale_amount AS INT) HAVING COUNT(*) > 5;`
7. `SELECT * FROM (SELECT employee_id, TRY_CAST(bonus AS DECIMAL(10,2)) AS bonus_value FROM employees) t WHERE bonus_value IS NOT NULL;`
8. `SELECT employee_id, TRY_CAST(salary * 1.1 AS DECIMAL(10,2)) AS new_salary FROM employees;`
9. `SELECT employee_id, TRY_CAST(salary AS DECIMAL(10,2)) AS decimal_salary FROM employees ORDER BY decimal_salary DESC;`
10. `SELECT TRY_CAST(order_date AS DATE) AS valid_date FROM orders WHERE TRY_CAST(order_date AS DATE) IS NOT NULL;`

--- 

