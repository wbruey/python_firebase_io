import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import db
import argparse

class fb_database:

    def __init__(self):
        self.cred_cert = credentials.Certificate('brutest-3228a-firebase-adminsdk-bex36-272252f791.json')
        self.default_app = firebase_admin.initialize_app(self.cred_cert, {'databaseURL':'https://brutest-3228a.firebaseio.com/'})

    def set_data(self,relative_reference,data_dict={}):
        ref=db.reference(relative_reference)
        ref.set(data_dict)

    def get_data(self,relative_reference):
        ref=db.reference(relative_reference)
        return ref.get()


if __name__ == "__main__":
#    parser=argparse.ArgumentParser(description='CRUD operations on a firebase realtime database at bruey enterprises specifically')
#    parser.add_argument('ref',type=str,help='this is the reference within the mega JSON tree that will act as the root for the input data')
#    parser.add_argument('data',type=dict,help='this is the data you want to write to the firebase realtime database')    

    mydb=fb_database()
    x=mydb.get_data('/')
    print(x)

    
    
    
