from Tkinter import *
import tkMessageBox
from tkFileDialog import askopenfilename
import sys
import xlrd
import pandas
import algorithm as alg

class GUI:

    def __init__(self):
        self.sheet_list = ["Wybierz najpierw plik"]
        self.listbox_height = 4
        self.filename = ""
        self.root = Tk()

        self.excel_file = StringVar()
        self.excel_file.set("testText1")

        self.listbox2 = Listbox(self.root, height=self.listbox_height, exportselection=0)
        self.objects_maping = {}  # Saves original objects names.

    def prepare_listbox(self,l):
        self.listbox2.grid(row=4)
        self.listbox2.delete(0, END)
        for elem in l:
            self.listbox2.insert(END, elem)

    def main(self):

        self.root.title("Dendryt")
        self.root.resizable(width=FALSE, height=FALSE)
        # self.root.geometry('{}x{}'.format(300, 300))
        self.prepare_listbox(self.sheet_list)

        label1 = Label(self.root, text="Wybierz plik excela do wczytania")
        label1.grid(row=0)


        label2=Label(self.root, text="Wybierz arkusz z wybranego pliku excela")
        label2.grid(row=3)

        file_button = Button(self.root, text="Wybierz plik", command=self.get_filename)
        file_button.grid(row=1)

        ok_button = Button(self.root, text="Ok", command=self.pressed)
        ok_button.config(width=10)
        ok_button.grid(row=5)
        self.root.mainloop()

    def get_filename(self):
        self.filename = askopenfilename()
        self.excel_file.set(self.filename)
        xls = pandas.ExcelFile(self.filename)
        self.prepare_listbox(xls.sheet_names)

        # print self.excel_file.get() # TODO: dodac Label z nazwa pliku?

    def pressed(self):
        print "Start calculations"
        try:
            print self.filename
            print self.listbox2.get(self.listbox2.curselection())
            excel = xlrd.open_workbook(str(self.filename))
            sheet = excel.sheet_by_index(self.listbox2.curselection()[0])
            self.get_excel_content(sheet)
            # sheet = read_excel(filename, sheetname=listbox2.get(listbox2.curselection())) # TODO: nie zczytuje excela
            # s = pandas.ExcelFile(filename)
            # s.parse(listbox2.get(listbox2.curselection()))
            # print_excel_content(s)
            # alg.run(0)
        except (IndexError, TclError) as e:
            print "Error:",e
            tkMessageBox.showinfo("Blad", "Wybierz plik i arkusz excela")

    def set_objects_maping(self, objects_list):
        c = 0
        for object in objects_list:
            self.objects_maping[c] = object
            c += 1

        print 'Maping:', self.objects_maping

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
        self.set_objects_maping(objects)
        self.data = data



if __name__ == '__main__':
    g = GUI()
    g.main()
