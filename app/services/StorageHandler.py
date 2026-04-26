import os
import uuid
from typing import Optional, BinaryIO
from firebase_admin import storage
from app.core.Config import AppConfig

class StorageHandler:
    """
    Lớp quản lý thao tác tải lên (Upload) và xóa (Delete) tệp tin trên Firebase Cloud Storage.
    """

    def __init__(self, bucketName: Optional[str] = None) -> None:
        try:
            if bucketName:
                self.m_bucket = storage.bucket(bucketName)
            else:
                self.m_bucket = storage.bucket()
        except Exception as e:
            print(f"Failed to initialize Storage: {e}")

    def uploadFile(self, fileData: BinaryIO, fileName: str, destinationFolder: str = "uploads") -> Optional[str]:
        """
        Tải file lên Cloud Storage và trả về URL công khai.
        """
        _, fileExtension = os.path.splitext(fileName)

        uniqueFileName = f"{uuid.uuid4()}{fileExtension}"
        fullPath = f"{destinationFolder}/{uniqueFileName}"
        
        try:
            blob = self.m_bucket.blob(fullPath)
            blob.upload_from_file(fileData)
            blob.make_public()
            return blob.public_url
            
        except Exception as e:
            print(f"Failed to upload file to Storage: {e}")
            return None
        
    def deleteFile(self, fileUrl: str) -> bool:
        """
        Xóa file khỏi Cloud Storage dựa trên public URL.
        """
        try:
            urlPrefix = f"https://storage.googleapis.com/{self.m_bucket.name}/"
            if not fileUrl.startswith(urlPrefix):
                print("Failed to delete file: URL does not belong to this bucket.")
                return False
                
            blobPath = fileUrl.replace(urlPrefix, "")
            blob = self.m_bucket.blob(blobPath)
            blob.delete()
            return True
            
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return False