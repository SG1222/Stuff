# Carbon Data Logger: Viva Preparation Sheet

Likely examiner questions, with short answers based on this project's code.
Function names refer to `carbon_logger.py`.

---

## 1. About the project

**Q1. What does your project do?**
It is a terminal program that records everyday activities such as electricity use, car/bus/train travel, LPG use and flights. It estimates the CO2 produced by each one and stores the records in MySQL. The user can search, update, delete, summarise and export the records.

**Q2. How is the CO2 calculated?**
`CO2 = quantity × emission factor`, done in one function, `calculate_emission()`, and rounded to 2 decimal places. For example, 20 km by car × 0.17 kg/km = 3.40 kg CO2.

**Q3. Are the emission factors real, official values?**
No. They are illustrative values for a school project, and the program says so. They are stored in the `categories` table, so they can be changed from menu 12 without changing the code.

**Q4. Why did you store emission factors in the database instead of the Python code?**
If they were written into the code, changing a factor would mean editing the program. In the database they can be updated with an `UPDATE` query from menu 12, and every calculation reads the latest value from MySQL.

**Q5. If you change an emission factor, do old records change?**
No. Each record stores the CO2 value calculated when it was entered, so it keeps the estimate made at that time. The new factor is used for new records and for records that are edited.

**Q6. Which modules did you use?**
`mysql.connector` for the MySQL connection, `csv` to export records, and `datetime` to check dates and get today's date. Only `mysql-connector-python` needs to be installed; the others come with Python.

---

## 2. Database and SQL

**Q7. How many tables are there, and what are they?**
Two tables in the database `carbon_logger`:
- `categories`: `category_id`, `category_name`, `unit`, `emission_factor`
- `emission_records`: `record_id`, `record_date`, `category_id`, `quantity`, `co2_emission`, `note`

**Q8. What are the degree and cardinality of the `categories` table?**
Degree (number of columns) = 4. Cardinality (number of rows) = 6 with the default categories, and it grows if the user adds more.

**Q9. What is the primary key in each table?**
`category_id` in `categories` and `record_id` in `emission_records`. A primary key uniquely identifies each row and cannot be NULL or repeated.

**Q10. Why did you use a foreign key?**
`category_id` in `emission_records` refers to `category_id` in `categories`. This links the two tables, so a record cannot be saved with a category that doesn't exist. MySQL also refuses to delete a category that still has records.

**Q11. Why not store the category name and unit in every record?**
That would repeat the same data many times, and changing a name would mean updating every record. Instead, each record stores only `category_id`, and the name and unit are fetched with a JOIN.

**Q12. Where did you use a JOIN?**
In `RECORD_QUERY` (used for viewing, searching and exporting) and in the summary queries:
```sql
FROM emission_records r INNER JOIN categories c ON r.category_id = c.category_id
```
`r` and `c` are aliases (short names for the tables). This is an equi-join because it matches rows where the `category_id` values are equal.

**Q13. What does `AUTO_INCREMENT` do?**
MySQL gives each new row the next number automatically (1, 2, 3, ...), so the user never has to type an ID.

**Q14. What constraints did you use?**
`PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL` (the field must have a value) and `UNIQUE` on `category_name` (two categories cannot have the same name).

**Q15. Which data types did you use, and why?**
`INT` for IDs, `VARCHAR(n)` for text such as names, units and notes, `FLOAT` for quantities, factors and CO2 (which have decimals), and `DATE` for the record date, so MySQL can compare dates and use `MONTH()` and `YEAR()`.

**Q16. Name the aggregate functions you used and where.**
- `COUNT()`, `SUM()`, `AVG()`, `MIN()` and `MAX()` in `get_overall_totals()` (menu 6)
- `MIN(record_date)` and `MAX(record_date)` to show the first and last record dates
- `COUNT()` and `SUM()` with `GROUP BY` in `get_category_totals()` (menus 7 and 9)

