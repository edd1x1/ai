import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Загрузка данных
df = pd.read_csv('turbo_cars.csv')

#сразу убираем дубликаты
df = df.drop_duplicates()

# print(df.isnull().sum())


#Дублирующие колонки и пустые их удаляем
columns_to_delete = [
    'specs_VIN',
    'specs_Комплектация',
    'specs_Коробка передач',
    'specs_Коробка',
    'specs_Мощность',

]

df.drop(columns=columns_to_delete,
        inplace=True,
        errors='ignore')

#добавленте бренда
df['brand'] = df['name'].str.split().str[0].str.lower()

#Замена и удаление значений
df['specs_Рассрочка'] = df['specs_Рассрочка'].fillna('Нет рассрочки')
df['specs_Гос номер'] = df['specs_Гос номер'].fillna('Гос номер не добавлен')
df['specs_Обмен'] = df['specs_Обмен'].fillna('Обмена нет')
df['specs_Прочее'] = df['specs_Прочее'].fillna('Нет информации')
df['specs_Пробег'] = df['specs_Пробег'].astype(str).str.replace(' км', '', case=False)
df['specs_Пробег'] = pd.to_numeric(df['specs_Пробег'], errors='coerce')
df['Пробег_Итоговый'] = df['millage_km'].combine_first(df['specs_Пробег'])

df = df.dropna(subset=['year_from_catalog'])


# перевод в дату 
df['published_at'] = pd.to_datetime(df['published_at']).dt.date


#Деление по объему и типу топлива
split_v = df['specs_Двигатель'].str.split('/', n=1, expand=True)
df['specs_Объем двигателя'] = split_v[0].str.strip().str.extract(r'(\d+\.\d+|\d+)')[0].astype(float)
df['specs_Тип топлива'] = split_v[1].str.strip()


# print(df.isnull().sum())
# print(df.shape) 
# print(df.duplicated().sum()) # нет дубликатов
# print(df.describe())

#Анализ цен
# print(df.groupby('brand')['price'].median().sort_values(ascending=False))

top_brands = df['brand'].value_counts().head(10).index
plt.figure(figsize=(12, 5))
sns.boxplot(data=df[df['brand'].isin(top_brands)], x='brand', y='price')
plt.xticks(rotation=45)
plt.title('Распределение цен по топ-10 брендам')
plt.ylabel('Цена (сом)')
plt.xlabel('')
plt.tight_layout()
# plt.show()

#Выброс
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df[df['price'] > upper][['name', 'price', 'brand']]
# print(f"Границы: {lower} — {upper} сом")
# print(f"Выбросов: {len(outliers)}")
# print(outliers.sort_values('price', ascending=False))


# # Анализ года выпуска машин
print(df['year_from_catalog'].mode()) #2021
print(df['year_from_catalog'].median()) #2020
plt.figure(figsize=(10, 4))
sns.histplot(df['year_from_catalog'].dropna(), kde=True)
plt.title('Распределение годов выпуска машин') # в основмном 2018-2021 годов, самый старый - 1981, макс - 2026
plt.show()


#Анализ кузова
count_categories = df['specs_Кузов'].nunique()
frequencies = df['specs_Кузов'].value_counts(normalize=True)
print(f"Количество уникальных типов кузова: {count_categories}")
print(df['specs_Кузов'].unique())
print(f'Частые кузовы авто {frequencies}')



#Тепловая карта
numeric_cols = ['price', 'year_from_catalog', 'specs_Объем двигателя', 'Пробег_Итоговый']

plt.figure(figsize=(8, 6))
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Корреляция числовых признаков')
plt.tight_layout()
plt.show()