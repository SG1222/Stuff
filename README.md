# Carbon Data Logger

A personal carbon footprint tracker for the terminal.
It is a CBSE Class XII Computer Science project in Python and MySQL.

This README uses the rules of Simplified Technical English (ASD-STE100).
Sentences are short. Each step has one instruction. Each concept has one name.

---

## 1. Technical terms

This document uses these terms with one meaning only.

| Term | Meaning |
|---|---|
| **program** | The file `carbon_logger.py`. |
| **database** | The MySQL database `carbon_logger`. |
| **record** | One row in the table `emission_records`. A record is one activity on one date. |
| **category** | One row in the table `categories`, for example "Car Travel". |
| **emission factor** | The kilograms of CO2 for one unit of a category, for example 0.17 kg for 1 km by car. |
| **CO2 value** | The estimated kilograms of CO2 for one record. |
| **cursor** | The Python object that sends SQL queries to MySQL and holds the results. |
| **placeholder** | The text `%s` in a query. The connector puts a value in its place. |
| **stack** | A list where the last item put in is the first item taken out (LIFO: Last In, First Out). |
| **tuple index** | The position of a value in a row, for example `category[3]`. Positions start at 0. |

---

## 2. What the program does

The program records activities that release CO2.
It calculates the CO2 value of each record with this formula:

```
CO2 value = quantity × emission factor
```

The program keeps all records in the database.
The user can search, update, delete, summarise and export the records.

> **Note:** The emission factors are illustrative values for a school project. They are not official data. The user can change them with menu option 12.

---

## 3. Project files

All project files are in the folder `CarbonDataLogger/`.

| File | Purpose |
|---|---|
| [`carbon_logger.py`](CarbonDataLogger/carbon_logger.py) | The program. It contains all the Python code. |
| [`database_setup.sql`](CarbonDataLogger/database_setup.sql) | An SQL script. It makes the database, the two tables, the default categories and five sample records. |
| [`VIVA_SHEET.md`](CarbonDataLogger/VIVA_SHEET.md) | Questions and answers for the viva. |
| [`Project_Report.docx`](CarbonDataLogger/Project_Report.docx) | The CBSE project report. It has the certificate, design, source code, screenshots, tests and bibliography. |
| `carbon_records.csv` | The CSV export. Menu option 10 makes this file. |
| `carbon_summary.txt` | The text summary. Menu option 11 makes this file. |

---

## 4. Requirements

- Python 3
- A MySQL server (MySQL 8 or MariaDB)
- The Python package `mysql-connector-python`

The modules `csv` and `datetime` are part of Python. You do not install them.

---

## 5. Setup procedure

> **Warning:** The program uses the MySQL user `root` with the password `root`. If your password is different, the program cannot connect. Do step 3 before you start the program.

1. Start the MySQL server.
2. Install the connector:
   ```
   pip install mysql-connector-python
   ```
3. Open `carbon_logger.py`. Find the line `DB_PASSWORD = "root"`. Change `root` to your MySQL password, if necessary.
4. Choose one of the two methods below to make the database.

**Method A: with sample data (recommended for a demonstration)**

> **Caution:** Run the SQL script one time only. A second run stops with a "Duplicate entry" error, because the category names must be unique.

1. Open the MySQL client in the folder `CarbonDataLogger`.
2. Type this command:
   ```sql
   SOURCE database_setup.sql;
   ```

**Method B: empty database**

1. Do not run the SQL script.
2. Start the program. The program makes the database, the tables and the default categories.

> **Note:** If you start the program first and then run the SQL script, the script stops with a "Duplicate entry" error. To start again, type `DROP DATABASE carbon_logger;` in the MySQL client. Then run the script.

---

## 6. Run the program

1. Open a terminal in the folder `CarbonDataLogger`.
2. Type:
   ```
   python carbon_logger.py
   ```
3. Type the number of a menu option.
4. Push Enter.

---

## 7. Menu options

