import sqlite3
import pandas as pd
import streamlit as st
import os

# Streamlit Settings 
st.set_page_config(page_title="Ticket Manager", layout="wide")
st.title("🗓️ Ticket Management System")

# Sure route for DataBase 
def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), "ticket_data_base.db")
    return sqlite3.connect(db_path)

# Create table if not exist
def ensure_table_exists():
    conn = connect_db()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

# Load tickets as DataFrame 
def load_tickets():
    conn = connect_db()
    try:
        df = pd.read_sql_query("SELECT * FROM Tickets ORDER BY creation_date DESC", conn)
    except Exception as e:
        st.error(f"❌ Error loading tickets: {e}")
        df = pd.DataFrame()
    conn.close()
    return df

# Create new ticket 
def create_ticket():
    with st.form("Create Ticket"):
        st.subheader("🖊️ Create New Ticket")
        id_client = st.number_input("Client ID", min_value=1)
        email = st.text_input("Email")
        description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submitted = st.form_submit_button("Create Ticket")

        if submitted:
            if not email or not description:
                st.warning("Email and description are required.")
            else:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Tickets (id_client, email, description, priority)
                    VALUES (?, ?, ?, ?)
                """, (id_client, email, description, priority))
                conn.commit()
                st.success(f"✅ Ticket created successfully with ID {cursor.lastrowid}!")
                conn.close()

# Ticket filters 
def filter_tickets(df):
    st.sidebar.subheader("🔍 Filter Tickets")
    priority_filter = st.sidebar.multiselect("Filter by Priority", df["priority"].unique())
    status_filter = st.sidebar.multiselect("Filter by Status", df["status"].unique())

    if priority_filter:
        df = df[df["priority"].isin(priority_filter)]
    if status_filter:
        df = df[df["status"].isin(status_filter)]

    return df

# Display tickets
def display_tickets():
    df = load_tickets()
    if df.empty:
        st.info("No tickets found in the database.")
    else:
        filtered_df = filter_tickets(df)
        st.subheader(":file_folder: Tickets on Record")
        st.dataframe(filtered_df, use_container_width=True)

# Delete ticket by ID
def delete_ticket_by_id(ticket_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tickets WHERE id_ticket = ?", (ticket_id,))
    conn.commit()
    conn.close()

# Delete ticket UI
def delete_ticket_ui():
    st.subheader("🔍 Delete Ticket")
    df = load_tickets()
    if not df.empty:
        ticket_ids = df["id_ticket"].tolist()
        selected_id = st.selectbox("Select a ticket to delete", ticket_ids)
        if st.button("🔎 Confirm Delete"):
            delete_ticket_by_id(selected_id)
            st.success(f"✅ Ticket ID {selected_id} deleted successfully!")

# Update ticket status
def update_ticket_ui():
    st.subheader("✏️ Update Ticket")
    df = load_tickets()
    if not df.empty:
        ticket_ids = df["id_ticket"].tolist()
        selected_id = st.selectbox("Select a ticket to update", ticket_ids, key="update")
        new_status = st.selectbox("New Status", ["Open", "Closed"])
        new_priority = st.selectbox("New Priority", ["High", "Medium", "Low"])
        if st.button("✅ Apply Update"):
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE Tickets SET status = ?, priority = ? WHERE id_ticket = ?",
                           (new_status, new_priority, selected_id))
            conn.commit()
            conn.close()
            st.success(f"✅ Ticket ID {selected_id} updated successfully!")

# Export tickets

def export_tickets_ui():
    df = load_tickets()
    if df.empty:
        st.info("No data to export.")
        return

    st.subheader("📂 Export Tickets")
    export_format = st.selectbox("Choose format", ["CSV", "Excel"])
    filename = st.text_input("Filename (without extension)", value="tickets_export")

    if st.button("🖫 Export Now"):
        if export_format == "CSV":
            df.to_csv(f"{filename}.csv", index=False)
            st.success(f"Exported to {filename}.csv")
        else:
            df.to_excel(f"{filename}.xlsx", index=False)
            st.success(f"Exported to {filename}.xlsx")

# Ejecutar app
ensure_table_exists()
create_ticket()
display_tickets()
delete_ticket_ui()
update_ticket_ui()
export_tickets_ui()
