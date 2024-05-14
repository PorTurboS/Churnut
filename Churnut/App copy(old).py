from classes.User import User
import tkinter as Tk
import main
from classes.User import User
import json
import os
print("Current working directory:", os.getcwd())

class App(Tk.Tk):
    def __init__(self):
        super().__init__()
        print("Current working directory:", os.getcwd())
        self.title('Churnut - Cryptocurrency Budgeting Service')
        self.geometry('800x600')
        self.frames = {}
        self.grid_rowconfigure(0, weight=1) # This makes the top row expandable
        self.grid_columnconfigure(0, weight=1) # This makes the left column expandable
        pages = (LoginFrame,SignupFrame)
        
    
        for F in pages:
                page_name = F.__name__
                frame = F(parent=self, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
        

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
            frame = self.frames[page_name]
            frame.tkraise()

    


class LoginFrame(Tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.main()

    def main(self):
        middle_row = 2
        middle_column = 2
        self.label_login = Tk.Label(self,text="login:")
        self.login_entry = Tk.Entry(self)
        self.label_mdp = Tk.Label(self,text="mdp:")
        self.mdp_entry = Tk.Entry(self)
        self.label_login.grid(row=middle_row, column=middle_column - 1, sticky="e")
        self.login_entry.grid(row=middle_row, column=middle_column, sticky="ew")
        self.label_mdp.grid(row=middle_row + 1, column=middle_column - 1, sticky="e")
        self.mdp_entry.grid(row=middle_row + 1, column=middle_column, sticky="ew")
        self.submit_login = Tk.Button(self,text="Submit",command=lambda:self.check_logins())
        self.submit_signup = Tk.Button(self,text="Sign Up",command=lambda:self.controller.show_frame("SignupFrame"))
        self.submit_login.grid(row=middle_row + 2, column=middle_column - 1, sticky="e")
        self.submit_signup.grid(row=middle_row + 2, column=middle_column, sticky="ew")
        self.grid_rowconfigure(7, weight=1)

        for widget in [self.label_login, self.login_entry, self.label_mdp, self.mdp_entry, self.submit_login, self.submit_signup]:
            widget.grid_configure(padx=10, pady=5) # Add padding for aesthetics
    
    def read_db(self):
        try:
            with open('db.json','r') as db:
                return json.load(db)
        except FileNotFoundError:
            print("db.json not found, returning None.")
            return None
        except Exception as e:
            print(f"An error occurred while reading db.json: {e}")
            return None
    
    def check_logins(self):
        data = self.read_db()
        if data is None:
            label = Tk.Label(self, text="No accounts found. Please sign up.", fg='red')
            label.grid(row=4, column=0, sticky="ew")
        else:
            user_login = self.login_entry.get()
            user_mdp = self.mdp_entry.get()
            if user_login in data and data[user_login] == user_mdp:
                main.BudgetApp()
            else:
                label = Tk.Label(self, text="Incorrect login info, please check or sign up.", fg='red')
                label.grid(row=4, column=0, sticky="ew")


class SignupFrame(Tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.logins = []
        self.mdps = []
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Rows with widgets get zero weight
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=1)  # Extra row with weight after widgets
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # Columns with widgets get zero weight
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        
        self.Sign()
    

    def Sign(self):
        middle_row = 2
        middle_column = 1
        self.label_login = Tk.Label(self,text="login:")
        self.login_entry = Tk.Entry(self)
        self.label_mdp = Tk.Label(self,text="mdp:")
        self.mdp_entry = Tk.Entry(self)
        self.submit_login = Tk.Button(self,text="Submit",command=lambda:[self.on_submit()])
        self.label_login.grid(row=middle_row, column=middle_column, sticky="e", padx=10, pady=5)
        self.login_entry.grid(row=middle_row, column=middle_column + 1, sticky="ew", padx=10, pady=5)
        self.label_mdp.grid(row=middle_row + 1, column=middle_column, sticky="e", padx=10, pady=5)
        self.mdp_entry.grid(row=middle_row + 1, column=middle_column + 1, sticky="ew", padx=10, pady=5)
        self.submit_login.grid(row=middle_row + 2, column=middle_column + 1, sticky="ew", padx=10, pady=5)
        for widget in [self.label_login, self.login_entry, self.label_mdp, self.mdp_entry, self.submit_login]:
            widget.grid_configure(padx=10, pady=5)


    def on_submit(self):
        # Get the login and password from the Entry widgets
        login = self.login_entry.get()
        mdp = self.mdp_entry.get()

        # Append to lists if needed or directly handle the login and password
        self.logins.append(login)
        self.mdps.append(mdp)

        print(self.logins)  # Debugging output

        # Register data and potentially clear entries after submission
        self.register_data()

        # Possibly clear entries after successful registration
        self.login_entry.delete(0, 'end')
        self.mdp_entry.delete(0, 'end')

        # Call the controller to change frames or further actions
        self.controller.show_frame("LoginFrame")


    
    def register_data(self):
        login = self.logins[-1]
        mdp = self.mdps[-1]
        obj = User(login,mdp)
        obj.write_db()


if __name__ == "__main__":
    
    app = App()
    app.mainloop()