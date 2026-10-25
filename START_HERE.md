# OLMS Release 1 — Windows and VS Code guide

This ZIP contains 10 application files, this guide, and a Git ignore file.
It implements staff login/logout, book registration, physical-copy records,
title/author search, book editing/deactivation/reactivation, member registration,
and active/inactive membership eligibility. Borrowing, returns and overdue
reports belong to later releases. Opening a folder does not start the server.

## 1. Before opening the project

Install Python 3.11 or newer from https://www.python.org/downloads/ and
VS Code from https://code.visualstudio.com/ if they are not already installed.
Select Add Python to PATH when offered. Reopen your terminal after installation.
In VS Code's Extensions panel, install Python by Microsoft.
Git is optional for running this release. SQLite is included with Python;
you do not need MySQL, Node.js, or a separate database server.

Open PowerShell and run each command separately:

    py --version
    py -m pip --version

Both should show version information. If py is not recognised, try python
instead, and use python instead of py in the environment creation command.

## 2. Extract and open

Right-click OLMS_Release1.zip, choose Extract All, and extract it.
In VS Code choose File > Open Folder. Select the OLMS_Release1 folder that
directly contains app.py and requirements.txt.
Choose Terminal > New Terminal. Run:

    dir

You should see app.py, requirements.txt, templates, static and START_HERE.md.
Do not run the application from inside the ZIP.

## 3. First-time environment setup

Run each command separately in that VS Code terminal:

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m pip show Flask

Internet access is required for the dependency installation. The last command
should show Flask 3.1.2. These commands use the environment directly; you do
not need to activate it or change PowerShell execution policy.

Press Ctrl+Shift+P, choose Python: Select Interpreter, and select the Python
inside .venv. If necessary choose Enter interpreter path and select
.venv\Scripts\python.exe inside this project.

## 4. Create a staff account once

    .\.venv\Scripts\python.exe app.py --create-staff

Choose a username and a password with at least 8 characters. Repeat the
password. No characters appear while typing the password; this is normal.
Successful setup displays Staff account created. There is no default account.

## 5. Start the application

    .\.venv\Scripts\python.exe app.py

Keep the terminal running. Open http://127.0.0.1:5000 in your browser.
Log in with the account you created. This is a local classroom application,
not a public production deployment. Separate computers have separate data.

## 6. Check every function in sequence

| Check | Action | Expected result |
|---|---|---|
| Login protection | Open http://127.0.0.1:5000/members while logged out | Login page |
| Staff login | Try an incorrect password, then the correct one | Incorrect rejected; correct opens catalogue |
| Book registration | Add Introduction to Python; author Ali Khan; edition First; 3 copies | Unique book ID and 3 unique copy IDs |
| Physical copies | View / Edit the book; add 2 copies | 5 unique copy IDs |
| Search | Search PYTHON, then khan | Both find the book |
| No match | Search zzzzunknown | No books found |
| Editing | Change the title to Python Basics | New title saved; book/copy IDs unchanged |
| Deactivation | Deactivate book, return to catalogue | Hidden from default catalogue |
| Inactive search | Select Include inactive books and Search | Book appears with 0 available copies |
| Reactivation | Open book and Reactivate book | Same IDs; 5 available copies again |
| Member registration | Register Test Student as Active | Unique member ID |
| Eligibility | Click Check eligibility | ELIGIBLE |
| Inactive member | Deactivate member; check eligibility | NOT ELIGIBLE |
| Reactivation | Activate member; check again | ELIGIBLE |
| Validation | Submit missing names or invalid copy counts | No invalid record saved |
| Logout | Log out and open catalogue | Login required again |
| Persistence | Stop server, restart, log in | All records retained |

Record tester name, date, expected result, actual result and pass/fail for your
team presentation. Browser validation may block invalid input before submission;
server-side validation also checks it.

Availability starts at the copy count for active books. No actual loans are
created in this release. Eligibility checks only membership status. Release 2
must enforce that check again when issuing a copy. Deactivation preserves book
and copy records; actual loan-link preservation must be checked after Release 2.

## 7. Stop and run next time

Press Ctrl+C in the server terminal to stop.
Next time, open the same folder and run only:

    .\.venv\Scripts\python.exe app.py

Then open http://127.0.0.1:5000. Do not recreate your account or environment.

## 8. File map

| Application file | Purpose |
|---|---|
| app.py | Routes, authentication, validation and SQLite operations |
| requirements.txt | Python dependencies |
| templates/base.html | Shared page layout and navigation |
| templates/login.html | Login form |
| templates/catalogue.html | Book list and search |
| templates/add_book.html | Book registration |
| templates/book_details.html | Editing, status and physical copies |
| templates/members.html | Member registration and status |
| templates/eligibility.html | Membership eligibility |
| static/style.css | Shared page styling |

Additional files: START_HERE.md is this guide; .gitignore excludes local data
and the Python environment from Git.

The application automatically creates instance/olms.sqlite3 (all records)
and instance/secret.key (login-session signing key). Do not delete them.
To back up, stop the server and copy the whole instance folder somewhere safe.
Do not share that folder in your source-code ZIP or commit it to Git.

## 9. Troubleshooting

| Problem | Solution |
|---|---|
| py not recognised | Try python; otherwise install Python and reopen terminal |
| No module named flask | Run the dependency install command above with .venv's Python |
| Cannot open app.py | Open the inner project folder containing app.py |
| Browser cannot connect | Start the server and keep its terminal running |
| Port 5000 already in use | Stop the previous OLMS server with Ctrl+C |
| Password invisible | Normal; type and press Enter |
| Form expired | Reload page, then submit again |
| Forgotten password | Run --create-staff and choose a new username |
| pip cannot download | Check internet access and retry without disabling certificate checks |

## Validation of this package

Automated Flask test-client checks were run against an isolated temporary
database for authentication, all seven feature areas, validation, CSRF,
HTML escaping, and persistence across application contexts. This does not
replace checking installation and browser appearance on your Windows machine.
