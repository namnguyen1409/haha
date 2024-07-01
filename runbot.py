import subprocess

subprocess.call(["python", r"D:\Users\Namnguyen\Documents\DISK D\crawlebook\lightnovel-crawler\lncrawl", "--bot", "telegram"])
# subprocess.call(["python", r"C:\Users\Namnguyen\Documents\DISK D\crawlebook\lightnovel-crawler\lncrawl", "--bot", "telegram"])


# def in_danh_sach_dao_nguoc(danh_sach):
#     # Chuẩn bị một ngăn xếp (stack) rỗng
#     stack = []

#     # Đẩy từng phần tử của danh sách vào ngăn xếp
#     for phan_tu in danh_sach:
#         stack.append(phan_tu)
#         print(stack)

#     # Lấy và in ra các phần tử từ ngăn xếp theo thứ tự ngược lại
#     while stack:
#         phan_tu = stack.pop()
#         print(phan_tu)
#         print(stack)

# # Sử dụng hàm in_danh_sach_dao_nguoc
# danh_sach = [1, 2, 3, 4, 5]
# in_danh_sach_dao_nguoc(danh_sach)


# data = ["soft drink menu", 
#         "1. Adding a new soft drink", 
#         "Printing the list in ascending order based on volumes then prices", 
#         "2. Printing out items which belong to a known make", 
#         "3. Printing out items whose volumes are between v1 and v2",
#         "4. Printing the list in ascending order based on volumes then prices",
#         "5. Quit"]

# width = 100
# print(f'printf("|{"-"*width}|\\n");')
# for i in data:
#     print(f'printf("|{" "*int((width -len(i))/2)}{i}{" "*int((width -len(i))/2)}|\\n");')
    # print(f'printf("|{i}{" "*int((width -len(i)))}|\\n");')


# do_uong = ["ca phe", "tra", "nuoc loc", "soda", "bia", "nuoc cam", "nuoc tao", "nuoc chanh", "nuoc dua", "sua"]
# nha_san_xuat = ["coca cola", "pepsico", "nestle", "starbucks", "red bull", "danone", "unilever", "vinamilk"]
# the_tich = [100, 150, 180, 200, 400, 500, 800, 1000]
# gia = [5000, 10000, 15000, 20000, 30000, 40000, 50000]

# from unidecode import unidecode
# import random
# import pyautogui
# from time import sleep

# # sleep(1)
# # for i in range(0, 50):
# #     pyautogui.write("1")
# #     pyautogui.press('enter')
# #     sleep(0.2)
# #     pyautogui.write(random.choice(do_uong))
# #     pyautogui.press('enter')
# #     sleep(0.2)
# #     pyautogui.write(random.choice(nha_san_xuat))
# #     pyautogui.press('enter')
# #     sleep(0.2)    
# #     pyautogui.write(unidecode(str(random.choice(the_tich))))
# #     pyautogui.press('enter')
# #     sleep(0.2)
# #     pyautogui.write(unidecode(str(random.choice(gia))))
# #     pyautogui.press('enter')
# #     sleep(0.2)
# #     pyautogui.press('enter')
# #     sleep(0.2)
# import math
# while True:
#     a = int(input("a: "))
#     print(a % 512)