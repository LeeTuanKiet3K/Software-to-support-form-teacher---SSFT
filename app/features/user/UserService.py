from typing import BinaryIO, Optional

from app.services.FirestoreHandler import FirestoreHandler
from app.services.StorageHandler import StorageHandler


class UserService:
    """
        - Gọi StorageHandler  ->  xử lý file trên Cloudinary.
        - Gọi FirestoreHandler ->  đồng bộ data vào Firestore.
    """

    USERS_COLLECTION = "Users"

    def __init__(self) -> None:
        # Infrastructure layer — tầng hạ tầng lưu trữ file
        self.m_storageHandler = StorageHandler()

        # Infrastructure layer — tầng hạ tầng cơ sở dữ liệu
        self.m_dbHandler = FirestoreHandler()

    def uploadAvatar(
        self,
        userId: str,
        fileData: BinaryIO,
        fileName: str
    ) -> Optional[str]:
        """
        Tải ảnh đại diện mới lên Cloudinary và đồng bộ URL vào Firestore.
            1. Lấy hồ sơ người dùng từ Firestore để kiểm tra ảnh cũ.
            2. Nếu đang có ảnh cũ -> xóa khỏi Cloudinary trước.
            3. Upload ảnh mới lên Cloudinary.
            4. Nếu upload thành công -> cập nhật `avatar_url` vào Firestore.
            5. Trả về URL mới, hoặc None nếu có lỗi.
        """
        try:
            # Bước 1: Lấy ảnh cũ từ Firestore
            existingAvatarUrl = self._getExistingAvatarUrl(userId)

            # Bước 2: Nếu đã có ảnh cũ -> xóa trên Cloudinary trước khi ghi đè
            if existingAvatarUrl:
                wasDeleted = self.m_storageHandler.deleteFile(existingAvatarUrl)
                if not wasDeleted:
                    print(
                        f"[UserService] Không thể xóa ảnh cũ "
                        f"(userId={userId}, url={existingAvatarUrl}). "
                        f"Tiếp tục upload ảnh mới."
                    )

            # Bước 3: Upload ảnh mới lên Cloudinary
            newAvatarUrl = self.m_storageHandler.uploadFile(
                fileData=fileData,
                fileName=fileName,
                destinationFolder="avatars"
            )

            if not newAvatarUrl:
                print(
                    f"[UserService] Upload ảnh mới thất bại "
                    f"(userId={userId})."
                )
                return None

            # Bước 4: Đồng bộ URL mới vào Firestore
            isSynced = self.m_dbHandler.updateDocument(
                collectionName=self.USERS_COLLECTION,
                documentId=userId,
                data={"avatar_url": newAvatarUrl}
            )

            if not isSynced:
                # Ảnh đã lên Cloudinary nhưng Firestore chưa cập nhật — ghi log để truy vết
                print(
                    f"[UserService] Ảnh đã upload nhưng Firestore "
                    f"cập nhật thất bại (userId={userId}, url={newAvatarUrl}). "
                    f"Cần kiểm tra lại thủ công."
                )

            return newAvatarUrl

        except Exception as e:
            print(f"[UserService] Lỗi không xác định trong uploadAvatar: {e}")
            return None

    def deleteAvatar(self, userId: str) -> bool:
        """
        Xóa ảnh đại diện khỏi Cloudinary và đồng bộ Firestore về None.
            1. Lấy `avatar_url` hiện tại từ Firestore.
            2. Nếu không có URL -> trả về False (không có gì để xóa).
            3. Gọi StorageHandler.deleteFile() để xóa file trên Cloudinary.
            4. Nếu xóa thành công -> cập nhật `avatar_url = None` trong Firestore.
            5. Trả về True nếu toàn bộ luồng thành công, False nếu có lỗi.
        """
        try:
            # Bước 1: Lấy URL ảnh hiện tại từ Firestore
            existingAvatarUrl = self._getExistingAvatarUrl(userId)
            if not existingAvatarUrl:
                print(
                    f"[UserService] Người dùng (userId={userId}) "
                    f"không có ảnh đại diện."
                )
                return False

            # Bước 3: Xóa file trên Cloudinary thông qua StorageHandler
            wasDeleted = self.m_storageHandler.deleteFile(existingAvatarUrl)

            if not wasDeleted:
                print(
                    f"[UserService] Xóa ảnh trên Cloudinary thất bại "
                    f"(userId={userId}, url={existingAvatarUrl})."
                )
                return False

            # Bước 4: Đồng bộ Firestore — set avatar_url về None
            isSynced = self.m_dbHandler.updateDocument(
                collectionName=self.USERS_COLLECTION,
                documentId=userId,
                data={"avatar_url": None}
            )

            if not isSynced:
                print(
                    f"[UserService] File đã xóa trên Cloudinary nhưng "
                    f"Firestore cập nhật thất bại (userId={userId}). "
                )
                return False

            print(
                f"[UserService] Đã xóa ảnh và đồng bộ Firestore "
                f"(userId={userId})."
            )
            return True

        except Exception as e:
            print(f"[UserService] Lỗi không xác định trong deleteAvatar: {e}")
            return False

    def _getExistingAvatarUrl(self, userId: str) -> Optional[str]:
        """
        Hàm nội bộ: Truy vấn Firestore để lấy URL ảnh đại diện hiện tại.

        Args:
            userId (str): UID người dùng.

        Returns:
            Optional[str]: URL ảnh hiện tại, hoặc None nếu chưa có / không tồn tại.
        """
        try:
            userProfile = self.m_dbHandler.getDocument(
                collectionName=self.USERS_COLLECTION,
                documentId=userId
            )

            if not userProfile:
                print(
                    f"[UserService] Không tìm thấy hồ sơ người dùng "
                    f"(userId={userId}) trong Firestore."
                )
                return None

            # Lấy URL — trả về None nếu field rỗng hoặc không tồn tại
            avatarUrl = userProfile.get("avatar_url") or None
            return avatarUrl

        except Exception as e:
            print(
                f"[UserService] Lỗi khi truy vấn avatar_url "
                f"(userId={userId}): {e}"
            )
            return None
