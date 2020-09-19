from tkinter import *
import datetime , dbm , os , pickle
from tkinter import filedialog
import pandas as pd
import numpy as np

class Book:
    all_book = np.array([])
    categories = {}
    def __init__(self,name,writer,n_copies,ISBN,subject=None):
        self.name = name
        self.writer = writer
        self.n_copies = n_copies
        self.subject = subject
        self.ISBN = ISBN
        self.who_taken = []
        Book.all_book = np.append(Book.all_book,self)
        if self.subject is not None:
            if self.subject not in Book.categories:
                Book.categories.setdefault(self.subject,[])
                Book.categories[self.subject].append(self)
    def check_can_take(self):
        if len(self.who_taken) < self.n_copies:
            return True
        else:
            return False
    def __repr__(self):
        return f'{self.name} ({self.writer})'

class User:
    all_user = np.array([])
    def __init__(self,user_name,user_credit=3):
        self.user_name = user_name
        self.user_credit= user_credit
        # self.taken_books = []
        self.taken_books = {}
        User.all_user = np.append(User.all_user,self)
    def __repr__(self):
        return self.user_name

    def remove_book(self,given_book):
        del self.taken_books[given_book]
        # self.taken_books.remove(given_book)
        given_book.who_taken.remove(self)
        self.user_credit+=1
    def add_book(self,given_book):
        if self.user_credit > 0:
            self.taken_books[given_book] = datetime.datetime.now().replace(microsecond=0)
            given_book.who_taken.append(self)
            self.user_credit-=1
    def expiration_time(self,given_book):
        return self.taken_books[given_book]+datetime.timedelta(days=7)
        
    def credit_control(self):
        """[summary]

        Returns:
            Bool -> IF CREDIT > 0 RETURN TRUE
        """
        if self.user_credit > 0:
            return True
        else:
            return False

