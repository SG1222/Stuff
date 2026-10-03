# ============================================================
# CARBON DATA LOGGER - Personal Carbon Footprint Tracking System
# CBSE Class XII Computer Science Project (Python + MySQL)
#
# Records everyday activities (electricity, travel, LPG, flights),
# estimates their CO2 emissions and stores them in MySQL.
# Emission factors are ILLUSTRATIVE project values, not official data.
# ============================================================

import csv
import datetime
import mysql.connector

# MySQL connection settings - change the password to match your system
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "carbon_logger"

# Output file names
CSV_FILE = "carbon_records.csv"
SUMMARY_FILE = "carbon_summary.txt"

# Default categories: (name, unit, illustrative kg CO2 per unit)
DEFAULT_CATEGORIES = [
    ("Electricity", "kWh", 0.82),
    ("Car Travel", "km", 0.17),
    ("Bus Travel", "km", 0.10),
    ("Train Travel", "km", 0.04),
    ("LPG", "kg", 2.98),
    ("Flight", "km", 0.15),
]

# Simple rule-based suggestions for each category
SUGGESTIONS = {
    "Electricity": "Switch off unused lights/fans and prefer LED bulbs and efficient appliances.",
    "Car Travel": "Consider public transport, car-pooling or cycling for suitable journeys.",
    "Bus Travel": "Bus travel is already a good choice; walk or cycle for very short trips.",
    "Train Travel": "Train travel is a low-emission option; keep using it where possible.",
    "LPG": "Use lids while cooking and pressure cookers to save cooking gas.",
    "Flight": "Flights add a lot of CO2; prefer trains for shorter distances when possible.",
}

MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")

# Common SELECT used to show records with category name and unit (JOIN)
RECORD_QUERY = ("SELECT r.record_id, r.record_date, c.category_name, r.quantity, "
                "c.unit, r.co2_emission, r.note "
                "FROM emission_records r INNER JOIN categories c "
                "ON r.category_id = c.category_id ")

connection = None
cursor = None


# ---------------- Database setup ----------------

# Connect to the MySQL server and select (or create) the database
def connect_database():
    global connection, cursor
    connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + DB_NAME)
    cursor.execute("USE " + DB_NAME)