| Option | Name | What it does | Function |
|---|---|---|---|
| 1 | Add Carbon Record | Asks for the category, date, quantity and note. Shows the calculation. Saves the record after you confirm. | `add_record()` |
| 2 | View All Records | Shows all records in a table, sorted by date. | `view_all_records()` |
| 3 | Search Records | Opens a sub-menu. You can search by record ID, category name, one date, or two dates. | `search_menu()` |
| 4 | Update Record | Shows a record. Lets you change the date, category, quantity and note. Calculates the CO2 value again. | `update_record()` |
| 5 | Delete Record | Shows a record. Deletes it after you type Y. | `delete_record()` |
| 6 | Carbon Footprint Summary | Shows the count, total, average, lowest and highest CO2 values. | `overall_summary()` |
| 7 | Category-wise Summary | Shows the number of records, total CO2 and percentage share for each category. | `category_summary()` |
| 8 | Monthly Summary | Shows the months that have records. Then shows a summary for one month. | `monthly_summary()` |
| 9 | Highest Emission Category | Shows the highest and lowest categories. Shows suggestions. | `highest_emission_category()` |
| 10 | Export Records to CSV | Writes all records to `carbon_records.csv`. | `export_to_csv()` |
| 11 | Export Summary to Text File | Writes a summary to `carbon_summary.txt`. | `export_summary_to_text()` |
| 12 | Manage/View Emission Factors | Opens a sub-menu. You can view the factors, change a factor, or add a category. | `manage_emission_factors()` |
| 13 | Help | Shows short instructions. | `show_help()` |
| 14 | Undo Last Added Record | Removes the newest record that you added in this session, after you type Y. Each use goes one record further back. | `undo_last_record()` |
| 0 | Exit | Closes the database connection. Stops the program. | in `main()` |

---

## 8. Database design

### Table `categories`

| Column | Type | Constraint |
|---|---|---|
| `category_id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `category_name` | VARCHAR(30) | NOT NULL, UNIQUE |
| `unit` | VARCHAR(10) | NOT NULL |
| `emission_factor` | FLOAT | NOT NULL |

### Table `emission_records`

| Column | Type | Constraint |
|---|---|---|
| `record_id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `record_date` | DATE | NOT NULL |
| `category_id` | INT | NOT NULL, FOREIGN KEY to `categories(category_id)` |
| `quantity` | FLOAT | NOT NULL |
| `co2_emission` | FLOAT | NOT NULL |
| `note` | VARCHAR(100) | (none) |

### Relation between the tables

One category has many records. Each record has one category.
The record keeps only the `category_id`. It does not keep the category name or unit.
The program gets the name and unit with an `INNER JOIN`.

```
categories (1) ──────< (many) emission_records
     category_id  =  category_id
```

The foreign key gives two protections:
- MySQL does not save a record with a category that does not exist.
- MySQL does not delete a category that has records.

---

## 9. How the program flows

### Startup

1. The last line of the file calls `main()`.
2. `main()` calls `connect_database()`. This function connects to MySQL. It makes the database if it does not exist.
3. `main()` calls `create_tables()`. This function makes the two tables if they do not exist.
4. `main()` calls `insert_default_categories()`. This function adds the six categories if the table is empty.
5. If one of these steps fails, the program shows the error and stops.

### Main loop

1. `main()` shows the menu with `display_main_menu()`.
2. The user types a choice.
3. `main()` finds the function for that choice in the dictionary `menu_actions`.
4. `main()` calls the function.
5. The loop starts again. Choice 0 stops the loop.

### Data flow when you add a record

```
user picks category ─► get_category() reads id, name, unit, factor from MySQL
user types date     ─► get_date() checks it
user types quantity ─► get_positive_number() checks it
                       calculate_emission(quantity, factor) ─► CO2 value
user types Y        ─► INSERT ... VALUES (%s, %s, %s, %s, %s) ─► commit()
```

---

## 10. The tricky parts, explained

This section explains the parts of the code that are not easy to see at first.

### 10.1 Two global variables: `connection` and `cursor`

