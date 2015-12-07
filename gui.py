# coding=utf-8
from Tkinter import *
import tkMessageBox
from tkFileDialog import askopenfilename
import xlrd
import pandas
import algorithm as alg
import os
import subprocess


class GUI:

    def __init__(self):
        self.sheet_list = ["Wybierz najpierw plik"]
        self.metric_list = ["Najbliższy sąsiad", "Najdalszy sąsiad"]
        self.listbox_height = 4
        self.button_width = 30
        self.filename = ""
        self.root = Tk()
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.excel_file = StringVar()
        subdirectories= [x[0] for x in os.walk(self.directory)]

        def get_visualisations_dir(subdirectory):
            for elem in subdirectory:
                if "wizualizacje" in elem:
                    return elem

        self.directory = get_visualisations_dir(subdirectories)
        self.sheet_listbox = Listbox(self.root, height=self.listbox_height, exportselection=0)
        self.metric_listbox = Listbox(self.root, height=self.listbox_height, exportselection=0)
        self.objects_mapping = {}  # Saves original objects names.

    def prepare_listboxes(self, l):
        self.sheet_listbox.grid(row=4)
        self.metric_listbox.grid(row=6)
        self.sheet_listbox.delete(0, END)
        self.metric_listbox.delete(0, END)

        for elem in l:
            self.sheet_listbox.insert(END, elem)
        for elem in self.metric_list:
            self.metric_listbox.insert(END, elem)

    def main(self):
        self.root.title("Dendryt")
        self.root.iconbitmap('icon.ico')
        self.root.resizable(width=FALSE, height=FALSE)
        self.prepare_listboxes(self.sheet_list)

        file_label = Label(self.root, text="Wybierz plik excela do wczytania")
        file_label.grid(row=0)

        sheet_lavel=Label(self.root, text="Wybierz arkusz z wybranego pliku excela")
        sheet_lavel.grid(row=3)

        file_button = Button(self.root, text="Wybierz plik", command=self.get_filename)
        file_button.grid(row=1)

        metric_label = Label(self.root, text="Wybierz sposób liczenia odległości między grupami")
        metric_label.grid(row=5)

        ok_button = Button(self.root, text="Stwórz dendryt", command=self.pressed)
        ok_button.grid(row=7)

        folder_button = Button(self.root, text="Otwórz folder z wizualizacjami", command=self.open_folder)
        folder_button.grid(row=8)
        self.root.mainloop()

    def open_folder(self):
        subprocess.Popen('explorer {}'.format(self.directory))

    def get_filename(self):
        self.filename = askopenfilename()
        self.excel_file.set(self.filename)
        xls = pandas.ExcelFile(self.filename)
        self.prepare_listboxes(xls.sheet_names)

    def pressed(self):
        print "Start calculations"
        try:
            print self.filename
            print self.sheet_listbox.get(self.sheet_listbox.curselection())
            excel = xlrd.open_workbook(str(self.filename))
            sheet = excel.sheet_by_index(self.sheet_listbox.curselection()[0])
            self.dendrite_data = self.get_excel_content(sheet)
            alg.run(self.dendrite_data, self.metric_listbox.get(self.metric_listbox.curselection()), self.objects_mapping)
        except (IndexError, TclError, IOError) as e:
            print "Error:",e
            tkMessageBox.showinfo("Błąd", "Wybierz poprawny plik, arkusz excela i sposób liczenia odleglości między grupami.")

    def set_objects_mapping(self, objects_list):
        for object in range(len(objects_list)):
            self.objects_mapping[object] = objects_list[object]

        print 'Maping:', self.objects_mapping

    def get_excel_content(self, excel_file):
        objects = []
        data = []
        num_cols = excel_file.ncols
        for row_idx in range(0, excel_file.nrows):    # Iterate through rows
            if row_idx != 0:
                data.append(excel_file.row_values(row_idx)[1:])
            else:
                print excel_file.row_values(row_idx)
                for col_idx in range(0, num_cols):
                    cell_obj = excel_file.cell(row_idx, col_idx)
                    objects.append(str(cell_obj.value))
        objects.pop(0)
        self.set_objects_mapping(objects)
        return data


if __name__ == '__main__':
    g = GUI()
    g.main()
