
from math import sqrt
from pandas import read_excel
import pandas as pd

big_m = 99999999999

class Counter:

    def __init__(self, filename, sheet_name):
        self.filename = filename
        self.sheet_name = sheet_name
        self.excel_data = read_excel(filename, sheetname=self.sheet_name)
        self.objects = []
        self.distance_matrix = []

    def read_excel(self):
        first_col = self.excel_data.iloc[:, 0]
        self.objects = [_ for _ in first_col]
        self.get_distance_matrix()

    def get_distance_matrix(self):
        n= len(self.excel_data)
        table = [[big_m for _ in range(n)] for _ in range(n)]

        for row in range(0, len(self.excel_data) - 1):
            distance = 0
            
            for col in self.excel_data.columns:
                distance += (self.excel_data[col][row] - self.excel_data[col][row+1]) ** 2
                distance = sqrt(distance)
            # table[col][row] = distance
            # table[row][col] = distance
            #     print row,
        for x in table:
            print x

if __name__ == '__main__':
    c = Counter('DaneHelwig.xlsx','Dane')
    c.read_excel()

"""
for row:
    for row2:
        distance = 0
        if row!=row2:
            for column:
                distance+= (data[col][row]-data[col][row2])**2
            distance = sqrt(distance)
            table[row][row2] = distance
            table[row2][row] = distance

"""