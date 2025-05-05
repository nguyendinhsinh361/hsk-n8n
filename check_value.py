import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage import io

def calculate_ssim(original_image, compressed_image):
    """
    Tính toán chỉ số SSIM giữa ảnh gốc và ảnh nén
    
    Parameters:
    - original_image: đường dẫn hoặc mảng numpy của ảnh gốc
    - compressed_image: đường dẫn hoặc mảng numpy của ảnh nén
    
    Returns:
    - Giá trị SSIM từ 0 đến 1
    """
    # Nếu là đường dẫn, đọc ảnh
    if isinstance(original_image, str):
        original_image = io.imread(original_image)
    if isinstance(compressed_image, str):
        compressed_image = io.imread(compressed_image)
    
    # Chuyển về ảnh xám nếu ảnh màu
    if len(original_image.shape) > 2:
        original_image = np.mean(original_image, axis=2)
    if len(compressed_image.shape) > 2:
        compressed_image = np.mean(compressed_image, axis=2)
    
    # Đảm bảo 2 ảnh cùng kích thước
    if original_image.shape != compressed_image.shape:
        raise ValueError("Hai ảnh phải có cùng kích thước")
    
    # Tính SSIM
    ssim_score = ssim(original_image, compressed_image, data_range=original_image.max() - original_image.min())
    
    return ssim_score

def calculate_mse(original_image, compressed_image):
    """
    Tính toán Mean Squared Error (MSE) giữa ảnh gốc và ảnh nén
    
    Parameters:
    - original_image: đường dẫn hoặc mảng numpy của ảnh gốc
    - compressed_image: đường dẫn hoặc mảng numpy của ảnh nén
    
    Returns:
    - Giá trị MSE
    """
    # Nếu là đường dẫn, đọc ảnh
    if isinstance(original_image, str):
        original_image = io.imread(original_image)
    if isinstance(compressed_image, str):
        compressed_image = io.imread(compressed_image)
    
    # Chuyển về ảnh xám nếu ảnh màu
    if len(original_image.shape) > 2:
        original_image = np.mean(original_image, axis=2)
    if len(compressed_image.shape) > 2:
        compressed_image = np.mean(compressed_image, axis=2)
    
    # Đảm bảo 2 ảnh cùng kích thước
    if original_image.shape != compressed_image.shape:
        raise ValueError("Hai ảnh phải có cùng kích thước")
    
    # Tính MSE
    mse = np.mean((original_image - compressed_image) ** 2)
    
    return mse

# Ví dụ sử dụng
def main():
    # Thay path_original và path_compressed bằng đường dẫn thực tế
    path_original = "img/E1_310001_1A.png"
    path_compressed = "img_out/E1_310001_1A.webp"
    
    try:
        # Tính SSIM
        ssim_score = calculate_ssim(path_original, path_compressed)
        print(f"SSIM Score: {ssim_score:.4f}")
        
        # Tính MSE
        mse_value = calculate_mse(path_original, path_compressed)
        print(f"MSE Value: {mse_value:.4f}")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
