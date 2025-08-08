from .supabase_client import supabase
from datetime import datetime
import uuid
import base64

class StorageManager:
    """Handles file uploads to Supabase Storage"""

    @staticmethod
    def upload_profile_image(base64_image: str, username:str) -> str:
        """
        Upload profile image to Supabase Storage
        Returns the public URL of the uploaded image
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image.split(',')[1])

            # Generate unique filename
            file_ext = "jpg"
            timestamp = datetime.now().strftime('%Y%m/%d_/%H%M:%S')
            filename = f"profile_{username}_{timestamp}.{file_ext}"

            # Upload to Supabase storage
            result = supabase.storage \
                .from_('profiles') \
                .upload(filename, image_data)
            
            # Get public URL
            public_url = supabase.storage \
                .from_('profiles') \
                .get_public_url(filename)
            
            return public_url
        
        except Exception as e:
            raise Exception(f"Failed to upload profile image: {str(e)}")
        
    @staticmethod
    def upload_post_image(base64_image:str, user_id: str) -> str:
        """
        Upload post image to Supabase Storage
        Returns the public URL of the uploaded image
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image.split(',')[1])

            # Generate unique filename
            file_ext = "jpg"
            timestamp = datetime.now().strftime('%Y%m/%d_/%H%M:%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"post_{user_id}_{timestamp}_{unique_id}.{file_ext}"

             # Upload to Supabase storage
            result = supabase.storage \
                .from_('posts') \
                .upload(filename, image_data)
            
            # Get public URL
            public_url = supabase.storage \
                .from_('posts') \
                .get_public_url(filename)
            
            return public_url
        
        except Exception as e:
            raise Exception(f"Failed to upload profile image: {str(e)}")

@staticmethod
def delete_image(bucket: str, path: str) -> bool:
    """Delete image from storage"""
    try:
        supabase.storage \
            .from_(bucket) \
            .remove([path])
        return True
    except Exception as e:
        raise Exception(f"Failed to delete image: {str(e)}")