The variables `connection` and `cursor` are at the top of the file. Their first value is `None`.
`connect_database()` gives them their real values. It uses the keyword `global` for this.
Without `global`, Python makes new local variables inside the function. Other functions cannot see local variables.
All other functions use the global `cursor` to run queries.

### 10.2 The shared query `RECORD_QUERY`

Four features show records: view, search, update and delete. They all need the same `SELECT ... INNER JOIN`.
The program keeps this query one time, in the constant `RECORD_QUERY`.
Each function adds its own end to the query:

```python
cursor.execute(RECORD_QUERY + "WHERE r.record_id = %s", (record_id,))
```

> **Caution:** `RECORD_QUERY` ends with a space. This space keeps `category_id` and `WHERE` apart. If you remove the space, the SQL becomes `category_idWHERE` and the query fails.

The query uses the aliases `r` and `c` for the two tables. The aliases make the query shorter.

### 10.3 Placeholders (`%s`) and the comma in `(record_id,)`

The program never joins user input into a query string. It uses placeholders:

```python
cursor.execute("DELETE FROM emission_records WHERE record_id = %s", (record_id,))
```

The connector puts each value in place of a `%s`. MySQL treats the value as data only.
This stops SQL injection. It also handles text with quotes, for example `Mom's car`.

The second argument must be a tuple. `(record_id)` is only a number in brackets.
The comma in `(record_id,)` makes a tuple with one item.

### 10.4 Why `"USE " + DB_NAME` joins strings

`connect_database()` uses `"CREATE DATABASE IF NOT EXISTS " + DB_NAME` and `"USE " + DB_NAME`.
A placeholder can hold a value. It cannot hold the name of a database or table.
`DB_NAME` is a constant in the code. The user does not type it. Thus the join is safe.

### 10.5 Tuple indexes in rows

MySQL returns each row as a tuple. The code reads values by position.

A **category** row (from `get_category()` and `choose_category()`):

| Index | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Value | category_id | category_name | unit | emission_factor |

A **record** row (from `RECORD_QUERY`):

| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Value | record_id | record_date | category_name | quantity | unit | co2_emission | note |

Thus `category[3]` is the emission factor, and `record[5]` is the CO2 value.

### 10.6 `fetchone()` and `fetchall()`

`fetchone()` returns one row as a tuple. If there is no row, it returns `None`.
The program uses `fetchone()` when the query gives one row only. Examples: a search by primary key, or a query with only aggregate functions.

`fetchall()` returns all rows as a list of tuples. If there are no rows, it returns an empty list `[]`.

In `monthly_summary()`, the query for the highest category can return many rows. The code uses `cursor.fetchall()[0]` there.
If you use `fetchone()` on a result with many rows, the other rows stay unread. Then the next query can fail with the error "Unread result found".

### 10.7 Aggregates on an empty table give NULL

On an empty table, `COUNT(*)` gives 0. But `SUM()`, `AVG()`, `MIN()` and `MAX()` give NULL. Python receives NULL as `None`.
The code `"{:.2f}".format(None)` stops with an error.
Thus each summary function checks for zero records first. It uses `if count == 0` or `if len(rows) == 0`. It shows a "No records" message and returns before the formatting.

### 10.8 Dates

`validate_date()` uses `datetime.datetime.strptime(text, "%Y-%m-%d")`.
If the date does not exist, for example `2026-02-30`, Python raises `ValueError`. The function then returns `None`.

The function then uses `strftime("%Y-%m-%d")` to write the date again. This step adds missing zeros: `2026-9-5` becomes `2026-09-05`.

The zeros are important in `search_by_date_range()`. That function compares two dates as strings: `if start_date > end_date`.
String comparison is correct only when all dates have the same length and the same order (year, month, day).
If the start date is after the end date, the function swaps them.

In `get_date()`, an empty answer gives today's date: `str(datetime.date.today())`.

MySQL returns a `DATE` column as a Python `date` object, not a string. The code uses `str(record[1])` to print it.

### 10.9 Numbers, rounding and formatting

