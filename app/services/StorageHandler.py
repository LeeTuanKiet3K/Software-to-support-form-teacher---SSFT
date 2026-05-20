import os
import uuid
from typing import Optional, BinaryIO

import cloudinary
import cloudinary.uploader
import cloudinary.api

from app.core.Config import AppConfig


class StorageHandler:
    """
    Lớp quản lý thao tác tải lên (Upload)
    và xóa (Delete) file bằng Cloudinary.
    """

    def __init__(self) -> None:
        """
        Khởi tạo cấu hình Cloudinary.
        """

        try:
            cloudinary.config(
                cloud_name=AppConfig.CLOUDINARY_CLOUD_NAME,
                api_key=AppConfig.CLOUDINARY_API_KEY,
                api_secret=AppConfig.CLOUDINARY_API_SECRET,
                secure=True
            )

        except Exception as e:
            print(f"Failed to initialize Cloudinary: {e}")

    def uploadFile(
        self,
        fileData: BinaryIO,
        fileName: str,
        destinationFolder: str = "uploads"
    ) -> Optional[str]:
        """
        Tải file lên Cloudinary và trả về URL công khai.
        """

        try:
            _, fileExtension = os.path.splitext(fileName)

            uniqueFileName = (
                f"{uuid.uuid4()}_"
                f"{os.path.splitext(fileName)[0]}"
            )

            uploadResult = cloudinary.uploader.upload(
                file=fileData,
                folder=destinationFolder,
                public_id=uniqueFileName,
                resource_type="auto"
            )

            return uploadResult.get("secure_url")

        except Exception as e:
            print(f"Failed to upload file to Cloudinary: {e}")
            return None

    def deleteFile(self, fileUrl: str) -> bool:
        """
        Xóa file khỏi Cloudinary dựa trên URL.
        """

        try:

            splitUrl = fileUrl.split("/upload/")

            if len(splitUrl) < 2:
                print("Invalid Cloudinary URL.")
                return False

            filePath = splitUrl[1]
            pathParts = filePath.split("/")

            if pathParts[0].startswith("v"):
                pathParts.pop(0)

            publicId = "/".join(pathParts)

            publicId = os.path.splitext(publicId)[0]

            result = cloudinary.uploader.destroy(publicId)

            return result.get("result") == "ok"

        except Exception as e:
            print(f"Failed to delete file from Cloudinary: {e}")
            return False