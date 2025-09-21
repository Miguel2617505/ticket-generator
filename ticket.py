import sqlite3
import re
import pandas as pd
import shutil
from datetime import datetime
"""
This program is useful to create tickets from users and
prioritize since the most highest to the lowest
CRUD phases
"""
#create connection and cursor
connection = sqlite3.connect("ticket_data_base.db") 
cursor = connection.cursor()

#CREATE phase 
#create Table 
cursor.execute('''
      CREATE TABLE IF NOT EXISTS Tickets (
            id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
            id_client INTEGER NOT NULL,
            email  TEXT NOT NULL, 
            description TEXT NOT NULL,
            priority TEXT CHECK (priority IN ("High", "Medium", "Low")) DEFAULT "Medium",
            status TEXT DEFAULT "Open",
            creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
''')

#Create function to get the user info
def create_ticket():
#Variables to get user data
    priority = ["High", "Medium", "Low"]
#create the loop to ask the information to the user
    while True:
        #ask user´s ID
        while True:
            try: 
               id_client = int(input("Enter your ID: "))
            except ValueError:
              print("You must enter a number")
              continue
            print(f"Customer's ID: {id_client}")
            break
        #ask the email and try if it works or is invalid
        while True:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            email_user = input("Enter your email please: ")    
            if not re.match(pattern, email_user):
               print(f"Invalid email. Please enter a valid email address.")
               continue
            else:
               print(f"Email: {email_user}")   
               break
        #Decription of user issue
        while True:
            description_user = input("Brief description of your issue: ").strip()
            if not description_user:
               print("You must enter the brief description")
               continue
            else:
                print(f"Issue: {description_user}")
                break
        #priority 
        while True:
            priority_user = input("Priority level (High, Medium ,Low): ").strip().capitalize()
            if priority_user not in priority:
               print("Error: Invalid input, only permited: High, Medium, Low") 
               continue
            else:
               print(f"Thanks, the priority level is {priority_user}")
               break
        query = "INSERT INTO Tickets (id_client, email, description, priority) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (id_client, email_user, description_user, priority_user))
        connection.commit()
        print(f"✅ Ticket successfully created. Ticket ID: {cursor.lastrowid} ✅")
        break
        #ASk the user if wants to add a new ticket or not 
def create_tickets_loop():        
    while True: 
        create_ticket()
        create_other = input("Do you want to create a new ticket (Yes/No)? ").capitalize()
        if create_other == "No": 
           print("✅ Ticket session finished. Exiting system...")
           break

#READ phase

#Print and create the ticket 
def read_tickets():
    print("\n--- Tickets currently in database ---")
    cursor.execute("""
        SELECT id_ticket, id_client, email, description, priority, status 
        FROM Tickets 
        ORDER BY 
            CASE priority 
                WHEN 'High' THEN 1 
                WHEN 'Medium' THEN 2 
                WHEN 'Low' THEN 3 
            END,
            creation_date
    """)
    
    rows = cursor.fetchall()

    if not rows:
        print("❌ No tickets found in the database.")
        return

    # Mostrar encabezados
    print(f"{'ID':<5} {'Client ID':<10} {'Email':<25} {'Description':<25} {'Priority':<10} {'Status'}")
    print("-" * 85)

    # Imprimir cada ticket
    for row in rows:
        id_ticket = row[0]
        id_client = row[1]
        email = row[2]
        description = row[3][:22] + "..." if len(row[3]) > 25 else row[3]
        priority = row[4]
        status = row[5]

        print(f"{id_ticket:<5} {id_client:<10} {email:<25} {description:<25} {priority:<10} {status}")