`calculate_emission()` uses `float()` on both values. This makes sure that both values are numbers before the multiplication.
It uses `round(..., 2)` to keep two decimal places.

A FLOAT column can give a value like `143.11000156402588` after `SUM()`.
The code shows numbers with `"{:.2f}".format(value)`. Thus the screen always shows two decimal places, for example `143.11`.

### 10.10 Update: "Press Enter to keep the current value"

`update_record()` first reads the current values into variables: `new_date`, `category_id`, `quantity` and `new_note`.
For each field, an empty answer keeps the old value. A new valid answer replaces it.
At the end, the function always calculates the CO2 value again. It uses the emission factor of the category that the record has now.
Then one `UPDATE` query saves all fields.

`RECORD_QUERY` does not give `category_id`. Thus `update_record()` reads it with one more small query.

### 10.11 A changed emission factor does not change old records

Each record keeps the CO2 value that the program calculated when the user saved it.
If you change a factor with menu option 12, old records keep their CO2 values.
A new record uses the new factor. An updated record also uses the new factor.
This is by design. A record shows the estimate at the time of the activity.

### 10.12 Highest and lowest category

`get_category_totals()` uses `GROUP BY c.category_name` and `ORDER BY SUM(r.co2_emission) DESC`.
Thus the first row is the highest category: `rows[0]`.
The last row is the lowest category: `rows[-1]`.

### 10.13 Percentage share and suggestions

`get_grand_total()` adds the totals of all categories.
Each share is: `category total / grand total × 100`.
The code checks `if grand_total > 0` before the division. This stops a division by zero.

`generate_suggestions()` gives a suggestion only for a category with a share of 20% or more.
It gets the text from the dictionary `SUGGESTIONS`. If the category is not in the dictionary, for example a new category, it uses a general text.
The rules are fixed. The program does not use AI or the internet.

### 10.14 The dictionary `menu_actions`

```python
menu_actions = {"1": add_record, "2": view_all_records, ...}
...
menu_actions[choice]()
```

The dictionary keeps the function names **without** brackets. Thus Python does not call the functions when it makes the dictionary.
The brackets at the end of `menu_actions[choice]()` call the function.
The keys are strings, because `input()` always returns a string.

Options 3 and 12 open a sub-menu. Each sub-menu pauses after each action. Thus `main()` does not pause again after these two options.

### 10.15 Three layers of error handling in `main()`

1. **Startup:** `try` / `except mysql.connector.Error`. If the connection fails, the program shows the cause and stops.
2. **Each menu action:** `try` / `except mysql.connector.Error`. A database error shows a message. The program then shows the menu again. It does not stop.
3. **The full loop:** `try` / `except KeyboardInterrupt` / `finally`. Ctrl+C shows "Program stopped by the user." The `finally` block always closes the cursor and the connection.

### 10.16 Input checks

| Function | What it stops |
|---|---|
| `get_integer()` | Text where a whole number is necessary. It catches `ValueError` and asks again. |
| `get_positive_number()` | Text, zero and negative numbers. It asks again. |
| `get_date()` | Dates that do not exist, or have the wrong format. It asks again. |
| `choose_category()` | A category ID that does not exist. It asks again. |
| `add_record()`, `update_record()` | A note longer than 100 characters. `[:100]` keeps the first 100 characters, because the column is VARCHAR(100). |
| `add_category()` | An empty name or unit. A name longer than 30 characters. A unit longer than 10 characters. |
| `add_category()` | A name that already exists. MySQL raises `IntegrityError` because the column is UNIQUE. |

> **Note:** MySQL compares text without regard to capital letters. Thus "cng car" and "CNG Car" are the same name. The second one gives "A category with this name already exists."

### 10.17 File export

`export_to_csv()` opens the file with three settings:
- `"w"`: makes a new file, or empties the old file.
- `newline=""`: stops blank lines between rows on Windows.
- `encoding="utf-8"`: lets the file hold symbols such as ₹ and Hindi text.

