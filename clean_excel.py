import pandas as pd

# Excel 檔案路徑
excel_path = '附件二、2026團隊名單_尾牙_TO人資 (1).xlsx'
xl = pd.ExcelFile(excel_path)

# 用 set 去重複
all_names = set()

# 數據表單：姓名、部門
df1 = pd.read_excel(xl, sheet_name='數據')
for _, row in df1.dropna(subset=['姓名']).iterrows():
    dept = row['部門'] if pd.notna(row['部門']) else ''
    all_names.add((row['姓名'], dept))

# 戰情表單：姓名、戶籍部門
df2 = pd.read_excel(xl, sheet_name='戰情')
for _, row in df2.dropna(subset=['姓名']).iterrows():
    dept = row['戶籍部門'] if pd.notna(row['戶籍部門']) else ''
    all_names.add((row['姓名'], dept))

# 數發表單：姓名、部門
df3 = pd.read_excel(xl, sheet_name='數發')
for _, row in df3.dropna(subset=['姓名']).iterrows():
    dept = row['部門'] if pd.notna(row['部門']) else ''
    all_names.add((row['姓名'], dept))

# 按姓名排序
sorted_names = sorted(all_names, key=lambda x: x[0])

# 寫入 txt
output_path = '清理後名單.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('姓名\t部門\n')
    for name, dept in sorted_names:
        f.write(f'{name}\t{dept}\n')

print(f'完成！共 {len(sorted_names)} 筆不重複資料，已儲存到 {output_path}')
