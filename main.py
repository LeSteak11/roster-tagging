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
from utils.ai_tagger import AITagger

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
if 'ai_tagger' not in st.session_state:
    st.session_state.ai_tagger = AITagger()
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = None

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
    
    # Show success messages
    if st.session_state.show_success_message:
        st.success(st.session_state.show_success_message)
        st.session_state.show_success_message = None
    
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
        
        # Batch Tagging Section
        st.subheader("🤖 AI Batch Tagging")
        
        untagged_count = len(db_manager.get_untagged_images())
        tagged_count = db_manager.get_tagged_image_count()
        
        if untagged_count > 0:
            st.write(f"📊 **{untagged_count}** untagged images")
            st.write(f"✅ **{tagged_count}** already tagged")
            
            if st.button("🚀 Auto-tag All Untagged", use_container_width=True, type="primary"):
                if st.session_state.get('confirm_batch_tag', False):
                    # Process batch tagging
                    untagged_images = db_manager.get_untagged_images()
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, image in enumerate(untagged_images):
                        status_text.text(f"Tagging {i+1}/{len(untagged_images)}: {image['filename']}")
                        progress_bar.progress((i + 1) / len(untagged_images))
                        
                        # Tag the image
                        success, ai_tags = st.session_state.ai_tagger.tag_image(image['filepath'])
                        if success and ai_tags:
                            db_manager.add_tags(
                                image_id=image['id'],
                                hair_color=ai_tags.get('hair_color'),
                                skin_tone=ai_tags.get('skin_tone'),
                                clothing_type=ai_tags.get('clothing_type'),
                                pose_type=ai_tags.get('pose_type'),
                                environment=ai_tags.get('environment'),
                                face_visible=ai_tags.get('face_visible')
                            )
                    
                    st.session_state.show_success_message = f"Batch tagging completed! Tagged {len(untagged_images)} images."
                    st.session_state.confirm_batch_tag = False
                    st.rerun()
                else:
                    st.session_state.confirm_batch_tag = True
                    st.rerun()
            
            if st.session_state.get('confirm_batch_tag', False):
                st.warning(f"⚠️ This will tag {untagged_count} images using AI. This may take several minutes and use API credits.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirm", use_container_width=True):
                        # Will be handled above
                        pass
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.confirm_batch_tag = False
                        st.rerun()
        else:
            st.success("🎉 All images are tagged!")
        
        st.divider()
        
        # Statistics
        total_images = db_manager.get_image_count()
        total_profiles = db_manager.get_profile_count()
        
        st.subheader("📊 Statistics")
        st.metric("Total Profiles", total_profiles)
        st.metric("Total Images", total_images) 
        st.metric("Tagged Images", tagged_count)
        if total_images > 0:
            tag_percentage = (tagged_count / total_images) * 100
            st.metric("Tag Progress", f"{tag_percentage:.1f}%")
    
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
    
    # Modal for large image view and tagging
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
                    
                    st.divider()
                    
                    # AI Tagging Section
                    st.subheader("🤖 AI Tags")
                    
                    # Get existing tags
                    existing_tags = db_manager.get_tags_by_image_id(image_data['id'])
                    
                    # Create form for tag editing
                    with st.form(f"tag_form_{image_data['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            hair_color = st.selectbox(
                                "Hair Color",
                                options=st.session_state.ai_tagger.get_tag_options('hair_color'),
                                index=0 if not existing_tags else st.session_state.ai_tagger.get_tag_options('hair_color').index(existing_tags.get('hair_color', 'unknown'))
                            )
                            
                            clothing_type = st.selectbox(
                                "Clothing Type", 
                                options=st.session_state.ai_tagger.get_tag_options('clothing_type'),
                                index=0 if not existing_tags else st.session_state.ai_tagger.get_tag_options('clothing_type').index(existing_tags.get('clothing_type', 'unknown'))
                            )
                            
                            environment = st.selectbox(
                                "Environment",
                                options=st.session_state.ai_tagger.get_tag_options('environment'),
                                index=0 if not existing_tags else st.session_state.ai_tagger.get_tag_options('environment').index(existing_tags.get('environment', 'unknown'))
                            )
                        
                        with col2:
                            skin_tone = st.selectbox(
                                "Skin Tone",
                                options=st.session_state.ai_tagger.get_tag_options('skin_tone'),
                                index=0 if not existing_tags else st.session_state.ai_tagger.get_tag_options('skin_tone').index(existing_tags.get('skin_tone', 'unknown'))
                            )
                            
                            pose_type = st.selectbox(
                                "Pose Type",
                                options=st.session_state.ai_tagger.get_tag_options('pose_type'), 
                                index=0 if not existing_tags else st.session_state.ai_tagger.get_tag_options('pose_type').index(existing_tags.get('pose_type', 'unknown'))
                            )
                            
                            face_visible = st.checkbox(
                                "Face Visible",
                                value=existing_tags.get('face_visible', False) if existing_tags else False
                            )
                        
                        # Action buttons
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Tags", type="primary"):
                                success = db_manager.add_tags(
                                    image_id=image_data['id'],
                                    hair_color=hair_color,
                                    skin_tone=skin_tone,
                                    clothing_type=clothing_type,
                                    pose_type=pose_type,
                                    environment=environment,
                                    face_visible=face_visible
                                )
                                if success:
                                    st.session_state.show_success_message = "Tags saved successfully!"
                                    st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🤖 AI Tag"):
                                with st.spinner("AI analyzing image..."):
                                    success, ai_tags = st.session_state.ai_tagger.tag_image(image_data['filepath'])
                                    if success and ai_tags:
                                        db_manager.add_tags(
                                            image_id=image_data['id'],
                                            hair_color=ai_tags.get('hair_color'),
                                            skin_tone=ai_tags.get('skin_tone'),
                                            clothing_type=ai_tags.get('clothing_type'),
                                            pose_type=ai_tags.get('pose_type'),
                                            environment=ai_tags.get('environment'),
                                            face_visible=ai_tags.get('face_visible')
                                        )
                                        st.session_state.show_success_message = "AI tagging completed!"
                                        st.rerun()
                                    else:
                                        st.error("AI tagging failed. Please try again.")
                    
                    # Show existing tags if available
                    if existing_tags:
                        st.success("✅ This image has been tagged")
                        with st.expander("View Current Tags"):
                            for key, value in existing_tags.items():
                                if key not in ['id', 'image_id', 'date_tagged']:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    else:
                        st.info("ℹ️ No tags yet. Use AI Tag button or manually select tags above.")
                    
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