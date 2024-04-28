import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from time import sleep
import re
import os
from docx import Document
from docx.shared import Inches

#  Запустите программу и разместите ее изображение
st.title(" 📊 Project Productivity Professional ")
st.markdown("---")
st.write('')
st.sidebar.title('***📊Добро пожаловать📊***')
st.sidebar.markdown("---")
image = Image.open("142.jpeg")
st.sidebar.image(image, caption='', use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.title("Информация о проекте")
# Установка максимального количества ячеек для отображения в Pandas Styler
pd.set_option("styler.render.max_elements", 559776)

# Кнопки "Разработчики" و "График" для главного выключателя
st.sidebar.title("Расчет трудоемкости")
show_upload_button = st.sidebar.checkbox("Разработчики")
# Добавление кнопки для отображения Просмотр каждого разработчика
show_dashboard = st.sidebar.checkbox("Просмотр каждого разработчика")
show_chart_button = st.sidebar.checkbox("Показать график")
# Загрузка файла журнала
if show_upload_button:
    st.write('')
    uploaded_files = st.sidebar.file_uploader("Выберите файл журнала (Log file)", type=['log'])  # Кнопка загрузки файла Log
    if uploaded_files is not None:  
        # Чтение данных из файла Log
        log_content = uploaded_files.readlines()

        # Преобразуйте содержимое в строки
        lines = [line.decode().strip() for line in log_content]

        # Разделите строки и удалите пустые строки
        lines = [line.strip() for line in lines if line.strip()]

        # Разделите каждую строку на две части с помощью вертикальной черты
        data = [line.split('|')[:2] for line in lines if '|' in line]

        # Создание DataFrame
        df = pd.DataFrame(data, columns=['Дата и время', 'Разработчики'])
        show_upload_button = st.sidebar.checkbox("Общий протокол")
        if show_upload_button:
          st.write('Общий протокол')
          df
        # Применение шаблона к именам пользователей
        pattern = re.compile(r'^[А-Яа-я]+\s[А-Яа-я]+$|^\w+\s\w+$')  
        df = df[df['Разработчики'].apply(lambda x: bool(pattern.match(x.strip())))]  
        
        # Объединение столбцов 'Дата' и 'время' в новый столбец 'Общее время'
        df['Общее время'] = pd.to_datetime(df['Дата и время'], errors='coerce')
        
        # Группировка данных по столбцу 'Разработчики'
        grouped_data = df.groupby('Разработчики')
        
        # Создание пустого списка для хранения результатов (с и без времени отдыха)
        results = []
        cleaned_results = []

        # Вычисление общего времени для каждого разработчика (включая исключение времени отдыха < 30 минут)
        for name, group in grouped_data:
            # Вычисляем разницу во времени
            time_diffs = group['Общее время'].diff().fillna(pd.Timedelta(seconds=0))

            # Исключаем периоды отрицательного времени
            time_diffs = time_diffs[time_diffs >= pd.Timedelta(seconds=0)]

            # Вычисляем общее время после исключения отрицательного времени
            total_time_seconds = time_diffs.sum().total_seconds()

            # Преобразование времени в дни, часы, минуты и секунды
            days, remainder = divmod(total_time_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Форматирование времени
            formatted_time = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minute, {int(seconds)} seconds"

            # Добавление результатов в список
            results.append({'Разработчики': name, 'Время': formatted_time})

            # Исключаем периоды времени отдыха более 30 минут
            time_diffs = time_diffs[time_diffs <= pd.Timedelta(minutes=30)]

            # Вычисляем общее время после исключения отрицательного времени и времени отдыха
            total_time_seconds = time_diffs.sum().total_seconds()

            # Преобразование времени в дни, часы, минуты и секунды
            days, remainder = divmod(total_time_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Форматирование времени
            formatted_time = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minute, {int(seconds)} seconds"

            # Добавление результатов в список
            cleaned_results.append({'Разработчики': name, 'Время': formatted_time})
        
        # Создание DataFrame из результатов с и без времени отдыха
        results_df = pd.DataFrame(results)
        cleaned_results_df = pd.DataFrame(cleaned_results)

        # Вывод результатов в виде таблиц
        st.write('Трудоемкость разработчиков:')
        st.write(results_df)
        st.write('Трудоемкость разработчиков (без времени отдыха < 30 минут):')
        st.write(cleaned_results_df)
        
 
        # Добавление кнопки для отображения Просмотр каждого разработчика
        if show_dashboard:
            st.markdown("---")
            # Получение списка всех имен сотрудников
            developers = cleaned_results_df['Разработчики'].unique()

            # Создание выпадающего списка для выбора сотрудника
            selected_developers = st.multiselect("Выберите разработчиков", developers)

            # Фильтрация данных для выбранных сотрудников
            if selected_developers:
                filtered_data = cleaned_results_df[cleaned_results_df['Разработчики'].isin(selected_developers)]
                for developer in selected_developers:
                    st.write(f"Сводная таблица для {developer}:")
                    st.write(filtered_data[filtered_data['Разработчики'] == developer])