class GUI(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.check = False
        self.initGUI()
        self.grid()
        if "BOOKSINFORMATIONS.db.dir" in os.listdir():
            print("Database founded")
            with dbm.open("BOOKSINFORMATIONS.db","c") as database:
                Book.all_book = pickle.loads(database["BOOKS"])
                print(type(Book.all_book))
                User.all_user = pickle.loads(database["USERS"])
                print(type(User.all_user))
                Book.categories = pickle.loads(database["CATS"])
        else:
            print("No Database Founded")
            
    def initGUI(self):
        Label(self,text="Libary System",bg="green",fg="white").grid(row=0,column=0,sticky=E+W+S+N,padx=10,pady=10)
        FRAME = Frame(self,relief=GROOVE,borderwidth=3)
        FRAME.grid(row=1,column=0,padx=10,pady=10,sticky=E+W+S+N)

        Label(FRAME,text="Library Functions",fg="red",bg="aqua").grid(row=0,column=0,padx=10,pady=10,sticky=E+W+S+N,columnspan=3)
        self.check_books_Button = Button(FRAME,text="Check Book", command=lambda:self.check_book(check=True))
        self.check_books_Button.grid(row=1,column=0,padx=10,pady=10,sticky=E+W+S+N)
        
        self.add_books_Button = Button(FRAME,text="Add Book",command=self.AddBook)
        self.add_books_Button.grid(row=1,column=1,padx=10,pady=10,sticky=E+W+S+N)

        self.add_user_Button = Button(FRAME,text="Add User",command=self.AddUser)
        self.add_user_Button.grid(row=1,column=2,padx=10,pady=10,sticky=E+W+S+N)

        self.delete_books_Button = Button(FRAME,text="Delete Books",command=lambda:self.check_book(check=False))
        self.delete_books_Button.grid(row=2,column=0,padx=10,pady=10,sticky=E+W+S+N)
        
        self.delete_user_Button = Button(FRAME,text="Add Book With XLSX",command=self.getPATH)
        self.delete_user_Button.grid(row=2,column=1,padx=10,pady=10,sticky=E+W+S+N)

        self.take_book = Button(FRAME,text="Take Book",command = self.take_book_funct)
        self.take_book.grid(row=2,column=2,padx=10,pady=10,sticky=E+W+S+N)

    def UploadDatabase(self,user=False,both=False):
        with dbm.open("BOOKSINFORMATIONS.db","c") as database:
            if both:
                database["BOOKS"] = pickle.dumps(Book.all_book)
                database["CATS"] = pickle.dumps(Book.categories)
                database["USERS"] = pickle.dumps(User.all_user)
            else:
                if user:
                    database["USERS"] = pickle.dumps(User.all_user)
                else:
                    database["BOOKS"] = pickle.dumps(Book.all_book)
                    database["CATS"] = pickle.dumps(Book.categories)
    def getPATH(self):
        get_path=str(filedialog.askopenfilename(filetypes=(("xlsx files","*.xlsx"),("all files","*.*"))))
        self.getEXCELL(path=get_path)
    
    def getEXCELL(self,path):
        df = pd.read_excel(path)
        for a in range(len(df)):
            ISBN = df.loc[a,'ISBN']
            TITLE = df.loc[a,'TITLE']
            AUTH = df.loc[a,'AUTHOR']
            NCOPY = df.loc[a,'NCOPIES']
            if len(Book.all_book) > 0:
                for b_obj in Book.all_book:
                    should_continue=False
                    if b_obj.name == str(TITLE):
                        should_continue = True
                if should_continue:
                    continue
                else:
                    Book(name=str(TITLE),writer=str(AUTH),n_copies=int(NCOPY),ISBN=str(ISBN))    
            else:
                Book(name=str(TITLE),writer=str(AUTH),n_copies=int(NCOPY),ISBN=str(ISBN))


    def take_book_funct(self):
        toplevel = Toplevel(self)
        toplevel.title("Take a Book")
        frame = Frame(toplevel,relief=GROOVE,borderwidth=3)
        frame.grid(row=0,column=0,padx=10,pady=10)
        Label(frame,text="Select User").grid(row=0,column=0,padx=10,pady=10)
        self.find_user_entry = Entry(frame)
        self.find_user_entry.grid(row=1,column=0,padx=10,pady=10)
        self.find_user_entry.bind("<Enter>",self.user_key_event)
        self.all_users_listbox = Listbox(frame,exportselection=0)
        self.all_users_listbox.grid(row=2,column=0,padx=10,pady=10)
        for a in User.all_user:self.all_users_listbox.insert(END,a)
        
        self.all_users_listbox.bind("<<ListboxSelect>>",lambda event:self.books_clicked(event=event,user=True))


        self.other_frame = Frame(toplevel,relief=GROOVE,borderwidth=3)
        self.other_frame.grid(row=0,column=1,padx=10,pady=10)


        Label(self.other_frame,text="Select Book").grid(row=0,column=0,padx=10,pady=10)
        self.find_books_entry = Entry(self.other_frame)
        self.find_books_entry.grid(row=1,column=0,padx=10,pady=10)

        self.b_lb = Listbox(self.other_frame)
        self.b_lb.grid(row=2,column=0,padx=10,pady=10)
        self.b_lb.bind("<<ListboxSelect>>",self.books_clicked)


        for b in Book.all_book:self.b_lb.insert(END,b)
        self.find_books_entry.bind("<Enter>",lambda event:self.s_book_event(event=event,given_listbox=self.b_lb))

        self.take_bk = Button(self.other_frame,text="Take Book",command=self.take_book_now)
        self.take_bk.grid(row=3,column=0,padx=10,pady=10)    
    def take_book_now(self):
        for user in User.all_user:
            if user.user_name == self.current_user:
                self.current_user = user
                break
        if self.current_user.credit_control():
            if self.current_book_obj.check_can_take():
                self.current_user.add_book(given_book = self.current_book_obj)
                print(self.current_user.taken_books)
                self.UploadDatabase(both=True)
                taked = Label(self.other_frame,text="Book Has ben Added to User",bg="green")
                self.original_setting(taked)

            else:
                taked = Label(self.other_frame,text="Limit is Full",bg="red")
        else:
            taked = Label(self.other_frame,text="Limit is Full",bg="red")
            # self.original_setting(taked)
        taked.grid(row=4,column=0,padx=10,pady=10)
        self.original_setting(taked)
    def original_setting(self,label):
        try:
            self.after(2000,lambda : label.configure(text="",bg="SystemButtonFace"))
        except:pass
    def user_key_event(self,event):
        current_entry = event.widget
        current_word = current_entry.get()
        if current_word != "":
            self.all_users_listbox.delete(0,END)
            for user in User.all_user:
                if user.user_name[:len(current_word)] == current_word:
                    self.all_users_listbox.insert(END,user)
                else:continue
        else:
            self.all_users_listbox.delete(0,END)
            for u in User.all_user:self.all_users_listbox.insert(END,u)
        
    def AddUser(self):
        toplevel = Toplevel(self)
        toplevel.title("Add an User")
        self.ADD_USER_FRAME = Frame(toplevel,borderwidth=3,relief=GROOVE)
        self.ADD_USER_FRAME.grid(row=0,column=0,padx=10,pady=10)

        Label(self.ADD_USER_FRAME, text="User Name").grid(row=0,column=0,padx=10,pady=10)
        self.add_user_name = Entry(self.ADD_USER_FRAME)
        self.add_user_name.grid(row=0,column=1,padx=10,pady=10,sticky=W)

        Label(self.ADD_USER_FRAME,text="Maximum Book Credit:").grid(row=1,column=0,padx=10,pady=10)
        self.add_user_credit = Entry(self.ADD_USER_FRAME)
        self.add_user_credit.grid(row=1,column=1,padx=10,pady=10,sticky=W)
        self.add_user_credit.insert(END,"3")

        self.add_User_Now = Button(self.ADD_USER_FRAME,text="Add User Now",command=self.addUserNow)
        self.add_User_Now.grid(row=2,column=0,padx=10,pady=10,sticky=E+W+S+N,columnspan=2)
    
    def addUserNow(self):
        if self.add_user_name.get() != "" and self.add_user_credit.get() != "":
            try:
                credit = int(self.add_user_credit.get())
                User(self.add_user_name.get(),credit)
                print(User.all_user)
            except:
                Label(self.ADD_USER_FRAME,text="INCORRECT INFORMATIONS",bg="red").grid(row=3,column=0,padx=10,pady=10,columnspan=2, sticky=E+W+S+N)
            else:
                Label(self.ADD_USER_FRAME,text="SUCCESSFULLY ADDED",bg="green").grid(row=3,column=0,padx=10,pady=10,columnspan=2, sticky=E+W+S+N)
                self.UploadDatabase(user=True)
        else:
            Label(self.ADD_USER_FRAME,text="INCORRECT INFORMATIONS",bg="red").grid(row=3,column=0,padx=10,pady=10,columnspan=2, sticky=E+W+S+N)

    def AddBook(self):
        toplevel = Toplevel(self)
        toplevel.title("Add a Book")
        self.ADD_BOOK_FRAME = Frame(toplevel,relief=GROOVE,borderwidth=3)
        self.ADD_BOOK_FRAME.grid(row=0,column=0,padx=10,pady=10)

        Label(self.ADD_BOOK_FRAME,text="Book Name:").grid(row=0,column=0,padx=10,pady=10)

        self.add_Book_name = Entry(self.ADD_BOOK_FRAME)
        self.add_Book_name.grid(row=0,column=1,padx=10,pady=10,sticky=W)

        Label(self.ADD_BOOK_FRAME,text="Book Writer:").grid(row=1,column=0,padx=10,pady=10)

        self.add_book_writer = Entry(self.ADD_BOOK_FRAME)
        self.add_book_writer.grid(row=1,column=1,padx=10,pady=10,sticky=W)

        Label(self.ADD_BOOK_FRAME,text="Number of Copies:").grid(row=2,column=0,padx=10,pady=10)
        self.add_book_copies = Entry(self.ADD_BOOK_FRAME)
        self.add_book_copies.grid(row=2,column=1,padx=10,pady=10,sticky=W)

        Label(self.ADD_BOOK_FRAME,text="ISBN:").grid(row=3,column=0,padx=10,pady=10)
        self.add_book_isbn = Entry(self.ADD_BOOK_FRAME)
        self.add_book_isbn.grid(row=3,column=1,padx=10,pady=10,sticky=W)

        Label(self.ADD_BOOK_FRAME,text="Subject(Not Important): ").grid(row=4,column=0,padx=10,pady=10)
        
        self.add_book_subject = Entry(self.ADD_BOOK_FRAME)
        self.add_book_subject.grid(row=4,column=1,padx=10,pady=10,sticky=W)

        

        self.create_new_book_button = Button(self.ADD_BOOK_FRAME,text="Add New Book Now",command=self.AddBookNow)
        self.create_new_book_button.grid(row=5,column=0,padx=10,pady=10,sticky=W+S+N+E,columnspan=2)
        
        self.sideFrame = Frame(toplevel,borderwidth=3,relief=GROOVE)
        self.sideFrame.grid(row=0,column=1,padx=10,pady=10)

        Label(self.sideFrame,text="Increase Existing Books \nNumber of Copies",bg="yellow").grid(row=0,column=0,padx=10,pady=10,columnspan=4,sticky=E+W+S+N)

        Label(self.sideFrame,text="Search Book").grid(row=1,column=0,pady=10,sticky=S)
        self.srch = Entry(self.sideFrame)
        self.srch.grid(row=2,column=0,padx=3,pady=10)

        self.srchlb = Listbox(self.sideFrame,exportselection=0)
        self.srchlb.grid(row=3,column=0,padx=10,pady=10,rowspan=3)
        for b in Book.all_book: self.srchlb.insert(END,b)
        
        self.srchlb.bind("<<ListboxSelect>>",lambda event:self.books_clicked(event=event,user=False,setCPS=True))
        self.srch.bind("<Enter>",lambda event:self.s_book_event(event=event,given_listbox=self.srchlb))

        self.minusButton = Button(self.sideFrame,text="-",command=lambda:self.incresaseDecrease(increase=False))
        self.minusButton.grid(row=2,column=1,pady=10,padx=15,sticky=E)

        self.setEntry = Entry(self.sideFrame,width=5)
        self.setEntry.grid(row=2,column=2,pady=10)

        self.incButton = Button(self.sideFrame,text="+",command=lambda:self.incresaseDecrease(increase=True))
        self.incButton.grid(row=2,column=3,pady=10,padx=10,sticky=W)

        self.setnow = Button(self.sideFrame,text="Set Now",command=self.setNEWCPSNOW)
        self.setnow.grid(row=3,column=2,padx=10,pady=10,sticky=N)
    def setNEWCPSNOW(self):
        if self.setEntry.get() != "":
            try:
                self.current_book_obj.n_copies = int(self.setEntry.get())
                self.UploadDatabase(both=True)
            except:
                LABEL = Label(self.sideFrame,text="Should be INTEGER",bg="red")
                LABEL.grid(row=4,column=2,padx=10,pady=10,sticky=E+W+S+N)
                self.original_setting(LABEL)
        else:
            LABEL = Label(self.sideFrame,text="Should be INTEGER",bg="red")
            LABEL.grid(row=4,column=2,padx=10,pady=10,sticky=E+W+S+N)
            self.original_setting(LABEL)
    def incresaseDecrease(self,increase=False):
        if self.setEntry.get() != "":
            try:
                get_int = int(self.setEntry.get())
            except:
                LABEL = Label(self.sideFrame,text="Should be INTEGER",bg="red")
                LABEL.grid(row=4,column=2,padx=10,pady=10,sticky=E+W+S+N)
                self.original_setting(LABEL)
                print("INTEGER OLMALI")
            else:
                self.setEntry.delete(0,END)
                if increase:
                    get_int+=1
                else:
                    get_int-=1
                self.setEntry.insert(END,str(get_int))
        else:
            LABEL = Label(self.sideFrame,text="Should be INTEGER",bg="red")
            LABEL.grid(row=4,column=2,padx=10,pady=10,sticky=E+W+S+N)
            self.original_setting(LABEL)
            print("cant be empty")
        
    def AddBookNow(self):
        if self.add_Book_name.get() != "" and self.add_book_copies != "" and self.add_book_writer != "" \
           and  self.add_book_isbn.get() != "":
            try:
                copies = int(self.add_book_copies.get())
                if self.add_book_subject.get() == "":
                    subject = None  
                Book(self.add_Book_name.get(),self.add_book_writer.get(),copies,ISBN=self.add_book_isbn.get(),subject=subject)
                self.srchlb.delete(0,END)
                for b in Book.all_book:self.srchlb.insert(END,b)
            except:
                Label(self.ADD_BOOK_FRAME,text="Incomplete Informations",bg="red").grid(row=6,column=0,padx=10,pady=10,columnspan=2,sticky=E+W+S+N)
            else:
                Label(self.ADD_BOOK_FRAME,text="Book has ben Added",bg="green").grid(row=6,column=0,padx=10,pady=10,columnspan=2,sticky=E+W+S+N)
                self.UploadDatabase(user=False)
        else:
            Label(self.ADD_BOOK_FRAME,text="Incomplete Informations",bg="red").grid(row=6,column=0,padx=10,pady=10,columnspan=2,sticky=E+W+S+N)

    def check_book(self,check):
        self.check_book_toplevel = Toplevel(self)
        self.check_book_toplevel.title("Check Book")
        search_frame = Frame(self.check_book_toplevel,borderwidth=3,relief=GROOVE)
        search_frame.grid(row=0,column=0,padx=10,pady=10)
        Label(search_frame,text="Search Books By Name or Writer or ISBN:").grid(row=1,column=0,padx=10,pady=10)
        
        self.sbook_name = Entry(search_frame)
        self.sbook_name.grid(row=2,column=0,padx=10,pady=10)
        
        
        self.all_books_listbox = Listbox(search_frame)
        self.all_books_listbox.grid(row=3,column=0,padx=10,pady=10)
        self.sbook_name.bind("<Enter>",lambda event : self.s_book_event(event=event,given_listbox=self.all_books_listbox))
        self.total_books_label = Label(search_frame,text=f"Total Book Number is : {len(Book.all_book)}")
        if check:
            self.check = True
            self.all_books_listbox.bind("<Double-Button>",self.books_clicked)
            self.total_books_label.grid(row=4,column=0,padx=10,pady=10)
        for books in Book.all_book:self.all_books_listbox.insert(END,books)
        if not check:
            self.check_book_toplevel.title("Delete Book")
            self.check = False
            self.all_books_listbox.bind("<<ListboxSelect>>",self.books_clicked)
            self.d_now = Button(search_frame,text="Delete Now!",command = self.delete_book_now)
            self.d_now.grid(row=4,column=0,padx=10,pady=10)
            self.total_books_label.grid(row=5,column=0,padx=10,pady=10)
    def delete_book_now(self):
        taken_users  = self.current_book_obj.who_taken.copy()
        if len(taken_users) > 0:
            for user in taken_users:
                print(user.taken_books)
                user.remove_book(self.current_book_obj)
                print(user.taken_books)
        for idx,obj in enumerate(Book.all_book):
            if obj == self.current_book_obj:
                Book.all_book = np.delete(Book.all_book,idx)
                break
        
        # Book.all_book.remove(self.current_book_obj)
        self.all_books_listbox.delete(0,END)
        for b in Book.all_book:self.all_books_listbox.insert(END,b)
        self.total_books_label.configure(text=f"Total Book Number is : {len(Book.all_book)}")
        self.UploadDatabase(user=False)
    
    def books_clicked(self,event,user=False,setCPS=None):
        try:
            listbox_event = event.widget
            current_book_index = listbox_event.curselection()
            current_book = listbox_event.get(current_book_index)
            if not user:
                self.current_book_obj  = self.find_book(current_book)
                if setCPS:
                    self.setEntry.delete(0,END)
                    self.setEntry.insert(END,str(self.current_book_obj.n_copies))
                print(self.current_book_obj)
            if user:
                self.current_user = current_book
                print(self.current_user)
            if self.check:
                print("Current User will be listed")
                print(self.current_book_obj.who_taken)
                new_toplevel = Toplevel(self.check_book_toplevel)
                new_toplevel.title(self.current_book_obj)
                if len(self.current_book_obj.who_taken) > 0:
                    
                    self.invest = Frame(new_toplevel,borderwidth=8,relief=GROOVE)
                    self.invest.grid(row=0,column=0,padx=10,pady=10,sticky=E+W+S+N)
                    Label(self.invest,text=f"Users who Taking {self.current_book_obj} Book Info ",bg="yellow").grid(row=0,column=1,padx=10,pady=10,columnspan=len(self.current_book_obj.who_taken),sticky=E+W+S+N)

                    row,column=1,1
                    for user in self.current_book_obj.who_taken:
                        if column % 3 == 0:
                            row+=1
                            column=1
                        
                        F = Frame(self.invest,relief=GROOVE,borderwidth=3)
                        F.grid(row=row,column=column,padx=10,pady=10)
                        
                        Label(F,text=f"Name : {user}").grid(row=0,column=0,padx=10,pady=10)
                        rowx=1
                        for user_books in user.taken_books:
                            if user_books == self.current_book_obj:
                                Label(F,text=f'Book : {user_books} Taken Time: {user.taken_books[user_books]}\n End Time : {user.expiration_time(user_books)}',bg="green").grid(row=rowx,column=0,padx=10,pady=10)
                            else:
                                Label(F,text=f'Book : {user_books} Taken Time: {user.taken_books[user_books]}').grid(row=rowx,column=0,padx=10,pady=10)
                            rowx+=1
                        column+=1
                else:
                    Label(new_toplevel,text=f"Users who Taking {self.current_book_obj} Book Info ",bg="yellow").grid(row=0,column=0,padx=10,pady=10,sticky=E+W+S+N)
                    Label(new_toplevel,text="No One Take This Book",bg="green").grid(row=1,column=0,padx=10,pady=10)
            else:
                print("Just finded object.")
        except:pass
    def find_book(self,book_str):
        for book in Book.all_book:
            if book.__repr__() == book_str:
                return book
    def s_book_event(self,event,given_listbox):
        current_entry = event.widget
        current_word = current_entry.get()
        if current_word != "":
            given_listbox.delete(0,END)
            for books in Book.all_book:
                if books.name[:len(current_word)] == current_word or books.ISBN[:len(current_word)] == current_word \
                    or books.writer[:len(current_word)] == current_word:
                    given_listbox.insert(END,books)
                else:continue
        else:
            given_listbox.delete(0,END)
            for b in Book.all_book : given_listbox.insert(END,b)

        
    
def main():
    root = Tk()
    gui = GUI(root)
    root.title("Library System")
    root.mainloop()

if __name__ == "__main__":
    main()
