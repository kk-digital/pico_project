import pandas as pd

# 定义要读取的CSV文件路径
csv_file_path = 'data/Na2SO4/1/A/channelA.csv'

# 定义你要查找的片段
substring = 'type=1,'

# 读取CSV文件
df = pd.read_csv(csv_file_path)

# 筛选列名中包含指定片段的列
filtered_columns = df.columns.str.contains(substring, na=False)

# 只保留包含指定片段的列
filtered_df = df.iloc[:,filtered_columns]

# 显示结果
print(filtered_df)
