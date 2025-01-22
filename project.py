import streamlit as st
import os
import shutil
from datetime import datetime

# Base directory for storage
BASE_DIR = "my_drive"
os.makedirs(BASE_DIR, exist_ok=True)

# Initialize session state
if 'require_rerun' not in st.session_state:
    st.session_state.require_rerun = False
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False

# Function to save uploaded file
def save_file(file, folder_path):
    """Save the uploaded file to the specified folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.name}"
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return filename

# Function to list all files in a folder
def list_files(folder_path):
    """List all files in the folder."""
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Function to list all folders in the base directory
def list_folders(base_path):
    """List all folders in the base directory."""
    return [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

# Function to create a new folder
def create_folder(folder_name, parent_folder):
    """Create a new folder."""
    folder_path = os.path.join(parent_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

# Function to get storage details
def get_storage_details():
    """Get the total and used storage details."""
    total, used, free = shutil.disk_usage(BASE_DIR)
    return total, used, free

# Function to get used storage within 'my_drive' folder
def get_used_storage_in_drive(base_path):
    """Calculate the total used storage for files in the 'my_drive' folder."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(base_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

# Function to convert bytes to human-readable format
def convert_size(size_in_bytes):
    """Convert bytes to a more readable format (KB, MB, GB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"

# Function to delete a file
def delete_file(file_path):
    """Delete the file."""
    try:
        os.remove(file_path)
        return True, None
    except Exception as e:
        return False, str(e)

# Function to handle file upload
def handle_upload():
    st.session_state.file_processed = False

# Streamlit UI
st.set_page_config(page_title="Td Drive ", layout="wide")
st.title("Td drive")

# Sidebar - File Manager
st.sidebar.header("File Manager")

# Display storage information
total, _, free = get_storage_details()
used_in_drive = get_used_storage_in_drive(BASE_DIR)
st.sidebar.markdown(f"**Storage Used in 'my_drive':** {convert_size(used_in_drive)} / {convert_size(free)}")
st.sidebar.markdown(f"**Storage Available:** {convert_size(free-used_in_drive)}")

# Sidebar: Folder navigation and Create Folder
folder_name = st.sidebar.text_input("Create New Folder")
if st.sidebar.button("Create Folder"):
    create_folder(folder_name, BASE_DIR)
    st.sidebar.success(f"Folder '{folder_name}' created!")

# Sidebar: Select Folder
folders = list_folders(BASE_DIR)
selected_folder = st.sidebar.selectbox("Select Folder", [""] + folders)
if selected_folder:
    current_folder = os.path.join(BASE_DIR, selected_folder)
else:
    current_folder = BASE_DIR

# Upload File
st.header("Upload Files")
uploaded_file = st.file_uploader("Choose a file", on_change=handle_upload)

if uploaded_file and not st.session_state.file_processed:
    saved_file_name = save_file(uploaded_file, current_folder)
    st.success(f"Uploaded file saved as '{saved_file_name}'")
    st.session_state.file_processed = True
    st.rerun()

# File List (Grid view)
st.header(f"Files in '{selected_folder or 'Root'}'")
files = list_files(current_folder)
if files:
    for file in files:
        file_path = os.path.join(current_folder, file)
        file_size = convert_size(os.path.getsize(file_path))
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        
        # File Display with details
        with st.expander(f"File: {file}", expanded=True):
            st.write(f"**Size:** {file_size}")
            st.write(f"**Last Modified:** {modified_time}")
            with open(file_path, "rb") as f:
                st.download_button(label=f"Download {file}", data=f.read(), file_name=file)
            
            # Delete File Button
            if st.button(f"Delete {file}", key=f"delete_{file}"):
                success, error_message = delete_file(file_path)
                if success:
                    st.success(f"File '{file}' deleted successfully.")
                    st.session_state.file_processed = False
                    st.rerun()
                else:
                    st.error(f"Failed to delete '{file}': {error_message}")
else:
    st.write("No files in this folder.")

# File Preview
st.header("Preview Files")
preview_file = st.selectbox("Select a file to preview", [""] + files)
if preview_file:
    file_path = os.path.join(current_folder, preview_file)
    
    if preview_file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        st.image(file_path, caption=preview_file)
    elif preview_file.lower().endswith((".txt", ".csv", ".log")):
        with open(file_path, "r") as f:
            st.text(f.read())
    elif preview_file.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            st.download_button(label="Preview PDF", data=f.read(), file_name=preview_file)
    else:
        st.write("File format not supported for preview.")

st.info("project made by TANMAY DAVE for Cloud Computing ")