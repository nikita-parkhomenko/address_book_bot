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
        self.email = None  # add field for email

    def add_email(self, email):
        self.email = Email(email)  # add email to the record

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

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
        phones_str = "; ".join(p.value for p in self.phones)
        email_str = self.email.value if self.email else "No email"
        return f"Contact name: {self.name.value}, contact birthday: {birthday_str}, phones: {phones_str}, email: {email_str}"


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
    email = args[2] if len(args) > 2 else None  # Додаємо email, якщо він вказаний
    record = book.find(name)
    if record is None:
        record = Record(name)
        print(f"new record created: {record}")
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)
    if email:
        record.add_email(email)  # Додаємо email, якщо він є
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
def add_email(args, book: AddressBook): # Додаємо поле email
    name, email = args
    record = book.find(name)

    if record:
        record.add_email(email)
        print(f"Email for {name} added.")
    else:
        print("Contact not found.")


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

        elif command == "phone": # може потрібно назвати команду "show-phone"?
            show_phone_numbers(args, book)

        elif command == "all":
            show_all_contacts(book)

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            upcoming_birthdays(book)

        elif command == "add-note":
            add_note(note_book)

        elif command == "delete-note":
            delete_note(args, note_book)

        elif command == "add-email":
            add_email(args, book)

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
