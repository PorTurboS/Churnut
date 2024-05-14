import json


class User:
    def __init__(self,login,mdp):
        self.login = login
        self.mdp = mdp

    def write_db(self):
        try:
            
            with open('db.json', 'r') as db:
               
                u_dict = json.load(db)  # Load existing data

        except FileNotFoundError:
            
            print("Creating new db.json file.")
            u_dict = {}  # If no file, start a new dict
        
        if self.login not in u_dict or isinstance(u_dict[self.login],str):
            u_dict[self.login] = {'password': self.mdp}
        else:
            # Ensure not to overwrite other data like crypto
            u_dict[self.login]['password'] = self.mdp
        
        with open('db.json','w') as db:
            json.dump(u_dict,db,indent=6)
            print("Data written to db.json")
