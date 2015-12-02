from Tkinter import *
import tkMessageBox
from tkFileDialog import askopenfilename

sheet_list = ["Arkusz1","Arkusz2", "Arkusz3"] # TODO
listbox_height = 4

root = Tk()

excel_file = StringVar()
excel_file.set("testText1")

listbox2 = Listbox(root, height=listbox_height, exportselection=0)

#label_file = Label(root, textvariable=excel_file)
#label_file.grid(row=2)
#label_file.pack()

def prepare_listbox():
    listbox2.grid(row=4)
    for elem in sheet_list:
        listbox2.insert(END, elem)

def main():

    root.title("Dendryt")
    root.resizable(width=FALSE, height=FALSE)
    root.geometry('{}x{}'.format(220, 220))
    prepare_listbox()

    label1 = Label(root, text="Wybierz plik excela do wczytania")
    label1.grid(row=0)


    label2=Label(root, text="Wybierz arkusz z wybranego pliku excela")
    label2.grid(row=3)

    file_button =Button(root, text="Wybierz plik", command=get_filename)
    file_button.grid(row=1)

    ok_button = Button(root, text="Ok", command=pressed)
    ok_button.config(width=10)
    ok_button.grid(row = 5)
    root.mainloop()

def get_filename():
    filename = askopenfilename()
    excel_file.set(filename)
    print excel_file.get() # TODO: dodac Label z nazwa pliku?

def pressed():
    print "Start calculations"
    try:
        print sheet_list[listbox2.curselection()[0]]
    except IndexError:
        tkMessageBox.showinfo("Blad", "Wybierz plik i arkusz excela")

if __name__ == '__main__':
    main()
