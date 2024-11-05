# Address Book Bot

Address Book Bot is a command-line-based contact management system that allows users to store and manage contacts, including phone numbers and birthdays. The bot offers functionalities for adding, editing, deleting, and viewing contact information, as well as listing upcoming birthdays.

## Features

- **Add and Edit Contacts**: Add new contacts with names, phone numbers, and birthdays.
- **Manage Phone Numbers**: Easily add, update, or delete phone numbers for existing contacts.
- **Birthday Management**: Add birthdays to contacts and retrieve upcoming birthdays within the next week.
- **Error Handling**: Provides clear feedback for incorrect input with custom error handling.
- **User-Friendly Commands**: Simple, intuitive commands for quick access to all functionalities.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/address-book-bot.git
   cd address-book-bot
   ```

# Adding a new contact with a phone number

> add John 1234567890
> Contact added.

# Adding a birthday for a contact

> add-birthday John 01.01.1990
> Birthday for John added.

# Changing a contact's phone number

> change John 1234567890 0987654321
> Phone has been changed.

# Showing a contact's phone numbers

> phone John
> 0987654321

# Showing all contacts

> all
> Contact name: John, contact birthday: 01.01.1990, phones: 0987654321

# Checking upcoming birthdays within a week

> birthdays
> Upcoming birthdays in the next week: John