`writer.writerows(records)` writes all rows in one call. The rows from `fetchall()` are tuples, and `writerows()` accepts them directly.

`export_to_csv()` uses a `with` block. The `with` block closes the file automatically.
`export_summary_to_text()` uses `open()`, `write()` and `close()`. The `close()` is in a `finally` block. Thus the file closes after an error too.
The two functions show the two methods of file handling in the syllabus.

### 10.18 Month names

`MONTH_NAMES` is a tuple of 12 names. Index 0 is "January".
Month numbers start at 1. Thus the code uses `MONTH_NAMES[month - 1]`.

### 10.19 Undo with a stack

The list `undo_stack` is a stack. It holds the IDs of the records that the user added in this session.
Two functions operate the stack:
- `push(stack, item)` puts an item on the top. It uses `append()`.
- `pop(stack)` removes the top item and returns it. If the stack is empty, it returns `None`.

The flow:
1. `add_record()` saves a record. Then it pushes the new ID: `push(undo_stack, cursor.lastrowid)`.
2. `undo_last_record()` pops the top ID. This is always the newest record (LIFO).
3. The function shows the record and asks for confirmation.
4. If the user types Y, the function deletes the record.
5. If the user types N, the function pushes the ID back. Thus the user can undo it later.

Three special cases:
- The stack is empty. The function shows "Nothing to undo".
- The user deleted the record before with option 5. `get_record()` returns `None`. The function shows "was already deleted".
- The program stops. The stack is a normal Python list in memory. Thus it is empty when the program starts again. Undo works only for records from the current session.

> **Note:** `undo_stack` is a global variable, but the functions do not use the keyword `global` for it. They change the list with `append()` and `pop()`. They do not give the name a new value. `global` is necessary only when a function gives a global name a new value, as in `connect_database()` (see 10.1).

---

## 11. SQL concepts in the program

| Concept | Where |
|---|---|
| CREATE DATABASE, CREATE TABLE | `connect_database()`, `create_tables()`, `database_setup.sql` |
| PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE | `create_tables()` |
| INSERT | `insert_default_categories()`, `add_record()`, `add_category()` |
| SELECT with WHERE | `get_record()`, `get_category()`, the search functions |
| UPDATE | `update_record()`, `update_emission_factor()` |
| DELETE | `delete_record()`, `undo_last_record()` |
| BETWEEN | `search_by_date_range()` |
| LIKE | `search_by_category()` |
| DISTINCT | `show_available_months()` |
| ORDER BY | most SELECT queries |
| COUNT, SUM, AVG, MIN, MAX | `get_overall_totals()`, `overall_summary()`, `monthly_summary()` |
| GROUP BY | `get_category_totals()`, `monthly_summary()` |
| INNER JOIN with aliases | `RECORD_QUERY`, `get_category_totals()`, `monthly_summary()` |

---

## 12. Troubleshooting

| Problem | Cause | Action |
|---|---|---|
| `ModuleNotFoundError: No module named 'mysql'` | The connector is not installed. | Type `pip install mysql-connector-python`. |
| "Could not connect to MySQL: ... Access denied" | The password is wrong. | Change `DB_PASSWORD` in `carbon_logger.py`. |
| "Could not connect to MySQL: ... Can't connect" | The MySQL server is not running. | Start the MySQL server. |
| "Duplicate entry" when you run the SQL script | The database already has the categories. | Type `DROP DATABASE carbon_logger;`. Then run the script again. |
| "Error: could not write to carbon_records.csv" | Another program, for example Excel, has the file open. | Close the file in the other program. Then export again. |

---

## 13. Known limitations

- The emission factors are illustrative. They are not official data.
- The program is for one user. It has no login.
- The program uses the terminal only. It has no graphical interface.
- A changed emission factor does not change old records (see 10.11).
- Undo (option 14) works only for records added since the program started (see 10.19).
- If you type `nan` or `inf` as a quantity, the program shows a database error. It does not stop.
- The CSV file shows numbers as Python writes them, for example `10.0` and `1.7`.
