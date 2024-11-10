import re
from collections import UserDict
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich import print
from rich.panel import Panel


console = Console()


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
            raise ValueError(
                ":red_circle: [red]Invalid date format. Use DD.MM.YYYY instead.[/red]"
            )


class Address(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError(
                ":red_circle: [red]Address must be at least 2 characters long.[/red]"
            )
        super().__init__(value)

    def validate(self, value):
        # check if the address is at least 2 characters long
        return len(value) >= 2


class Email(Field):  # add class for email
    def __init__(self, value):
        if not Email.validate(value):  # call the static validate method
            raise ValueError(":red_circle: [red]Invalid email format.[/red]")
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
        return ":telephone_receiver: [red]Phone not found.[/red]"

    def __str__(self):
        birthday_str = (
            datetime.strftime(self.birthday.value, "%d.%m.%Y")
            if self.birthday
            else "No birthday"
        )
        address = self.address.value if self.address else "No address"
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
            return "[indian_red]Contact not found.[/indian_red]"


class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __str__(self):
        return f"[cornflower_blue]Title:[/cornflower_blue] {self.title}, [cornflower_blue]Content:[/cornflower_blue] {self.content}"


class NoteBook(UserDict):
    def add_note(self, title, content):
        if title in self.data:
            return f"[yellow]Note with the title[/yellow] '{title}' [yellow]already exists.[/yellow]"
        self.data[title] = Note(title, content)
        return "[sky_blue3]Note was added![/sky_blue3]"

    def delete_note(self, title):
        if title in self.data:
            del self.data[title]
            return f"[cornflower_blue]Note[/cornflower_blue] '{title}' [cornflower_blue]has been deleted.[/cornflower_blue]"
        return f"[indian_red]Note[/indian_red] '{title}' [indian_red]was not found.[/indian_red]"

    def edit_note_title(self, current_title, new_title):
        """Edit the title of a note while keeping its content."""
        if current_title in self.data:
            self.data[new_title] = self.data.pop(
                current_title
            )  # Rename the note by moving it
            self.data[new_title].title = (
                new_title  # Update the title in the Note object
            )

    def edit_note_content(self, title, new_content):
        """Edit the content of an existing note."""
        if title in self.data:
            self.data[title].content = new_content


# Decorator to handle errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as er:
            print(f"[red]Error: {er}[/red]")

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args[0], args[1]
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"[green]New contact added.[/green]"
    else:
        message = f"[yellow]Contact updated.[/yellow]"
    record.add_phone(phone)

    print(message)


@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args[0], args[1], args[2]
    record: Record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        console.print(":ok_hand: [yellow]Phone has been changed.[/yellow]")
    else:
        console.print("[indian_red]Contact not found.[/indian_red]")


@input_error
def show_phone_numbers(args, book: AddressBook):
    name = args[0]
    record: Record = book.find(name)
    if record:
        phones = record.phones
        print("; ".join(p.value for p in phones))
    return f"[indian_red]Contact not found.[/indian_red]"


@input_error
def show_all_contacts(book: AddressBook):
    is_empty = len(book.data) < 1
    if is_empty:
        console.print("[bold yellow]Address book is empty.[/bold yellow]")
        return

    table = Table(title=":open_book: Address Book")
    table.add_column("Name", justify="center", style="cyan", no_wrap=True)
    table.add_column("Birthday", justify="center", style="medium_purple3")
    table.add_column("Phones", justify="center", style="green")
    table.add_column("Email", justify="center", style="green_yellow")
    table.add_column("Address", justify="center", style="blue")

    for record in book.data.values():
        birthday_str = (
            datetime.strftime(record.birthday.value, "%d.%m.%Y")
            if record.birthday
            else "No birthday"
        )
        phones_str = "; ".join(p.value for p in record.phones) or "No phones"
        email_str = record.email.value if record.email else "No email"
        address_str = record.address.value if record.address else "No address"

        table.add_row(
            f":bust_in_silhouette: {record.name.value}",
            birthday_str,
            phones_str,
            email_str,
            address_str,
        )

    console.print(table)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args[0], args[1]
    record: Record = book.find(name)
    if record:
        record.add_birthday(birthday)
        console.print(f"[medium_purple3]Birthday for {name} added[/medium_purple3]")
    else:
        console.print(f":point_right: [indian_red]Contact not found.[/indian_red]")


@input_error
def add_address(args, book: AddressBook):
    name = args[0]
    address = " ".join(args[1:])
    record: Record = book.find(name)
    if record:
        record.add_address(address)
        console.print(f"[blue]Address for {name} added.[/blue]")
    else:
        console.print(f"[indian_red]Contact not found.[/indian_red]")


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        console.print(
            f"{name}'s birthday: {datetime.strftime(record.birthday.value, '%d.%m.%Y')}"
        )
    elif record:
        console.print(f"[yellow]{name} does not have a birthday set.[/yellow]")
    else:
        console.print(f"[indian_red]Contact not found.[/indian_red]")


@input_error
def upcoming_birthdays(args, book: AddressBook):
    days = int(args[0]) if args and args[0].isdigit() else 7  # Use 7 days by default
    upcoming = book.get_upcoming_birthdays(days)
    if upcoming:
        console.print(f"Contacts with birthdays in {days} days: " + ", ".join(upcoming))
    else:
        console.print(f"No contacts with birthdays in {days} days.")


@input_error
def add_note(note_book: NoteBook):
    while True:
        title = input("Please enter note title: ").strip()
        if not title:
            console.print("Note title cannot be empty.")
        elif title in note_book.data:
            console.print(f"Note with the title '{title}' already exists.")
        else:
            break

    content = input("Please enter note content: ").strip()
    if not content:
        console.print(f"Your note '{title}' has not content.")

    note_book.add_note(title, content)

    console.print(f"Note successfully created! Title: '{title}', Content: '{content}'")


def edit_note(note_book: NoteBook):
    # Step 1: Prompt for the current note title until a valid title is entered
    while True:
        current_title = input("Enter the title of the note you want to edit: ").strip()
        if current_title in note_book.data:
            break  # Exit the loop if the title is found
        console.print(
            f"[yellow]Note with title '{current_title}' not found. Please try again.[/yellow]"
        )

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
            console.print("[sky_blue1]Exiting the edit process.[/sky_blue1]")
            return  # Exit the function without making changes
        else:
            console.print(
                "[indian_red]Invalid choice. Please enter (T)itle, (C)ontent, (B)oth, or (E)xit.[/indian_red]"
            )

    # Edit the title if chosen
    if choice in ("t", "b"):
        while True:
            new_title_input = input("Enter the new title:").strip()
            if not new_title_input:
                console.print(
                    "[indian_red]New title cannot be empty. Please try again.[/indian_red]"
                )
            elif new_title_input in note_book.data and new_title_input != current_title:
                console.print(
                    f"A note with the title '{new_title_input}' already exists. Please try again."
                )
            else:
                note_book.edit_note_title(current_title, new_title_input)
                break

    # Edit the content if chosen
    if choice in ("c", "b"):
        new_content_input = input("Enter the new content for the note: ").strip()
        if not new_content_input:
            console.print(
                "[indian_red]Note content is empty.[/indian_red]"
            )  # Inform the user but still proceed to save
        note_book.edit_note_content(new_title_input, new_content_input)

    console.print("[yellow]Note updated successfully![/yellow]")


@input_error
def show_all_notes(note_book: NoteBook):
    is_empty = len(note_book.data) < 1
    if is_empty:
        console.print("[indian_red]Notes book is empty.[/indian_red]")
        return

    table = Table(title=":notebook: Notes Book")
    table.add_column("Title", justify="center", style="cyan", no_wrap=True)
    table.add_column("Content", justify="center", style="green")

    for note in note_book.data.values():
        table.add_row(f"{note.title}", f"{note.content}")

    console.print(table)


@input_error
def delete_note(args, note_book: NoteBook):
    title = args[0]
    message = note_book.delete_note(title)
    print(message)


@input_error
def add_email(args, book: AddressBook):
    name, email = args
    record = book.find(name)

    if record:
        record.add_email(email)
        console.print(f"[green_yellow]Email for {name} added.[/green_yellow]")
    else:
        console.print("[indian_red]Contact not found.[/indian_red]")


def show_menu():
    """Виводить меню з доступними командами"""
    commands = """
    [bold]Контакти:[/bold]
    [cyan3]add <name> <phone>[/cyan3]                           - Додати новий контакт з телефоном
    [cyan3]add-birthday <name> <birthday>[/cyan3]               - Додати день народження для контакту
    [cyan3]add-address <name> <address>[/cyan3]                 - Додати адресу для контакту
    [cyan3]add-email <name> <email>[/cyan3]                     - Додати або оновити email контакту
    [cyan3]change <name> <old_phone> <new_phone>[/cyan3]        - Змінити телефон контакту
    [cyan3]phone <name>[/cyan3]                                 - Показати номери телефонів контакту
    [cyan3]show-birthday <name>[/cyan3]                         - Показати день народження контакту
    [cyan3]birthdays <days>[/cyan3]                             - Показати контакти з найближчими днями народження
    [cyan3]all[/cyan3]                                          - Показати всі контакти

    [bold]Нотатки:[/bold]
    [sky_blue1]add-note <title> <text>[/sky_blue1]                      - Додати нову нотатку
    [sky_blue1]edit-note[/sky_blue1]                                    - Редагувати нотатку
    [sky_blue1]all-notes[/sky_blue1]                                    - Показати всі нотатки
    [sky_blue1]delete-note <title>[/sky_blue1]                          - Видалити нотатку

    [bold]Вихід:[/bold]
    [dark_orange]close / exit[/dark_orange]                                 - Вийти з програми
    """

    # Виводимо меню з рамкою
    console.print(
        Panel(
            commands,
            title="[bold light_sky_blue3]:sparkles: Список команд бота :sparkles:[/bold light_sky_blue3]",
            expand=False,
        )
    )


def main():
    book = AddressBook()
    note_book = NoteBook()
    console.print(":robot: [bold blue]Welcome to the assistant bot![/bold blue] :wave:")
    show_menu()

    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split(maxsplit=1)
        args = args[0].split() if args else []

        if command in ["close", "exit"]:
            console.print(":wave: [green]Good bye![/green]")
            break

        elif command == "hello":
            console.print(":smiley: [yellow]How can I help you?[/yellow]")

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
            upcoming_birthdays(args, book)

        elif command == "add-note":
            add_note(note_book)

        elif command == "edit-note":
            edit_note(note_book)

        elif command == "all-notes":
            show_all_notes(note_book)

        elif command == "delete-note":
            delete_note(args, note_book)

        elif command == "add-email":
            add_email(args, book)

        else:
            console.print(
                ":exclamation: [bold red]Invalid command. Please try again![/bold red]"
            )


if __name__ == "__main__":
    main()
