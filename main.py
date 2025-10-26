"""
Roster Tagging - Main Application Entry Point
Desktop application for organizing synthetic female model images
"""

import streamlit as st
import os
from pathlib import Path
from PIL import Image
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

# Session state initialization
if 'selected_profile' not in st.session_state:
    st.session_state.selected_profile = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# Constants
IMAGES_PER_PAGE = 50

def display_image_thumbnail(image_path, max_size=(200, 200)):
    """Display image thumbnail with error handling"""
    try:
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image.thumbnail(max_size)
            return image
        else:
            return None
    except Exception as e:
        st.error(f"Error loading image {os.path.basename(image_path)}: {e}")
        return None

def display_image_grid(images, page=0, images_per_page=IMAGES_PER_PAGE):
    """Display images in a grid with pagination"""
    start_idx = page * images_per_page
    end_idx = start_idx + images_per_page
    page_images = images[start_idx:end_idx]
    
    if not page_images:
        st.info("No images to display")
        return
    
    # Display pagination info
    total_pages = (len(images) - 1) // images_per_page + 1
    if total_pages > 1:
        st.write(f"Page {page + 1} of {total_pages} ({len(images)} total images)")
    
    # Create grid layout
    cols_per_row = 4
    for i in range(0, len(page_images), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(page_images):
                image_data = page_images[i + j]
                with col:
                    # Load and display thumbnail
                    thumbnail = display_image_thumbnail(image_data['filepath'])
                    if thumbnail:
                        st.image(thumbnail, caption=image_data['filename'], use_container_width=True)
                        
                        # Click to view larger image
                        if st.button(f"View", key=f"view_{image_data['id']}"):
                            st.session_state.modal_image = image_data
                    else:
                        st.error(f"📁 {image_data['filename']}")
                        st.caption("File not found")
    
    # Pagination controls
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if page > 0:
                if st.button("← Previous"):
                    st.session_state.current_page = page - 1
                    st.rerun()
        
        with col2:
            st.write(f"Page {page + 1} of {total_pages}")
        
        with col3:
            if page < total_pages - 1:
                if st.button("Next →"):
                    st.session_state.current_page = page + 1
                    st.rerun()

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
                    
                    processed_count = 0
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
                            processed_count += 1
                    
                    st.success(f"Processed {processed_count} files from {len(files)} total files")
                    st.rerun()
            else:
                st.error("Folder path does not exist")
        
        st.divider()
        
        # Display profiles with counts
        profiles = db_manager.get_profiles_with_counts()
        if profiles:
            st.subheader("📋 Profile List")
            
            # Show All Profiles option
            if st.button("🔍 Show All Profiles", use_container_width=True, 
                        type="primary" if st.session_state.selected_profile is None else "secondary"):
                st.session_state.selected_profile = None
                st.session_state.current_page = 0
                st.rerun()
            
            st.write("---")
            
            # Individual profiles
            for profile in profiles:
                username = profile['username']
                image_count = profile['image_count']
                
                # Highlight selected profile
                button_type = "primary" if st.session_state.selected_profile == username else "secondary"
                
                if st.button(f"👤 {username} ({image_count})", 
                           key=f"profile_{username}",
                           use_container_width=True,
                           type=button_type):
                    st.session_state.selected_profile = username
                    st.session_state.current_page = 0
                    st.rerun()
        else:
            st.info("No profiles found yet")
        
        st.divider()
        
        # Statistics
        total_images = db_manager.get_image_count()
        total_profiles = db_manager.get_profile_count()
        
        st.subheader("� Statistics")
        st.metric("Total Profiles", total_profiles)
        st.metric("Total Images", total_images)
    
    # Main content area
    if st.session_state.selected_profile:
        # Show specific profile
        username = st.session_state.selected_profile
        st.header(f"🖼️ Profile: {username}")
        
        # Get images for this profile
        images = db_manager.get_images_by_username(username)
        
        if images:
            st.write(f"Found {len(images)} images for **{username}**")
            display_image_grid(images, st.session_state.current_page)
        else:
            st.info(f"No images found for profile: {username}")
    
    else:
        # Show all profiles overview
        st.header("🖼️ All Profiles Overview")
        
        total_images = db_manager.get_image_count()
        total_profiles = db_manager.get_profile_count()
        
        if total_profiles > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Images", total_images)
            with col2:
                st.metric("Total Profiles", total_profiles)
            
            st.subheader("📋 Profile Summary")
            profiles = db_manager.get_profiles_with_counts()
            
            # Display profiles in a nice table format
            if profiles:
                profile_data = []
                for profile in profiles:
                    profile_data.append({
                        "Profile": profile['username'],
                        "Images": profile['image_count']
                    })
                
                st.dataframe(profile_data, use_container_width=True)
                
                st.info("💡 Click on a profile in the sidebar to view its images")
            
        else:
            st.info("Select a folder in the sidebar to start importing images")
    
    # Modal for large image view
    if 'modal_image' in st.session_state:
        image_data = st.session_state.modal_image
        
        @st.dialog(f"🖼️ {image_data['filename']}")
        def show_image_modal():
            try:
                if os.path.exists(image_data['filepath']):
                    image = Image.open(image_data['filepath'])
                    st.image(image, caption=f"Profile: {image_data['username']}", use_container_width=True)
                    
                    # Image details
                    st.write("**File Details:**")
                    st.write(f"• **Filename:** {image_data['filename']}")
                    st.write(f"• **Profile:** {image_data['username']}")
                    st.write(f"• **Added:** {image_data['date_added']}")
                    st.write(f"• **Path:** {image_data['filepath']}")
                else:
                    st.error("Image file not found")
            except Exception as e:
                st.error(f"Error loading image: {e}")
            
            if st.button("Close"):
                del st.session_state.modal_image
                st.rerun()
        
        show_image_modal()

if __name__ == "__main__":
    main()