#UPDATE phase
def update_ticket():
    # Show the current tickets on file 
    print("\n------ Available Tickets ------")
    cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status 
                      FROM Tickets ORDER BY creation_date""")
    rows = cursor.fetchall()
    if not rows:
        print("No tickets found in the database.")
        return
    
    for row in rows:
        print(f"ID: {row[0]} | Client: {row[1]} | Email: {row[2]} | Desc: {row[3][:20]}... | Priority: {row[4]} | Status: {row[5]}")

    # ASK FOR TICKET ID
    while True:
        try:
            ticket_id = int(input("\nSelect the ticket ID you want to update: "))
            cursor.execute("SELECT * FROM Tickets WHERE id_ticket = ?", (ticket_id,))
            ticket = cursor.fetchone()
            if ticket:
                break
            else:
                print("❌ Ticket ID not found. Please try again.")
        except ValueError:
            print("❌ You must enter a number.")

    # UPDATE MENU
    while True:
        print("\nWhat do you want to update?")
        print("1. Email")
        print("2. Description")
        print("3. Priority")
        print("4. Status")
        print("5. Cancel")

        choice = input("Enter option number: ")

        #email option 
        if choice == "1":
            while True:
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                new_email = input("Enter the new email please: ")    
                if not re.match(pattern, new_email):
                   print(f"Invalid email. Please enter a valid email address.")
                   continue
                else:
                    print(f"Email: {new_email}")   
                    break
            if new_email:
                cursor.execute("UPDATE Tickets SET email = ? WHERE id_ticket = ?",
                               (new_email, ticket_id))
                connection.commit()
                print("✅ Email updated successfully.")
            else:
                print("❌ Email cannot be empty.")
        #Description option
        if choice == "2":
            new_description = input("Enter new description: ").strip()
            if new_description:
                cursor.execute("UPDATE Tickets SET description = ? WHERE id_ticket = ?", 
                               (new_description, ticket_id))
                connection.commit()
                print("✅ Description updated successfully.")
            else:
                print("❌ Description cannot be empty.")
        #Prority option
        elif choice == "3":
            while True:
                new_priority = input("Enter new priority (High/Medium/Low): ").capitalize()
                if new_priority in ["High", "Medium", "Low"]:
                    cursor.execute("UPDATE Tickets SET priority = ? WHERE id_ticket = ?", 
                                   (new_priority, ticket_id))
                    connection.commit()
                    print("✅ Priority updated successfully.")
                    break
                else:
                    print("❌ Invalid priority. Try again.")
         #Status option 
        elif choice == "4":
            while True:
                new_status = input("Enter new status (Open/In Progress/Closed): ").title()
                if new_status in ["Open", "In Progress", "Closed"]:
                    cursor.execute("UPDATE Tickets SET status = ? WHERE id_ticket = ?", 
                                   (new_status, ticket_id))
                    connection.commit()
                    print("✅ Status updated successfully.")
                    break
                else:
                    print("❌ Invalid status. Try again.")
        #Cancel option in case the user doesn't want to update nothing
        elif choice == "5":
            print("Update cancelled.")
            break
        else:
            print("❌ Invalid option. Try again.")

        # ASk if he wants to make a change in the same ticket
        more = input("Do you want to update another field for this ticket? (Yes/No): ").capitalize()
        if more == "No":
            break

#DELETE phase 
def delete_ticket():
    #show tickets on file
    print("------Choose ticket you want to delete---------")
    cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status 
                   FROM Tickets ORDER BY creation_date""")
    rows = cursor.fetchall()
    if not rows:
        print("No tickets to delete in your database")
        return
    for row in rows: 
        print(f"ID:{row[0]} | Client ID: {row[1]} | Email: {row[2]} | Description: {row[3][:20]} | Priority: {row[4]} | Status: {row[5]}")
    
    #ask for the ticket to DELETE
    
    while True:
        try:
            ticket_delete = int(input("Select the Ticket ID you want to DELETE: "))
            cursor.execute("SELECT * FROM Tickets WHERE id_ticket = ?", (ticket_delete,))
            ticket = cursor.fetchone()
            if ticket:
                break
            else:
                print("❌ Ticket ID not found. Please try again.")
        except ValueError:
            print("❌ You must enter a number.")
        
    #confirm ticket deletion
    while True:
        confirm = input(f"Are you sure to delete the ticket {ticket_delete}? (Yes/No): ").capitalize()
        if confirm == "Yes":
            cursor.execute("DELETE FROM Tickets WHERE id_ticket = ?", (ticket_delete,))
            connection.commit()
            print(f"✅ Ticket ID {ticket_delete} deletion successfully.")
            break
        elif confirm == "No":
            print("✅ Deletion cancelled.")
            break
        else: 
            print("❌Invalid option. Type 'Yes' or 'No'. ")