# Create both tables if they do not exist yet
def create_tables():
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
                        category_id INT AUTO_INCREMENT PRIMARY KEY,
                        category_name VARCHAR(30) NOT NULL UNIQUE,
                        unit VARCHAR(10) NOT NULL,
                        emission_factor FLOAT NOT NULL)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS emission_records (
                        record_id INT AUTO_INCREMENT PRIMARY KEY,
                        record_date DATE NOT NULL,
                        category_id INT NOT NULL,
                        quantity FLOAT NOT NULL,
                        co2_emission FLOAT NOT NULL,
                        note VARCHAR(100),
                        FOREIGN KEY (category_id) REFERENCES categories(category_id))""")
    connection.commit()


# Insert the default categories only when the table is empty
def insert_default_categories():
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    if count == 0:
        query = "INSERT INTO categories (category_name, unit, emission_factor) VALUES (%s, %s, %s)"
        for category in DEFAULT_CATEGORIES:
            cursor.execute(query, category)
        connection.commit()
        print("Default categories added.")


# ---------------- Input helper functions ----------------

# Wait for the user before showing the menu again
def pause_program():
    input("\nPress Enter to continue...")


def print_heading(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


# Keep asking until the user types a whole number
def get_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input! Please enter a whole number.")


# Keep asking until the user types a number greater than zero
def get_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Quantity must be greater than zero.")
            else:
                return value
        except ValueError:
            print("Invalid input! Please enter a numeric value.")


# Return the date as 'YYYY-MM-DD' if it is valid, otherwise None
def validate_date(date_text):
    try:
        date_value = datetime.datetime.strptime(date_text, "%Y-%m-%d")
        return date_value.strftime("%Y-%m-%d")
    except ValueError:
        return None


# Ask for a date; an empty answer means today's date
def get_date(prompt):
    while True:
        date_text = input(prompt + " (YYYY-MM-DD, Enter for today): ").strip()
        if date_text == "":
            return str(datetime.date.today())
        valid_date = validate_date(date_text)
        if valid_date is None:
            print("Invalid date! Example of a correct date: 2026-08-15")
        else:
            return valid_date


def ask_yes_no(prompt):
    answer = input(prompt + " (Y/N): ").strip().upper()
    return answer == "Y"


# ---------------- Categories ----------------

# Display all categories in a table and return them as a list
def display_categories():
    cursor.execute("SELECT category_id, category_name, unit, emission_factor "
                   "FROM categories ORDER BY category_id")
    categories = cursor.fetchall()
    print("\n{:<5}{:<16}{:<8}{:>22}".format("ID", "CATEGORY", "UNIT", "FACTOR (kg CO2/unit)"))
    print("-" * 51)
    for category in categories:
        print("{:<5}{:<16}{:<8}{:>22.3f}".format(category[0], category[1],
                                                 category[2], category[3]))
    return categories


# Fetch one category (id, name, unit, factor) from MySQL, or None
def get_category(category_id):
    cursor.execute("SELECT category_id, category_name, unit, emission_factor "
                   "FROM categories WHERE category_id = %s", (category_id,))
    return cursor.fetchone()


# Ask the user to pick a valid category ID
def choose_category():
    display_categories()
    while True:
        category_id = get_integer("\nEnter category ID: ")
        category = get_category(category_id)
        if category is None:
            print("No category with that ID. Try again.")
        else:
            return category


# ---------------- Carbon calculation ----------------

# Calculate carbon emission: CO2 = quantity x emission factor
def calculate_emission(quantity, emission_factor):
    return round(float(quantity) * float(emission_factor), 2)


# ---------------- Add and view records ----------------

def add_record():
    print_heading("ADD CARBON RECORD")
    category = choose_category()
    record_date = get_date("Enter date")
    quantity = get_positive_number("Enter quantity in " + category[2] + ": ")
    note = input("Enter a note (optional): ").strip()

    # The emission factor comes from the categories table in MySQL
    co2 = calculate_emission(quantity, category[3])
    print("\nCalculation:", quantity, category[2], "x", category[3], "kg/" + category[2],
          "=", co2, "kg CO2")

    if ask_yes_no("Save this record?"):
        query = ("INSERT INTO emission_records (record_date, category_id, quantity, "
                 "co2_emission, note) VALUES (%s, %s, %s, %s, %s)")
        values = (record_date, category[0], quantity, co2, note)
        cursor.execute(query, values)
        connection.commit()
        print("Record saved successfully with ID", cursor.lastrowid)
    else:
        print("Record not saved.")


# Print a list of records as a neat table
def print_records(records):
    if len(records) == 0:
        print("\nNo records found.")
        return
    print("\n{:<5}{:<13}{:<15}{:>10}  {:<6}{:>10}  {}".format(
        "ID", "DATE", "CATEGORY", "QUANTITY", "UNIT", "CO2 (kg)", "NOTE"))
    print("-" * 80)
    for record in records:
        note = record[6] if record[6] else ""
        print("{:<5}{:<13}{:<15}{:>10.2f}  {:<6}{:>10.2f}  {}".format(
            record[0], str(record[1]), record[2], record[3], record[4], record[5], note))
    print("-" * 80)
    print("Records shown:", len(records))


# Display all stored records
def view_all_records():
    print_heading("ALL CARBON RECORDS")
    cursor.execute(RECORD_QUERY + "ORDER BY r.record_date, r.record_id")
    records = cursor.fetchall()
    print_records(records)


# Fetch one record by its ID, or None if it does not exist
def get_record(record_id):
    cursor.execute(RECORD_QUERY + "WHERE r.record_id = %s", (record_id,))
    return cursor.fetchone()


# ---------------- Search ----------------

def search_by_id():
    record_id = get_integer("Enter record ID: ")
    record = get_record(record_id)
    if record is None:
        print("No record found with ID", record_id)
    else:
        print_records([record])


def search_by_category():
    name = input("Enter category name (or part of it): ").strip()
    cursor.execute(RECORD_QUERY + "WHERE c.category_name LIKE %s ORDER BY r.record_date",
                   ("%" + name + "%",))
    print_records(cursor.fetchall())


def search_by_date():
    record_date = get_date("Enter date")
    cursor.execute(RECORD_QUERY + "WHERE r.record_date = %s", (record_date,))
    print_records(cursor.fetchall())


def search_by_date_range():
    start_date = get_date("Enter start date")
    end_date = get_date("Enter end date")
    if start_date > end_date:
        print("Start date was after end date, so the dates have been swapped.")
        start_date, end_date = end_date, start_date
    cursor.execute(RECORD_QUERY + "WHERE r.record_date BETWEEN %s AND %s "
                   "ORDER BY r.record_date", (start_date, end_date))
    print_records(cursor.fetchall())


def search_menu():
    while True:
        print_heading("SEARCH RECORDS")
        print("1. Search by Record ID")
        print("2. Search by Category")
        print("3. Search by Date")
        print("4. Search between two dates")
        print("5. Return to Main Menu")
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            search_by_id()
        elif choice == "2":
            search_by_category()
        elif choice == "3":
            search_by_date()
        elif choice == "4":
            search_by_date_range()
        elif choice == "5":
            return
        else:
            print("Invalid choice! Please enter 1 to 5.")
        pause_program()


# ---------------- Update and delete ----------------

def update_record():
    print_heading("UPDATE RECORD")
    record_id = get_integer("Enter record ID to update: ")
    record = get_record(record_id)
    if record is None:
        print("No record found with ID", record_id)
        return
    print("\nCurrent details:")
    print_records([record])

    # Read the current category ID and quantity of this record
    cursor.execute("SELECT category_id, quantity FROM emission_records WHERE record_id = %s",
                   (record_id,))
    category_id, quantity = cursor.fetchone()
    new_date = str(record[1])
    new_note = record[6]

    print("\nPress Enter to keep the current value.")
    date_text = input("New date (YYYY-MM-DD): ").strip()
    if date_text != "":
        if validate_date(date_text) is None:
            print("Invalid date, keeping the old date.")
        else:
            new_date = validate_date(date_text)

    if ask_yes_no("Change the category?"):
        category_id = choose_category()[0]

    quantity_text = input("New quantity: ").strip()
    if quantity_text != "":
        try:
            if float(quantity_text) > 0:
                quantity = float(quantity_text)
            else:
                print("Quantity must be positive, keeping the old quantity.")
        except ValueError:
            print("Not a number, keeping the old quantity.")

    note_text = input("New note: ").strip()
    if note_text != "":
        new_note = note_text

    # Recalculate CO2 using the factor of the (possibly new) category
    category = get_category(category_id)
    new_co2 = calculate_emission(quantity, category[3])

    query = ("UPDATE emission_records SET record_date = %s, category_id = %s, "
             "quantity = %s, co2_emission = %s, note = %s WHERE record_id = %s")
    cursor.execute(query, (new_date, category_id, quantity, new_co2, new_note, record_id))
    connection.commit()
    print("\nRecord updated. Recalculated CO2:", new_co2, "kg")
    print_records([get_record(record_id)])


def delete_record():
    print_heading("DELETE RECORD")
    record_id = get_integer("Enter record ID to delete: ")
    record = get_record(record_id)
    if record is None:
        print("No record found with ID", record_id)
        return
    print_records([record])
    if ask_yes_no("Delete this record?"):
        cursor.execute("DELETE FROM emission_records WHERE record_id = %s", (record_id,))
        connection.commit()
        print(cursor.rowcount, "record deleted.")
    else:
        print("Delete cancelled.")


# ---------------- Summaries ----------------

# Return (count, total, average, minimum, maximum) using aggregate functions
def get_overall_totals():
    cursor.execute("SELECT COUNT(*), SUM(co2_emission), AVG(co2_emission), "
                   "MIN(co2_emission), MAX(co2_emission) FROM emission_records")
    return cursor.fetchone()


# Return a list of (category, number of records, total CO2), highest first
def get_category_totals():
    cursor.execute("SELECT c.category_name, COUNT(*), SUM(r.co2_emission) "
                   "FROM emission_records r INNER JOIN categories c "
                   "ON r.category_id = c.category_id "
                   "GROUP BY c.category_name ORDER BY SUM(r.co2_emission) DESC")
    return cursor.fetchall()


def overall_summary():
    print_heading("CARBON FOOTPRINT SUMMARY")
    count, total, average, lowest, highest = get_overall_totals()
    if count == 0:
        print("No records available yet.")
        return
    print("Total records              :", count)
    print("Total CO2 emissions        : {:.2f} kg".format(total))
    print("Average CO2 per record     : {:.2f} kg".format(average))
    print("Lowest individual emission : {:.2f} kg".format(lowest))
    print("Highest individual emission: {:.2f} kg".format(highest))

    cursor.execute("SELECT MIN(record_date), MAX(record_date) FROM emission_records")
    first_date, last_date = cursor.fetchone()
    print("Records from", first_date, "to", last_date)


def category_summary():
    print_heading("CATEGORY-WISE SUMMARY")
    rows = get_category_totals()
    if len(rows) == 0:
        print("No records available yet.")
        return
    grand_total = 0
    print("{:<18}{:>10}{:>16}{:>12}".format("CATEGORY", "RECORDS", "TOTAL CO2", "SHARE"))
    print("-" * 56)
    for row in rows:
        grand_total = grand_total + float(row[2])
    for row in rows:
        share = float(row[2]) / grand_total * 100 if grand_total > 0 else 0
        print("{:<18}{:>10}{:>16.2f}{:>11.1f}%".format(row[0], row[1], row[2], share))
    print("-" * 56)
    print("{:<18}{:>10}{:>16.2f}".format("TOTAL", "", grand_total))


# Show which months have records, using DISTINCT
def show_available_months():
    cursor.execute("SELECT DISTINCT YEAR(record_date), MONTH(record_date) "
                   "FROM emission_records ORDER BY 1, 2")
    months = cursor.fetchall()
    if len(months) > 0:
        print("Months with records:")
        for year, month in months:
            print("  ", MONTH_NAMES[month - 1], year, "(" + str(month) + "/" + str(year) + ")")
    return len(months)


def monthly_summary():
    print_heading("MONTHLY SUMMARY")
    if show_available_months() == 0:
        print("No records available yet.")
        return
    month = get_integer("\nEnter month number (1-12): ")
    if month < 1 or month > 12:
        print("Invalid month! It must be between 1 and 12.")
        return
    year = get_integer("Enter year (e.g. 2026): ")

    cursor.execute("SELECT COUNT(*), SUM(co2_emission), AVG(co2_emission) FROM emission_records "
                   "WHERE MONTH(record_date) = %s AND YEAR(record_date) = %s", (month, year))
    count, total, average = cursor.fetchone()
    print("\nCARBON SUMMARY -", MONTH_NAMES[month - 1].upper(), year)
    if count == 0:
        print("No records for this month.")
        return
    print("\nTotal records:", count)
    print("Total estimated CO2: {:.2f} kg".format(total))
    print("Average emission: {:.2f} kg".format(average))

    # Category with the largest total in that month
    cursor.execute("SELECT c.category_name, SUM(r.co2_emission) "
                   "FROM emission_records r INNER JOIN categories c "
                   "ON r.category_id = c.category_id "
                   "WHERE MONTH(r.record_date) = %s AND YEAR(r.record_date) = %s "
                   "GROUP BY c.category_name ORDER BY SUM(r.co2_emission) DESC", (month, year))
    top = cursor.fetchall()[0]
    print("Highest category:", top[0], "({:.2f} kg)".format(top[1]))


# Return a list of suggestion strings based on the recorded categories
def generate_suggestions(category_totals):
    suggestions = []
    grand_total = 0
    for row in category_totals:
        grand_total = grand_total + float(row[2])
    for row in category_totals:
        name = row[0]
        share = float(row[2]) / grand_total * 100 if grand_total > 0 else 0
        # Suggest only for categories contributing at least 20% of the total
        if share >= 20:
            if name in SUGGESTIONS:
                advice = SUGGESTIONS[name]
            else:
                advice = "Try to reduce this activity where it is practical."
            suggestions.append(name + " ({:.1f}% of total): ".format(share) + advice)
    return suggestions


def highest_emission_category():
    print_heading("HIGHEST EMISSION CATEGORY")
    rows = get_category_totals()
    if len(rows) == 0:
        print("No records available yet.")
        return
    # Rows are ordered by total CO2 in descending order, so the first is the highest
    print("Category with the highest emissions:", rows[0][0])
    print("Total CO2 from this category: {:.2f} kg in {} record(s)".format(rows[0][2], rows[0][1]))
    if len(rows) > 1:
        print("Lowest category:", rows[-1][0], "({:.2f} kg)".format(rows[-1][2]))

    print("\nSuggestions:")
    for suggestion in generate_suggestions(rows):
        print("-", suggestion)


# ---------------- Export ----------------

# Write all records to a CSV file using the csv module
def export_to_csv():
    print_heading("EXPORT RECORDS TO CSV")
    cursor.execute(RECORD_QUERY + "ORDER BY r.record_date, r.record_id")
    records = cursor.fetchall()
    if len(records) == 0:
        print("No records to export.")
        return
    try:
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Record ID", "Date", "Category", "Quantity", "Unit",
                             "CO2 (kg)", "Note"])
            writer.writerows(records)
        print(len(records), "records exported to", CSV_FILE)
    except IOError:
        print("Error: could not write to", CSV_FILE, "(is it open in another program?)")


# Write an overall and category-wise summary to a text file
def export_summary_to_text():
    print_heading("EXPORT SUMMARY TO TEXT FILE")
    count, total, average, lowest, highest = get_overall_totals()
    if count == 0:
        print("No records available to summarise.")
        return
    category_rows = get_category_totals()
    file = None
    try:
        file = open(SUMMARY_FILE, "w")
        file.write("CARBON DATA LOGGER\n")
        file.write("PERSONAL FOOTPRINT SUMMARY\n")
        file.write("Generated on: " + str(datetime.date.today()) + "\n\n")
        file.write("Total Records: " + str(count) + "\n")
        file.write("Total Estimated CO2: {:.2f} kg\n".format(total))
        file.write("Average CO2: {:.2f} kg\n".format(average))
        file.write("Lowest Emission: {:.2f} kg\n".format(lowest))
        file.write("Highest Emission: {:.2f} kg\n\n".format(highest))
        file.write("CATEGORY SUMMARY\n")
        file.write("----------------\n")
        for row in category_rows:
            file.write("{}: {:.2f} kg ({} records)\n".format(row[0], row[2], row[1]))
        file.write("\nSUGGESTIONS\n")
        file.write("-----------\n")
        for suggestion in generate_suggestions(category_rows):
            file.write("- " + suggestion + "\n")
        file.write("\nNote: emission factors are illustrative project values.\n")
        print("Summary exported to", SUMMARY_FILE)
    except IOError:
        print("Error: could not write to", SUMMARY_FILE)
    finally:
        # The file is closed whether or not an error occurred
        if file is not None:
            file.close()


# ---------------- Manage emission factors ----------------

def update_emission_factor():
    category = choose_category()
    print("Current factor for", category[1], "is", category[3], "kg CO2 per", category[2])
    new_factor = get_positive_number("Enter new emission factor: ")
    cursor.execute("UPDATE categories SET emission_factor = %s WHERE category_id = %s",
                   (new_factor, category[0]))
    connection.commit()
    print("Emission factor updated. It will be used for new or edited records.")


def add_category():
    name = input("Enter new category name: ").strip().title()
    unit = input("Enter unit (e.g. kWh, km, kg): ").strip()
    if name == "" or unit == "":
        print("Name and unit cannot be empty.")
        return
    factor = get_positive_number("Enter emission factor (kg CO2 per " + unit + "): ")
    try:
        cursor.execute("INSERT INTO categories (category_name, unit, emission_factor) "
                       "VALUES (%s, %s, %s)", (name, unit, factor))
        connection.commit()
        print("Category", name, "added.")
    except mysql.connector.IntegrityError:
        print("A category with this name already exists.")


def manage_emission_factors():
    while True:
        print_heading("MANAGE / VIEW EMISSION FACTORS")
        print("Note: these factors are illustrative values for this project.")
        print("1. View Emission Factors")
        print("2. Update an Emission Factor")
        print("3. Add a New Category")
        print("4. Return to Main Menu")
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            display_categories()
        elif choice == "2":
            update_emission_factor()
        elif choice == "3":
            add_category()
        elif choice == "4":
            return
        else:
            print("Invalid choice! Please enter 1 to 4.")
        pause_program()


# ---------------- Help and main menu ----------------

def show_help():
    print_heading("HELP")
    print("* Add a record for an activity, e.g. 15 kWh of electricity or 20 km by car.")
    print("* CO2 is estimated as: quantity x emission factor of the category.")
    print("* Dates are entered as YYYY-MM-DD. Press Enter to use today's date.")
    print("* Use Search, Update and Delete with the record ID shown in the tables.")
    print("* Summaries show totals overall, per category and per month.")
    print("* Exports create", CSV_FILE, "and", SUMMARY_FILE, "in this folder.")
    print("* Emission factors are illustrative and can be changed from option 12.")


def display_main_menu():
    print("\n" + "=" * 50)
    print("CARBON DATA LOGGER".center(50))
    print("=" * 50)
    print("1. Add Carbon Record")
    print("2. View All Records")
    print("3. Search Records")
    print("4. Update Record")
    print("5. Delete Record")
    print("6. Carbon Footprint Summary")
    print("7. Category-wise Summary")
    print("8. Monthly Summary")
    print("9. Highest Emission Category")
    print("10. Export Records to CSV")
    print("11. Export Summary to Text File")
    print("12. Manage/View Emission Factors")
    print("13. Help")
    print("0. Exit")


def main():
    try:
        # Connect to the MySQL database and prepare the tables
        connect_database()
        create_tables()
        insert_default_categories()
    except mysql.connector.Error as error:
        print("Could not connect to MySQL:", error)
        print("Check that MySQL is running and the password in DB_PASSWORD is correct.")
        return

    # Each menu number is linked to the function that handles it
    menu_actions = {
        "1": add_record, "2": view_all_records, "3": search_menu,
        "4": update_record, "5": delete_record, "6": overall_summary,
        "7": category_summary, "8": monthly_summary, "9": highest_emission_category,
        "10": export_to_csv, "11": export_summary_to_text,
        "12": manage_emission_factors, "13": show_help,
    }

    try:
        while True:
            display_main_menu()
            choice = input("\nEnter your choice: ").strip()
            if choice == "0":
                print("Thank you for using Carbon Data Logger. Goodbye!")
                break
            elif choice in menu_actions:
                try:
                    menu_actions[choice]()
                except mysql.connector.Error as error:
                    print("Database error:", error)
                # Sub-menus already pause after each action
                if choice not in ("3", "12"):
                    pause_program()
            else:
                print("Invalid choice! Please enter a number from 0 to 13.")
    finally:
        # Always close the cursor and connection when the program ends
        cursor.close()
        connection.close()


main()
