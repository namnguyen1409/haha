import hashlib

print(hashlib.md5(open('D:\crawlebook\lightnovel-crawler\sources\multi\\blogspot.py', encoding='utf-8').read().encode()).hexdigest())