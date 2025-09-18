# Build a programming Journal
import database

menu = """Please select one of the following options:
1 - Add new entry for today
2 - View entries
3 - Exit
"""

welcome = "welcome to the programming diary"
print(welcome)
database.create_table()

def prompt_new_entry():
    entry_content = input ("what have you done today?")
    entry_date = input("enter the date: ")
    database.add_entry(entry_content, entry_date)

def view_entries():
    for entry in entries:
        print(f"{entry["date"]}\n{entry["content"]}\n\n")
    # the cursor returns a tuple instead of dictionary
    # if we don't use: connection.row_factory = sqlite3.Row, which will deal with rows like dictiona
    # then we should deal with tuple using:
    # print(f"{entry[0]}\n{entry[1]}\n\n")
    


# use walrus operator
while (user_input := input(menu)) != "3":
    if user_input == "1":
        prompt_new_entry()
    elif user_input == "2":
        entries = database.get_entry()
        view_entries()
    else:
        print("invalid, try again")



