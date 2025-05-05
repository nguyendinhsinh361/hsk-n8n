def find_index_by_name(mang, field_search):
    """
    Hàm tìm vị trí của phần tử theo giá trị trường 'ten'
    
    Args:
    - mang: Mảng chứa các object
    - ten_can_tim: Tên cần tìm
    
    Returns:
    - Vị trí của phần tử (index) nếu tìm thấy
    - None nếu không tìm thấy
    """
    for index, obj in enumerate(mang):
        if obj['ten'] == field_search:
            return index
    return None

# Ví dụ sử dụng
mang_test = [
    {"ten": "Nguyen", "tuoi": 25},
    {"ten": "Tran", "tuoi": 30},
    {"ten": "Le", "tuoi": 35}
]

# Tìm vị trí theo tên
ket_qua = find_index_by_name(mang_test, "tran")

if ket_qua is not None:
    print(f"Phần tử được tìm thấy tại vị trí: {ket_qua}")
else:
    print("Không tìm thấy phần tử")