**Q17. What does `GROUP BY` do in your project?**
It puts all records of the same category into one group, so `COUNT(*)` and `SUM(co2_emission)` give the number of records and the total CO2 for each category.

**Q18. How do you find the highest-emission category?**
`get_category_totals()` groups by category and sorts with `ORDER BY SUM(r.co2_emission) DESC`. The first row is therefore the highest and the last row is the lowest.

**Q19. Where did you use `BETWEEN`, `LIKE` and `DISTINCT`?**
- `BETWEEN`: search between two dates (`search_by_date_range()`)
- `LIKE`: search by category name, where `'%car%'` matches "Car Travel" (`search_by_category()`)
- `DISTINCT`: listing the months that have records (`show_available_months()`)

**Q20. How does the monthly summary pick one month?**
```sql
WHERE MONTH(record_date) = %s AND YEAR(record_date) = %s
```
`MONTH()` and `YEAR()` take the month and year out of a `DATE` value.

**Q21. Which DDL and DML commands does the project use?**
DDL (defines structure): `CREATE DATABASE`, `CREATE TABLE`.
DML (works with data): `INSERT`, `SELECT`, `UPDATE`, `DELETE`.

**Q22. What does `IF NOT EXISTS` do?**
It creates the database or table only if it isn't already there. That's why the program can be run many times without errors.

---

## 3. Python–MySQL connectivity

