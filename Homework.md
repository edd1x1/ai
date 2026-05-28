
mysql> CREATE TABLE courses (id INT PRIMARY KEY, course_name VARCHAR(100),
    -> price DECIMAL(10,2),
    -> mentor_id INT);
Query OK, 0 rows affected (0.398 sec)

mysql> INSERT INTO courses(id, course_name, price, mentor_id)
    -> VALUES (1, 'Аналитика данных', 15000.00, 100),
    -> (2, 'QA тестировщик', 8200.00, 101),
    -> (3, 'Python для начинающих', 20000.00, 102),
    -> (4, 'SQL тренажер', 3600.00, 103),
    -> (5, 'Fronted разработка', 12800.00, 100),
    -> (8, 'QA тестировщик: Продвинутый уровень', 10200.00, 102),
    -> (10, 'Английский для IT-специалистов', 5000.00, 103),
    -> (20, 'Fullstack-разработчик (Индивидуально)', 50000.00, 100);
Query OK, 8 rows affected (0.139 sec)
Records: 8  Duplicates: 0  Warnings: 0

mysql> with expensive_courses as ( select * from courses where price > 15000) select * from expensive_courses;
+----+---------------------------------------+----------+-----------+
| id | course_name                           | price    | mentor_id |
+----+---------------------------------------+----------+-----------+
|  3 | Python для начинающих                 | 20000.00 |       102 |
| 20 | Fullstack-разработчик (Индивидуально) | 50000.00 |       100 |
+----+---------------------------------------+----------+-----------+
2 rows in set (0.060 sec)

mysql> with avarage_cost as ( select avg(price) as avg_price from courses) select * from avarage_cost;
+--------------+
| avg_price    |
+--------------+
| 15600.000000 |
+--------------+
1 row in set (0.020 sec)

mysql> with max_price as ( select max(price) as maxPrice from courses) select * from max_price;
+----------+
| maxPrice |
+----------+
| 50000.00 |
+----------+
1 row in set (0.024 sec)

mysql> with min_price as ( select min(price) as minPrice from courses) select * from min_price;
+----------+
| minPrice |
+----------+
|  3600.00 |
+----------+
1 row in set (0.016 sec)

mysql> with mentor_courses as ( select * from courses where mentor_id = 101) select * from mentor_courses;
+----+----------------+---------+-----------+
| id | course_name    | price   | mentor_id |
+----+----------------+---------+-----------+
|  2 | QA тестировщик | 8200.00 |       101 |
+----+----------------+---------+-----------+
1 row in set (0.006 sec)
