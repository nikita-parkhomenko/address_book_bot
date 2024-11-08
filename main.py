import re
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    def validate(self, value):
        return bool(re.fullmatch(r"\d{10}", value))


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY instead")


class Address(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Address must be at least 2 characters long.")
        super().__init__(value)

    def validate(self, value):
        # check if the address is at least 2 characters long
        return len(value) >= 2


class Email(Field):  # add class for email
    def __init__(self, value):
        if not Email.validate(value):  # call the static validate method
            raise ValueError("Invalid email format.")
        super().__init__(value)

    @staticmethod
    def validate(value):  # add static method for validation
        return bool(
            re.fullmatch(
                r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$",
                value,
            )
        )


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = None
        self.phones = []
        self.email = None
        self.address = None

    def add_email(self, email):
        self.email = Email(email)  # add email to the record

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_address(self, address):
        self.address = Address(address)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return "Phone not found."

    def __str__(self):
        birthday_str = (
            datetime.strftime(self.birthday.value, "%d.%m.%Y")
            if self.birthday
            else "No birthday"
        )
        address = self.address.value if self.address else "no address"
        phones_str = "; ".join(p.value for p in self.phones)
        email_str = self.email.value if self.email else "No email"
        return f"Contact name: {self.name.value}, contact birthday: {birthday_str}, phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today()
        target_date = today + timedelta(days=days)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                # current year birthdays
                birthday_this_year = record.birthday.value.replace(year=today.year)

                # if birthday already passed this year, check next year's date
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Check if the birthday is in the specified range
                if today <= birthday_this_year <= target_date:
                    upcoming_birthdays.append(record.name.value)

        return upcoming_birthdays

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            return "Contact not found."


class Note:
    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __str__(self):
        return f"Title: {self.title}, Text: {self.text}"


class NoteBook(UserDict):
    def add_note(self, title, text):
        if title in self.data:
            return f"Note with the title '{title}' already exists."
        self.data[title] = Note(title, text)
        return "Note was added!"

    def delete_note(self, title):
        if title in self.data:
            del self.data[title]
            return f"Note '{title}' has been deleted.'"
        return f"Note '{title} was not found.'"

    def edit_note_title(self, old_title, new_title):
        """Edit the title of a note while keeping its content."""
        if old_title in self.data:
            self.data[new_title] = self.data.pop(
                old_title
            )  # Rename the note by moving it
            self.data[new_title].title = (
                new_title  # Update the title in the Note object
            )

    def edit_note_content(self, title, new_content):
        """Edit the content of an existing note."""
        if title in self.data:
            self.data[title].text = new_content


# Decorator to handle errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as er:
            return f"Error: {er}"

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args[0], args[1]
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "New contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)

    print(message)


@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args[0], args[1], args[2]
    record: Record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        print("Phone has been changed.")
    else:
        print("Contact not found.")


@input_error
def show_phone_numbers(args, book: AddressBook):
    name = args[0]
    record: Record = book.find(name)
    if record:
        phones = record.phones
        print("; ".join(p.value for p in phones))
    return "Contact not found."


@input_error
def show_all_contacts(book: AddressBook):
    is_empty = len(book.data) < 1
    if is_empty:
        print("Address book is empty.")
    else:
        print("\n".join(str(record) for record in book.data.values()))


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args[0], args[1]
    record: Record = book.find(name)
    if record:
        record.add_birthday(birthday)
        print(f"Birthday for {name} added")
    else:
        print("Contact not found.")


@input_error
def add_address(args, book: AddressBook):
    name = args[0]
    address = " ".join(args[1:])
    record: Record = book.find(name)
    if record:
        record.add_address(address)
        print(f"Address for {name} added")
    else:
        print("Contact not found")


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(
            f"{name}'s birthday: {datetime.strftime(record.birthday.value, '%d.%m.%Y')}"
        )
    elif record:
        print(f"{name} does not have a birthday set.")
    else:
        print("Contact not found.")


@input_error
def upcoming_birthdays(args, book: AddressBook):
    days = int(args[0]) if args and args[0].isdigit() else 7  # Use 7 days by default
    upcoming = book.get_upcoming_birthdays(days)
    if upcoming:
        print(f"Contacts with birthdays in {days} days: " + ", ".join(upcoming))
    else:
        print(f"No contacts with birthdays in {days} days.")


@input_error
def add_note(note_book: NoteBook):
    while True:
        title = input("Please enter note title: ").strip()
        if not title:
            print("Note title cannot be empty.")
        elif title in note_book.data:
            print(f"Note with the title '{title}' already exists.")
        else:
            break

    text = input("Please enter note content: ").strip()
    if not text:
        print(f"Your note '{title}' has not content.")

    note_book.add_note(title, text)

    print(f"Note successfully created! Title: '{title}', Text: '{text}'")


@input_error
def delete_note(args, note_book: NoteBook):
    title = args[0]
    message = note_book.delete_note(title)
    print(message)


@input_error
<<<<<<< HEAD
def add_email(args, book: AddressBook):
    name, email = args
    record = book.find(name)

    if record:
        record.add_email(email)
        print(f"Email for {name} added.")
    else:
        print("Contact not found.")
=======
def edit_note(note_book: NoteBook):
    # Step 1: Prompt for the current note title until a valid title is entered
    while True:
        old_title = input("Enter the title of the note you want to edit: ").strip()
        if old_title in note_book.data:
            print(f"Note with title '{old_title}' found.")  # Confirm title found
            break  # Exit the loop if the title is found
        print(f"Note with title '{old_title}' not found. Please try again.")

    note = note_book.data[old_title]  # Access the note to edit
    new_title = old_title  # Default to the current title in case it's not changed
    new_content = note.text  # Default to the current content in case it's not changed

    # Step 2: Choose what to edit
    while True:
        choice = (
            input("Would you like to edit the (T)itle, (C)ontent, (B)oth, or (E)xit? ")
            .strip()
            .lower()
        )
        if choice in ("t", "c", "b"):
            break  # Exit the loop if the input is valid
        elif choice == "e":
            print("Exiting the edit process.")
            return  # Exit the function without making changes
        else:
            print("Invalid choice. Please enter (T)itle, (C)ontent, (B)oth, or (E)xit.")

    # Edit the title if chosen
    if choice in ("t", "b"):
        while True:
            new_title_input = input("Enter the new title: ").strip()
            if not new_title_input:
                print("New title cannot be empty. Please try again.")
            elif new_title_input in note_book.data and new_title_input != old_title:
                print(
                    f"A note with the title '{new_title_input}' already exists. Please try again."
                )
            else:
                new_title = (
                    new_title_input or old_title
                )  # Use the new title if provided, otherwise keep the old one
                if new_title != old_title:
                    note_book.edit_note_title(old_title, new_title)
                break

    # Edit the content if chosen
    if choice in ("c", "b"):
        new_content_input = input("Enter the new content for the note: ").strip()
        if not new_content_input:
            print("Note content is empty.")  # Inform the user but still proceed to save
        new_content = (
            new_content_input or ""
        )  # Update with new content, even if it's empty
        if new_content != note.text:
            note_book.edit_note_content(new_title, new_content)

    # Print confirmation message including the updated note's title and content
    print(f"Note updated successfully!\nTitle: '{new_title}'\nContent: '{new_content}'")
>>>>>>> bc85b80 (feature/Edit-note)


def main():
    book = AddressBook()
    note_book = NoteBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split(maxsplit=1)
        args = args[0].split() if args else []

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            add_contact(args, book)

        elif command == "change":
            change_phone(args, book)

        elif command == "phone":
            show_phone_numbers(args, book)

        elif command == "all":
            show_all_contacts(book)

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "add-address":
            add_address(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            upcoming_birthdays(book)

        elif command == "add-note":
            add_note(note_book)

        elif command == "delete-note":
            delete_note(args, note_book)

<<<<<<< HEAD
        elif command == "add-email":
            add_email(args, book)
=======
        elif command == "edit-note":
            edit_note(note_book)
>>>>>>> bc85b80 (feature/Edit-note)

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