#Add some filter just in case
def filter_tickets():
    while True:
        print("----Search and filter Menu----")
        print("1. Do you know the ID?: ")
        print("2. Email: ")
        print("3. Status type: (Open /In progress / Closed): ")
        print("4. Priority: (High, Medium, Low): ")
        print("5. Back to main menu")

        option = input("Select the option (1-5): ")

        #Filter by ID
        if option == "1":
            try:
                ticket_id = int(input("Enter the ticket ID: "))
                cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status
                               FROM Tickets WHERE id_ticket = ?""", (ticket_id,))
                ticket = cursor.fetchone()
                if ticket:
                    print("\n Found Ticket: ")
                    print(f"ID:{ticket[0]} | Client ID: {ticket[1]} | Email: {ticket[2]} | Description: {ticket[3][:20]} | Priority: {ticket[4]} | Status: {ticket[5]}")
                else: 
                    print("❌ Ticket not found.")
            except ValueError:
                print("❌ Invalid ID. please enter a number")
        # Filter by Email 
        if option == "2":
            while True:
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                new_email = input("Enter the new email please: ")    
                if not re.match(pattern, new_email):
                   print(f"Invalid email. Please enter a valid email address.")
                   continue
                else:
                    print(f"Email: {new_email}")   
                    break
            if new_email:
                cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status 
                               FROM Tickets WHERE email = ?""", (new_email,))
                rows = cursor.fetchall()

                if not rows:
                    print(f"No tickets found for email {new_email}")
                else:
                    print(f"\n Tickets found for {new_email}: ")
                    for row in rows: 
                        print(f"ID: {row[0]} | Client: {row[1]} | Email: {row[2]} | Desc: {row[3][:20]}... | Priority: {row[4]} | Status: {row[5]}")


        # Filter by Status
        elif option == "3":
            status = input("Enter status to filter (Open/In Progress/Closed): ").title()
            if status not in ["Open", "In Progress", "Closed"]:
                print("❌ Invalid status.")
                continue
            cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status 
                              FROM Tickets WHERE status = ? ORDER BY creation_date""", (status,))
            rows = cursor.fetchall()
            if not rows:
                print(f"⚠️ No tickets found with status {status}.")
            else:
                for row in rows:
                    print(f"ID: {row[0]} | Client: {row[1]} | Email: {row[2]} | Desc: {row[3][:20]}... | Priority: {row[4]} | Status: {row[5]}")

        # Filter by Priority
        elif option == "4":
            priority = input("Enter priority to filter (High/Medium/Low): ").capitalize()
            if priority not in ["High", "Medium", "Low"]:
                print("❌ Invalid priority.")
                continue
            cursor.execute("""SELECT id_ticket, id_client, email, description, priority, status 
                              FROM Tickets WHERE priority = ? ORDER BY creation_date""", (priority,))
            rows = cursor.fetchall()
            if not rows:
                print(f"⚠️ No tickets found with priority {priority}.")
            else:
                for row in rows:
                    print(f"ID: {row[0]} | Client: {row[1]} | Email: {row[2]} | Desc: {row[3][:20]}... | Priority: {row[4]} | Status: {row[5]}")

        # Return to Main Menu
        elif option == "5":
            break
        else:
            print("❌ Invalid option. Try again.")
            
def tickets_summary():
    print("\n--- Tickets Summary ---")
    # Read the ticket on DataFrame
    df = pd.read_sql_query("SELECT * FROM Tickets", connection)

    if df.empty:
        print("⚠️ No tickets in the database.")
        return

    total_tickets = len(df)
    print(f"Total tickets: {total_tickets}\n")

    # Count by priority 
    print("Tickets by Priority:")
    priority_counts = df['priority'].value_counts()
    for priority, count in priority_counts.items():
        print(f"  {priority}: {count}")
    
    # Count by status
    print("\nTickets by Status:")
    status_counts = df['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    # % Closed tickets
    closed_count = status_counts.get("Closed", 0)
    resolved_percent = (closed_count / total_tickets) * 100
    print(f"✅ Resolved Tickets: {closed_count} of {total_tickets} ({resolved_percent:.1f}%)")

def export_tickets():
    print("\n--- Export Tickets ---")
    try:
        # Read all the tickets in a Dataframe
        df = pd.read_sql_query("SELECT * FROM Tickets", connection)

        if df.empty:
            print("⚠️ No tickets to export.")
            return

        # ASk exportation format
        while True:
            format_choice = input("Choose format (CSV / Excel): ").lower()
            if format_choice in ["csv", "excel"]:
                break
            else:
                print("❌ Invalid option. Please type 'CSV' or 'Excel'.")

        # Export on the format selected 
        if format_choice == "csv":
            df.to_csv("tickets_export.csv", index=False)
            print("✅ Tickets successfully exported to 'tickets_export.csv'")
        else:
            df.to_excel("tickets_export.xlsx", index=False)
            print("✅ Tickets successfully exported to 'tickets_export.xlsx'")

    except Exception as e:
        print(f"❌ Error exporting tickets: {e}")
#Back up of the database 
def backup_database():
    print("\n--- Backup Database ---")
    try:
        source_file = "ticket_data_base.db"

        # Create a file name with the current date and time 
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"ticket_data_base_backup_{timestamp}.db"

        # Copy file
        shutil.copy(source_file, backup_file)
        print(f"✅ Backup created successfully: {backup_file}")

    except FileNotFoundError:
        print("❌ Database file not found. No backup created.")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

while True:
    print("\n--- TICKET SYSTEM MENU ---")
    print("1. Create Ticket")
    print("2. View Tickets")
    print("3. Update Ticket")
    print("4. Delete Ticket")
    print("5. Search / Filter Tickets")
    print("6. Export Tickets to (CSV/Excel)")  
    print("7. Tickets Summary")
    print("8. Backup Database")
    print("9. Exit")

    choice = input("Choose an option (1 to 9): ")

    if choice == "1":
        create_tickets_loop()
    elif choice == "2":
        read_tickets()
    elif choice == "3":
        update_ticket()
    elif choice == "4":
        delete_ticket()
    elif choice == "5":
       
       filter_tickets()
    elif choice == "6":
        export_tickets() 
    elif choice == "7":
        tickets_summary()
    elif choice == "8":
        backup_database()
    elif choice == "9":
        print("👋 Exiting system... Goodbye!")
        break
    else:
        print("❌ Invalid option. Try again.")
    
connection.close()
print("👋 Database connection closed. Goodbye!")




           


               



