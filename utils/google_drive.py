"""
Google Drive backup helper
"""
import os
import json
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveBackup:
    def __init__(self):
        """Initialize Google Drive service"""
        self.service = None
        self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        
        # Load credentials from environment
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json or not self.folder_id:
            self.service = None
            return
        
        try:
            creds_dict = json.loads(creds_json)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"❌ Google Drive auth failed: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """Check if Google Drive backup is configured"""
        return self.service is not None
    
    def upload_csv(self, filename: str, csv_content: bytes) -> bool:
        """Upload CSV file to Google Drive"""
        if not self.is_available():
            return False
        
        try:
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id],
                'mimeType': 'text/csv'
            }
            
            file_io = io.BytesIO(csv_content)
            media = MediaIoBaseUpload(file_io, mimetype='text/csv')
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            print(f"✅ Uploaded to Drive: {file['webViewLink']}")
            return True
        except Exception as e:
            print(f"❌ Drive upload failed: {e}")
            return False

# Global instance
drive_backup = GoogleDriveBackup()
