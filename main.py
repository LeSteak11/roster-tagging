"""
Roster Tagging - Main Application Entry Point
Desktop application for organizing synthetic female model images
"""

import streamlit as st
import os
from pathlib import Path
from database.db_manager import DatabaseManager
from utils.file_scanner import FileScanner
from utils.username_extractor import UsernameExtractor

# Page configuration
st.set_page_config(
    page_title="Roster Tagging",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📸 Roster Tagging")
    st.caption("AI Model Image Organization System")
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Sidebar for Profiles
    with st.sidebar:
        st.header("👥 Profiles")
        
        # Folder selection
        st.subheader("📁 Select Image Folder")
        folder_path = st.text_input("Enter folder path:", placeholder="C:/path/to/images")
        
        if st.button("Scan Folder") and folder_path:
            if os.path.exists(folder_path):
                with st.spinner("Scanning files..."):
                    scanner = FileScanner()
                    extractor = UsernameExtractor()
                    
                    # Scan for supported files
                    files = scanner.scan_folder(folder_path)
                    
                    # Process each file
                    for file_path in files:
                        username = extractor.extract_username(file_path)
                        if username:
                            db_manager.add_profile(username)
                            db_manager.add_image(
                                filename=Path(file_path).name,
                                filepath=str(file_path),
                                username=username
                            )
                    
                    st.success(f"Processed {len(files)} files")
                    st.rerun()
            else:
                st.error("Folder path does not exist")
        
        # Display profiles
        profiles = db_manager.get_all_profiles()
        if profiles:
            st.subheader("📋 Discovered Profiles")
            for profile in profiles:
                st.text(f"• {profile['username']}")
        else:
            st.info("No profiles found yet")
    
    # Main content area
    st.header("🖼️ Image Viewer Coming Soon")
    st.info("Select a folder in the sidebar to start importing images")
    
    # Display some stats if we have data
    total_images = db_manager.get_image_count()
    total_profiles = db_manager.get_profile_count()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Images", total_images)
    with col2:
        st.metric("Total Profiles", total_profiles)

if __name__ == "__main__":
    main()