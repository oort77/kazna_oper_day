# !/Users/gm/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
#  File: kazna_oper_day.py
#  Project: 'kazna_oper_day'
#  Created by Gennady Matveev (gm@og.ly) on 27-07-2021.
#  Copyright 2021. All rights reserved.

# This script reads an xml file, downloaded from
# https://roskazna.gov.ru/finansovye-operacii/operacionnyj-den/,
# and converts it to an Excel file.

# import libraries
import pandas as pd
import os
import xlsxwriter

path = '/Users/gm/Downloads/'  # change path if needed
entries = os.listdir(path)
xml_files = []
for filename in entries:
    if filename.split('.')[-1] == 'xml' and 'operday' in filename:
        xml_files.append(filename)
print('------------------------------------------')
print('You have the following xml files in ~/Downloads:\n')

for i, filename in enumerate(xml_files, start=1):
    print(f'{i}. {filename}')
print('------------------------------------------')

# input loop
got_it = False

while got_it == False:
    n = input('Please type the file number:\n\n') or '1'
    if int(n)-1 in range(len(xml_files)):
        xml_file = xml_files[int(n)-1]
        got_it = True
    else:
        print('Oops, wrong choice...\n')

# read xml data to pandas dataframe
# df = pd.read_xml('./data/operday_2307787163.xml')
# df = pd.read_xml('./data/operday_2307787163.xml')
df = pd.read_xml(path+xml_file)
df.set_index('Num', inplace=True)

# new order for columns
new_order = [
    'OperDate', 'DepoSum', 'DepoUsdSum', 'DepoMeanRate', 'DepoCntDay',
    'DepoCntOrg', 'DepoOstRub', 'DepoOstUsd', 'RepoSUM', 'RepoUsdSUM',
    'RepoMeanRate', 'RepoCntDay', 'RepoCntOrg', 'RepoOst', 'RepoOstUsd',
    'KredSum', 'BSOst', 'SwopSum', 'SwopCurr', 'DepoCKSum', 'DepoCKMeanRate',
    'DepoCKCntDay', 'DepoCKOstRub'
]
# top-level names for multiindex
m = [
    'Размещено на банковских депозитах', 'Размещено по договорам репо',
    'Предоставлено бюджетных кредитов', 'Остаток на банковских счетах',
    'Размещено по валютным свопам',
    'Размещено на депозитах с центральным контрагентом'
]
# columns names in Russian
new_col_names = [
    'Дата',
    'Сумма, млн рублей',
    'Сумма, млн долларов США',
    'Средневзвешенная процентная ставка (фиксированная или спред), %',
    'Срок, дней',
    'Количество кредитных организаций, заявки которых удовлетворены, шт.',
    'Остаток к возврату, млн рублей',
    'Остаток к возврату, млн долларов США',
    'Сумма, млн рублей',
    'Сумма, млн долларов США',
    'Средневзвешенная процентная ставка (фиксированная или спред), %',
    'Срок, дней',
    'Количество кредитных организаций, заявки которых удовлетворены, шт.',
    'Остаток к возврату, млн рублей',
    'Остаток к возврату, млн долларов США',
    'Сумма, млн рублей',  # 'Остаток к возврату, млн рублей',
    'Остаток средств, млн рублей',
    'Сумма, млн рублей',
    'Купленная валюта',
    'Сумма, млн рублей',
    'Средневзвешенная процентная ставка (фиксированная или спред), %',
    'Срок, дней',
    'Остаток к возврату, млн рублей'
]
# columns to scale by 1 mio
mln_cols = [
    'DepoSum', 'RepoSUM', 'KredSum', 'BSOst', 'DepoUsdSum', 'DepoOstRub',
    'DepoOstUsd', 'RepoOst', 'SwopSum', 'RepoOstUsd', 'RepoUsdSUM',
    'DepoCKSum', 'DepoCKOstRub'
]
# columns to convert to integers
int_cols = [
    'DepoCntDay', 'RepoCntDay', 'DepoCntOrg', 'RepoCntOrg', 'DepoCKCntDay'
]
# multiindex mapping
multi = [
    ' ', m[0], m[0], m[0], m[0], m[0], m[0], m[0], m[1], m[1], m[1], m[1],
    m[1], m[1], m[1], m[2], m[3], m[4], m[4], m[5], m[5], m[5], m[5]
]

df.fillna('', inplace=True)

# scale by 1_000_000
for col in mln_cols:
    df[col] = df[col].apply(lambda x: x if x == '' else int(int(x) / 1000000))
# convert to integers
for col in int_cols:
    df[col] = df[col].apply(lambda x: x if x == '' else int(x))

# change columns order and give them Russian names
df1 = df[new_order]
df1.columns = new_col_names
df2 = df1.T

# create multiindex
df2.index = [multi, df2.index]

# write results to Excel file to ~/Downloads folder

# create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(path + 'kazna_oper_day__.xlsx', engine='xlsxwriter')

# convert the dataframe to an XlsxWriter Excel object.
df2.to_excel(writer, sheet_name='Операционный день казначейства')

# cet the xlsxwriter workbook and worksheet objects.
workbook = writer.book
worksheet = writer.sheets['Операционный день казначейства']

# Add some cell formats.
# format_idx0 = workbook.add_format({'bold': True,  # font bold
#                                    #    'border': 1,  # Cell border width
#                                    'align': 'left',  # alignment
#                                    'valign': 'top',  # font alignment
#                                    'text_wrap': True  # wrap text
#                                    })

format_mln_row = workbook.add_format({'num_format': '#,##0'})

# Note: It isn't possible to format any cells that already have a format such
# as the index or headers or any cells that contain dates or datetimes.

# Set the column width and format.
# worksheet.set_column('A:A', 30, format_idx0)

# set mln rows
mln_rows = [2, 3, 7, 8, 9, 10, 14, 15, 16, 17, 18, 20, 23]
for row in mln_rows:
    worksheet.set_row(row, None, format_mln_row)

# Close the Pandas Excel writer and output the Excel file.
writer.save()

print('\n', df2.iloc[:5, :5], '\n')

print('Tutto opossum!\n')
