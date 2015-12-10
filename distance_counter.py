from math import sqrt
from pandas import read_excel

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
        n = len(self.excel_data)
        table = [[big_m for _ in range(n)] for _ in range(n)]

        for row in range(0, len(self.excel_data)):
            for row2 in range(0, len(self.excel_data)):
                distance = 0
                if row!=row2:
                    for col in self.excel_data.columns:
                        distance += (self.excel_data[col][row] - self.excel_data[col][row2]) ** 2
                    distance = sqrt(distance)

                    table[row][row2] = distance
                    table[row2][row] = distance
         return table

if __name__ == '__main__':
    c = Counter('DaneHelwig.xlsx','Dane')
    c.read_excel()