**Q23. What are the steps to connect Python to MySQL?**
1. `import mysql.connector`
2. `connection = mysql.connector.connect(host=..., user=..., password=...)`
3. `cursor = connection.cursor()`
4. `cursor.execute(query, values)`
5. `connection.commit()` after INSERT, UPDATE or DELETE
6. `cursor.fetchone()` / `cursor.fetchall()` after SELECT
7. `cursor.close()` and `connection.close()` at the end (done in `main()`'s `finally`)

**Q24. What is a cursor?**
An object that sends SQL queries to MySQL and holds the results so Python can read them.

**Q25. What does `commit()` do? What happens without it?**
It permanently saves the changes made by INSERT, UPDATE or DELETE. Without `commit()` the changes are lost when the program closes. SELECT doesn't need `commit()` because it doesn't change data.

**Q26. Difference between `fetchone()` and `fetchall()`?**
`fetchone()` returns one row as a tuple, or `None` if there is no row. It is used where only one row is expected, such as `get_record()` and `get_category()`. `fetchall()` returns all rows as a list of tuples and is used for tables and summaries.

**Q27. Why `%s` instead of joining strings to build the query?**
With `%s`, the connector inserts the values safely. Anything the user types is treated only as data, never as part of the SQL command. This prevents **SQL injection** (a user typing SQL code that changes the query) and also handles quotes in text such as `Mom's car` correctly.
```python
cursor.execute("DELETE FROM emission_records WHERE record_id = %s", (record_id,))
```

**Q28. But `connect_database()` joins strings: `"USE " + DB_NAME`. Why?**
`%s` works only for values, not for names of databases or tables. `DB_NAME` is a fixed constant written in the program, not user input, so joining strings is safe there.

**Q29. Why is there a comma in `(record_id,)`?**
`execute()` needs a tuple of values. `(record_id)` is just a number in brackets; the comma makes it a one-item tuple.

**Q30. What are `rowcount` and `lastrowid`?**
`cursor.rowcount` is the number of rows changed by the last query, shown after a delete. `cursor.lastrowid` is the ID given to the last inserted row, shown after adding a record.

**Q31. `lastrowid` is not in the CBSE syllabus list. Why did you use it?**
The syllabus lists `connect()`, `cursor()`, `execute()`, `commit()`, `fetchone()`, `fetchall()` and `rowcount`. `lastrowid` is a cursor attribute of the same kind as `rowcount`: `rowcount` tells how many rows changed, and `lastrowid` tells the ID of the row just inserted. I need that ID to show it to the user and to push it onto the undo stack. Using only listed features, the same ID could be found with `SELECT MAX(record_id) FROM emission_records` and `fetchone()`, but `lastrowid` is the standard, shorter way.

**Q32. Why does the monthly summary use `cursor.fetchall()[0]` instead of `fetchone()`?**
That query uses `GROUP BY` and can return several rows, one per category. If `fetchone()` reads only the first row, the other rows stay unread, and the next `execute()` can fail with the error "Unread result found". `fetchall()` reads every row, and `[0]` takes the first one, which is the highest category because of `ORDER BY ... DESC`.

**Q33. Why do the summary functions check for zero records first?**
On an empty table `COUNT(*)` gives 0, but `SUM()`, `AVG()`, `MIN()` and `MAX()` give NULL, which Python receives as `None`. Formatting `None` with `"{:.2f}"` raises an error. So each summary checks `if count == 0` (or `if len(rows) == 0`) and shows "No records available yet." before formatting anything.

---

## 4. Python concepts

**Q34. Why did you use so many functions?**
Each function does one job, such as `add_record()`, `search_by_date()` or `export_to_csv()`. This makes the program easier to read, test and explain, and avoids repeating code. For example, `print_records()` is reused by viewing, searching, updating and deleting.

**Q35. Why is the `global` keyword used in `connect_database()`?**
`connection` and `cursor` are created inside the function, but every other function needs them. `global` makes the function change the variables at the top of the file instead of creating new local ones.

**Q36. How does the main menu work?**
`main()` runs a `while True` loop that shows the menu and reads a choice. The dictionary `menu_actions` links each choice ("1", "2", ...) to its function. Choosing "0" uses `break` to leave the loop.

**Q37. Where did you use `try`/`except`/`finally`?**
- `get_integer()` and `get_positive_number()`: catch `ValueError` when the user types letters
- `validate_date()`: catches `ValueError` for impossible dates such as 2026-13-45
- `main()`: catches `mysql.connector.Error` (wrong password, server not running), and `KeyboardInterrupt` (Ctrl+C); its `finally` always closes the cursor and connection
- `add_category()`: catches `IntegrityError` for a duplicate category name
- `export_summary_to_text()`: catches `IOError`; its `finally` always closes the file

**Q38. What is the purpose of `finally`?**
Code in `finally` runs whether or not an error happened. It is used to close files and the database connection, so they are never left open.

**Q39. How do you check that a date is valid?**
`validate_date()` uses `datetime.datetime.strptime(date_text, "%Y-%m-%d")`. If the date doesn't exist (for example, February 30), Python raises `ValueError`, and the function returns `None`.

**Q40. How do you stop negative or text quantities?**
`get_positive_number()` keeps asking in a `while True` loop. `float()` raises `ValueError` for text, and an `if` rejects values that are 0 or less.

**Q41. Why is the note cut with `[:100]`?**
The `note` column is `VARCHAR(100)`. Slicing keeps the first 100 characters, so MySQL never rejects a long note and the record is not lost.

**Q42. What does `x if condition else y` mean in your code?**
It is a short form of `if`/`else` that gives one of two values. For example, `share = float(row[2]) / grand_total * 100 if grand_total > 0 else 0` calculates the percentage only when the total is above zero, which avoids a division by zero. `note = record[6] if record[6] else ""` shows an empty note as blank instead of `None`.

**Q43. Why do you write `MONTH_NAMES[month - 1]`?**
`MONTH_NAMES` is a tuple of 12 names, and tuple indexes start at 0, so "January" is at index 0. Month numbers start at 1, so month `m` is at index `m - 1`. For example, month 9 gives `MONTH_NAMES[8]`, which is "September".

---

## 5. Stack (Undo Last Added Record)

**Q44. Where did you use a stack?**
In menu option 14, Undo Last Added Record. The list `undo_stack` stores the ID of every record added in this session. Option 14 removes the most recently added record first.

**Q45. What is a stack? Why is it the right choice for undo?**
A stack is a LIFO (Last In, First Out) structure: the last item put in is the first one taken out. Undo must always remove the newest action first, then the one before it, which is exactly LIFO.

**Q46. How did you implement the stack?**
With a Python list and two functions:
```python
def push(stack, item):
    stack.append(item)          # add to the top

def pop(stack):
    if len(stack) == 0:         # empty stack (underflow)
        return None
    return stack.pop()          # remove and return the top
```
`add_record()` calls `push(undo_stack, cursor.lastrowid)` after saving. `undo_last_record()` calls `pop(undo_stack)`.

**Q47. What happens if the stack is empty?**
`pop()` checks `len(stack) == 0` and returns `None`, so the program shows "Nothing to undo" instead of crashing. Calling `list.pop()` on an empty list would raise an `IndexError`. This situation is called stack underflow.

**Q48. What if the user says N at the confirmation?**
The ID is pushed back onto the stack, so the record can still be undone later.

**Q49. What if the record was already deleted with option 5?**
`get_record()` returns `None`, so the program shows "Record … was already deleted" and nothing else happens.

**Q50. Why is `global` not needed for `undo_stack`?**
The functions only change the list's contents with `append()` and `pop()`; they never assign a new value to the name `undo_stack`. `global` is needed only when a function assigns to a global name, as `connect_database()` does with `connection` and `cursor`.

**Q51. Does undo work after restarting the program?**
No. The stack is an ordinary list in memory, so it starts empty each time the program runs. Undo is meant for mistakes made in the current session; older records can still be removed with option 5, Delete Record.

---

## 6. File handling

**Q52. How do you export to CSV?**
`export_to_csv()` opens `carbon_records.csv` in write mode with a `with` statement, creates a `csv.writer`, writes the headings with `writerow()`, and writes all records at once with `writerows()`.

**Q53. Why `newline=""` when opening the CSV file?**
Without it, Windows adds an extra blank line between rows in the CSV file.

**Q54. Why `encoding="utf-8"`?**
So symbols like ₹ and Hindi text in notes can be written to the file. Otherwise Windows may raise an error.

**Q55. Difference between the two export functions?**
`export_to_csv()` uses the `csv` module and a `with` clause, which closes the file automatically. `export_summary_to_text()` uses normal text-file handling with `open()`, `write()` and `close()` inside `try`/`finally`. Together they show both ways of working with files.

**Q56. What does mode `"w"` do?**
It creates the file, or empties it if it already exists, before writing. So each export replaces the old file with fresh data.

---

## 7. Suggestions and limitations

**Q57. How are suggestions generated?**
They are rule-based. `generate_suggestions()` works out each category's share of the total CO2. If a category is 20% or more of the total, it shows the fixed tip for that category from the `SUGGESTIONS` dictionary. No AI or internet is used.

**Q58. What are the limitations of your project?**
- Emission factors are illustrative, not official.
- It is for a single user and has no login.
- It runs in the terminal only, with no graphical interface.
- Changing a factor does not recalculate old records (this is deliberate).
- Undo works only for records added in the current session.
- Typing `nan` or `inf` as a quantity is accepted by `float()`, and MySQL then rejects it with a database error. The program shows the error and returns to the menu; it does not crash.

**Q59. How could the project be improved?**
Add charts of monthly emissions, set monthly targets, support several users, use official factors from a government source, or build a graphical interface.

---

## Quick demo order for the presentation
1. Menu 2: show the sample records (the JOIN brings in the category name and unit).
2. Menu 1: add a record and show the calculation and confirmation.
3. Menu 3: search between two dates (BETWEEN) and by category (LIKE).
4. Menu 4: update the quantity and show that CO2 is recalculated.
5. Menus 6, 7 and 9: show the summaries (aggregates, GROUP BY, suggestions).
6. Menus 10 and 11: export, then open the CSV and text files.
7. Menu 14: undo the record added in step 2, which shows the stack in action.
8. Type letters as a quantity and an impossible date to show the error handling.
