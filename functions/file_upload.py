import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL=os.getenv("WEBHOOK_URL")


def upload_csv_to_google_drive(file_path, filename="test", delete_after_upload=False):
    """Upload CSV file to Google Drive via n8n webhook
    
    Args:
        file_path: Path to the CSV file to upload
        filename: Name for the file in Google Drive
        delete_after_upload: If True, delete the local file after successful upload
    """
    
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        print(f"Current directory: {os.getcwd()}")
        return False
    
    print(f"Uploading {file_path} to Google Drive...")
    
    try:
        # Open and send the file
        with open(file_path, 'rb') as file:
            files = {
                'data': (filename, file, 'text/csv')
            }
            response = requests.post(WEBHOOK_URL, files=files)
        
        # Check response
        if response.status_code == 200:
            print("CSV uploaded successfully to Google Drive!")
            
            # Delete file after successful upload if requested
            if delete_after_upload:
                try:
                    os.remove(file_path)
                    print(f"Deleted local file: {file_path}")
                except Exception as e:
                    print(f"Warning: Could not delete local file: {e}")
            
            return True
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False

# Run the upload
if __name__ == "__main__":
    upload_csv_to_google_drive()