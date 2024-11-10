import re
import pickle
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
            raise ValueError("[red]Invalid date format. Use DD.MM.YYYY instead.[/red]")


class Address(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("[red]Address must be at least 2 characters long.[/red]")
        super().__init__(value)

    def validate(self, value):
        # check if the address is at least 2 characters long
        return len(value) >= 2


class Email(Field):  # add class for email
    def __init__(self, value):
        if not Email.validate(value):  # call the static validate method
            raise ValueError("[red]Invalid email format.[/red]")
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
        return ":telephone_receiver: [indian_red]Phone not found.[/indian_red]"

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
            return ":point_right: [indian_red]Contact not found.[/indian_red]"


class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.tags = []

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def __str__(self):
        tags_str = ", ".join(self.tags) if self.tags else "No tags"
        return f"[cornflower_blue]Title:[/cornflower_blue] {self.title}, [cornflower_blue]Content:[/cornflower_blue] {self.content}, [cornflower_blue]Tags:[/cornflower_blue] {tags_str}"


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
        return f":point_right: [indian_red]Note[/indian_red] '{title}' [indian_red]was not found.[/indian_red]"

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
            console.print(f"[red]Error: {er}[/red]")

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
        console.print(":point_right: [indian_red]Contact not found.[/indian_red]")


@input_error
def show_phone_numbers(args, book: AddressBook):
    name = args[0]
    record: Record = book.find(name)
    if record:
        phones = record.phones
        print("; ".join(p.value for p in phones))
    return f":point_right: [indian_red]Contact not found.[/indian_red]"


@input_error
def show_all_contacts(book: AddressBook):
    is_empty = len(book.data) < 1
    if is_empty:
        console.print("[yellow]Address book is empty.[/yellow]")
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
        console.print(f"[medium_purple3]Birthday for {name} added.[/medium_purple3]")
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
        console.print(f":point_right: [indian_red]Contact not found.[/indian_red]")


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
        console.print(f":point_right: [indian_red]Contact not found.[/indian_red]")


@input_error
def upcoming_birthdays(args, book: AddressBook):
    days = int(args[0]) if args and args[0].isdigit() else 7  # Use 7 days by default
    upcoming = book.get_upcoming_birthdays(days)
    if upcoming:
        console.print(
            f"[medium_purple3]Contacts with birthdays in {days} days: [/medium_purple3] :tada:"
            + ", ".join(upcoming)
        )
    else:
        console.print(
            f":calendar: [medium_purple3]No contacts with birthdays in {days} days.[/medium_purple3]"
        )


@input_error
def add_note(note_book: NoteBook):
    while True:
        title = input("Please enter note title: ").strip()
        if not title:
            console.print("[yellow]Note title cannot be empty.[/yellow]")
        elif title in note_book.data:
            console.print(
                f":point_right: [indian_red]Note with the title '{title}' already exists.[/indian_red]"
            )
        else:
            break

    content = input("Please enter note content: ").strip()

    note_book.add_note(title, content)

    console.print(
        f"[blue]Note successfully created! Title:[/blue] '{title}'[blue], Content: [/blue]'{content}'"
    )


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
    new_title = current_title  # Default to current title unless changed
    if choice in ("t", "b"):
        while True:
            new_title_input = input("Enter the new title: ").strip()
            if not new_title_input:
                console.print(
                    "[indian_red]New title cannot be empty. Please try again.[/indian_red]"
                )
            elif new_title_input in note_book.data and new_title_input != current_title:
                console.print(
                    f"[indian_red]A note with the title[/indian_red] '{new_title_input}' [indian_red]already exists. Please try again.[/indian_red]"
                )
            else:
                note_book.edit_note_title(current_title, new_title_input)
                new_title = new_title_input  # Update new title for content editing
                break

    # Edit the content if chosen
    if choice in ("c", "b"):
        new_content_input = input("Enter the new content for the note: ").strip()
        if not new_content_input:
            console.print(
                "[indian_red]Note content is empty.[/indian_red]"
            )  # Inform the user but still proceed to save
        note_book.edit_note_content(new_title, new_content_input)

    console.print("[yellow]Note updated successfully![/yellow]")


@input_error
def show_all_notes(note_book: NoteBook):
    is_empty = len(note_book.data) < 1
    if is_empty:
        console.print("[yellow]Notes book is empty.[/yellow]")
        return

    table = Table(title=":notebook: [bold turquoise4]Notes Book[/bold turquoise4]")
    table.add_column("Title", justify="center", style="cyan", no_wrap=True)
    table.add_column("Content", justify="center", style="green")
    table.add_column("Tag", justify="center", style="medium_purple3")

    for note in note_book.data.values():
        tags_str = ", ".join(note.tags) if note.tags else "No tags"
        table.add_row(
            f"{note.title}", f"{note.content}", tags_str
        )

    console.print(table)


@input_error
def delete_note(args, note_book: NoteBook):
    title = " ".join(args[:])
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
        console.print(":point_right: [indian_red]Contact not found.[/indian_red]")


@input_error
def search_note(args, note_book: NoteBook):
    query = " ".join(args).strip().lower()

    if not query:
        console.print("[indian_red]Search query should not be empty.[/indian_red]")
        return

    results = [
        note
        for note in note_book.data.values()
        if query in note.title.lower() or query in note.content.lower()
    ]

    if results:
        table = Table(
            title=":magnifying_glass_tilted_right: [bold turquoise4]Search Results[/bold turquoise4]"
        )
        table.add_column("Title", justify="center", style="cyan", no_wrap=True)
        table.add_column("Content", justify="center", style="green")
        table.add_column("Tag", justify="center", style="medium_purple3")

        for note in results:
            tags_str = (
                ", ".join(note.tags) if note.tags else "No tags"
            )
            table.add_row(note.title, note.content, tags_str)

        console.print(table)
    else:
        console.print("[indian_red]No matching notes found.[/indian_red]")


@input_error
def add_tag(note_book: NoteBook):
    note_title = input("Note title: ").strip()

    if note_title not in note_book.data:
        console.print(f"[indian_red]Note with title '{note_title}' not found.[/indian_red]")
        return

    tag = input("Note tag to add: ").strip()
    if not tag:
        console.print("[indian_red]Tag cannot be empty.[/indian_red]")
        return

    note = note_book.data[note_title]
    note.add_tag(tag)
    console.print(
        f"[cyan3]Tag[/cyan3] '{tag}' [cyan3]successfully added to note[/cyan3] '{note_title}'[cyan3]![/cyan3]"
    )


def show_menu():
    """Displays the menu with available commands"""
    commands = """
    [bold]Contacts:[/bold]
    [cyan3]add-contact <name> <phone>[/cyan3]                   - Add new contact with a phone number
    [cyan3]add-birthday <name> <birthday>[/cyan3]               - Add birthday for a contact
    [cyan3]add-address <name> <address>[/cyan3]                 - Add contact's address
    [cyan3]add-email <name> <email>[/cyan3]                     - Add or update contact's email
    [cyan3]change-phone <name> <old_phone> <new_phone>[/cyan3]  - Change contact's phone number
    [cyan3]show-phone <name>[/cyan3]                            - Show contact's phone numbers
    [cyan3]show-birthday <name>[/cyan3]                         - Show contact's birthday
    [cyan3]birthdays <days>[/cyan3]                             - Show prospects with upcoming birthdays
    [cyan3]all-contacts[/cyan3]                                 - Show all contacts

    [bold]Notes:[/bold]
    [sky_blue1]add-note[/sky_blue1]                                     - Add a new note
    [sky_blue1]edit-note[/sky_blue1]                                    - Edit a note
    [sky_blue1]all-notes[/sky_blue1]                                    - Show all notes
    [sky_blue1]delete-note <title>[/sky_blue1]                          - Delete note
    [sky_blue1]search-note <query>[/sky_blue1]                          - Search note
    [sky_blue1]note-add-tag[/sky_blue1]                                 - Add tag

    [bold]Exit:[/bold]
    [dark_orange]close / exit[/dark_orange]                                 - Exit the application
    """

    # Print table with commands
    console.print(
        Panel(
            commands,
            title="[khaki1]:sparkles: List of bot commands :sparkles:[/khaki1]",
            expand=False,
        )
    )


def save_address_book(address_book: AddressBook, file_name: str = "address_book.pkl"):
    with open(file_name, "wb") as f:
        pickle.dump(address_book, f)


def load_address_book(file_name: str = "address_book.pkl"):
    try:
        with open(file_name, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def save_note_book(note_book: NoteBook, file_name: str = "note_book.pkl"):
    with open(file_name, "wb") as f:
        pickle.dump(note_book, f)


def load_note_book(file_name: str = "note_book.pkl"):
    try:
        with open(file_name, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return NoteBook()


def main():
    note_book = load_note_book()
    address_book = load_address_book()
    console.print(":robot: [bold blue]Welcome to the assistant bot![/bold blue] :wave:")
    show_menu()

    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split(maxsplit=1)
        args = args[0].split() if args else []

        if command in ["close", "exit"]:
            save_note_book(note_book)
            save_address_book(address_book)
            console.print(":wave: [bold green]Good bye![/bold green]")
            break

        elif command == "hello":
            console.print(":smiley: [yellow]How can I help you?[/yellow]")

        elif command == "add-contact":
            add_contact(args, address_book)

        elif command == "change-phone":
            change_phone(args, address_book)

        elif command == "show-phone":
            show_phone_numbers(args, address_book)

        elif command == "all-contacts":
            show_all_contacts(address_book)

        elif command == "add-birthday":
            add_birthday(args, address_book)

        elif command == "add-address":
            add_address(args, address_book)

        elif command == "add-email":
            add_email(args, address_book)

        elif command == "show-birthday":
            show_birthday(args, address_book)

        elif command == "birthdays":
            upcoming_birthdays(args, address_book)

        elif command == "add-note":
            add_note(note_book)

        elif command == "edit-note":
            edit_note(note_book)

        elif command == "all-notes":
            show_all_notes(note_book)

        elif command == "delete-note":
            delete_note(args, note_book)

        elif command == "search-note":
            search_note(args, note_book)

        elif command == "note-add-tag":
            add_tag(note_book)

        else:
            console.print("[red]Invalid command. Please try again![/red]")


if __name__ == "__main__":
    main()
