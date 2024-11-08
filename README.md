# Address Book Bot

Address Book Bot is a command-line-based contact management system that allows users to store and manage contacts, including phone numbers and birthdays. The bot offers functionalities for adding, editing, deleting, and viewing contact information, as well as listing upcoming birthdays.

## Features

- **Add and Edit Contacts**: Add new contacts with names, phone numbers, and birthdays.
- **Manage Phone Numbers**: Easily add, update, or delete phone numbers for existing contacts.
- **Birthday Management**: Add birthdays to contacts and retrieve upcoming birthdays within the next week.
- **Error Handling**: Provides clear feedback for incorrect input with custom error handling.
- **User-Friendly Commands**: Simple, intuitive commands for quick access to all functionalities.

## How to install

1. **Clone the repository**:

   ```bash
   git clone https://github.com/nikita-parkhomenko/address_book_bot.git
   cd address-book-bot
   python main.py
   ```

## Commands

### Note Management

- **add-note**: Adds a new note by entering a title and content.
- **edit-note**: Prompts you to edit a note's title or content.
- **all-notes**: Displays all notes in the notes book.
- **delete-note <title>**: Deletes a note by its title.

### Contact Management

- **hello**: Greets the user and provides an introductory message.
- **add <name> <phone>**: Adds a new contact with the specified name and phone number. If the contact exists, it updates the phone number.
- **change <name> <old_phone> <new_phone>**: Updates a contact’s phone number.
- **phone <name>**: Displays all phone numbers associated with the contact.
- **all**: Shows all contacts in the address book.
- **add-birthday <name> <birthday>**: Adds or updates the birthday for the specified contact. The birthday format should be `DD.MM.YYYY`.
- **add-address <name> <address>**: Adds or updates the address for the specified contact.
- **show-birthday <name>**: Displays the birthday of the specified contact.
- **birthdays <days>**: Lists contacts with upcoming birthdays within the specified number of days.
- **add-email <name> <email>**: Adds or updates the email for the specified contact.

### Exiting the Bot

- **exit** or **close**: Closes the bot and ends the session.
