from io import DEFAULT_BUFFER_SIZE
from types import prepare_class
import zipfile
from flask import Flask, render_template, redirect, request,url_for
import random
from flask.helpers import send_file
from zipfile import ZipFile
import os
try: #these are for running on the local machine heroku does not require dotenv lib 
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

#database format -> user_name TEXT, otp INTEGER, file_name TEXT, file BYTEA

import psycopg2
app = Flask(__name__)

#cridentials = ""
cridentials = os.getenv("CRIDENTIALS") #CRIDENTIALS for pestgres database at heroku
fortyMb_inbytes = 41943040 #file size limit 

table = 'test'
def connect_to_db():
    conn = psycopg2.connect(cridentials)
    cur = conn.cursor()
    return cur,conn

def close_and_commit_connection(conn):
    conn.commit()
    conn.close()

def get_all_otp():
    cur,conn = connect_to_db()
    cur.execute(f"SELECT otp FROM {table}")
    otp_list = cur.fetchall()
    close_and_commit_connection(conn)
    return [o[0] for o in otp_list]

def get_all_user_name():
    cur,conn = connect_to_db()
    cur.execute(f"SELECT user_name FROM {table}")
    user_name_list = cur.fetchall()
    close_and_commit_connection(conn)
    return [o[0] for o in user_name_list]

def user_name_already_exists(user_name):
    user_list = get_all_user_name()
    if user_name in user_list:
        return True
    else:
        return False

        
def generate_otp():
    otp_list = get_all_otp()
    otp = random.randint(1112,9999) #in random library upper-limit is included
    while otp in otp_list:
        otp = random.randint(1112,9999)
    return otp



def get_size_of_db():
    cur,conn = connect_to_db()
    cur.execute("SELECT pg_size_pretty( pg_database_size('dd397n8dctvgb2') );")
    size = cur.fetchone()
    close_and_commit_connection(conn)
    res = [i for i in size[0].split()]
    #print(res) 
    if(res[1] == 'kB'):
        return 1
    return int(res[0])


def to_binary(binary):
    binary = psycopg2.Binary(binary)
    return binary

def write_to_file(binary_code, file_name):
    #converts the data from database back to a file object and returns it
    my_file = open(file_name, 'wb')
    my_file.write(binary_code)
    #print(f'Created file with name: {file_name}')
    return file_name



def enter_file_to_db(user_name,otp,file_name, data):
    cur,conn = connect_to_db()
    cur.execute(f"INSERT INTO {table} VALUES('{user_name}',{otp},'{file_name}',{data})")
    close_and_commit_connection(conn)
    #print("entered file")

def get_all_from_db(user_name, otp):
    cur, conn = connect_to_db()
    cur.execute(f"SELECT * FROM {table} WHERE user_name = '{user_name}' AND otp = {otp}")
    name_and_file = cur.fetchall()
    cur.execute(f"DELETE FROM {table} WHERE user_name = '{user_name}' AND otp = {otp}")
    close_and_commit_connection(conn)
    return name_and_file
    

def check_all_from_db(user_name, otp):
    cur, conn = connect_to_db()
    cur.execute(f"SELECT user_name ,otp , file_name FROM {table} WHERE user_name = '{user_name}' AND otp = {otp}")
    details = cur.fetchall()
    close_and_commit_connection(conn)
    return details



def delete_file(file):
    os.remove(file)
    #print("deleted file :",file)

def make_into_zip(list_of_files,user_name):
    files = []
    zf =  ZipFile(f'{user_name}.zip','w') 
    for each in list_of_files:
        files.append(write_to_file(each[3],each[2]))
        zf.write(each[2])
        delete_file(each[2])  #takes file names
    zf.close()
   
    #print("these are files names in the zip:",files)
    
    return f'{user_name}.zip'

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/share/", methods = ["POST","GET"])
def share():
    if db_size>950:
        return str(db_size)+"MB : databse size limit has exceeded <br>this is a rare case please contact the ownerof the webapp"
    return render_template("share.html") 

@app.route("/success/", methods = ['POST'])
def success():
    otp = 0 # this is just to avoid irritating warnings
    user_name = ""
    if request.method == "POST":
        #print(request.files["files"].filename)  # getting the name of the file
        #print(request.files.getlist("files"))   # a list of files
        user_name = request.form["user_name"]

        if user_name_already_exists(user_name):
            return render_template("share.html", error = "User name already exists pls try another one")

        
        otp = generate_otp()
        totalfilesize = 0
        for f in request.files.getlist("files"):
            file_name = f.filename
            file_data = f.read()
            totalfilesize += len(file_data)
            enter_file_to_db(user_name,otp,file_name,to_binary(file_data))
            #print(f"{file_name} written to database along with its name {f.filename.split('.')[0]}")
 
        if totalfilesize >= fortyMb_inbytes:
            return render_template("share.html", error = "Your files exceed the memory limit")

    return render_template("success.html",details = (otp,user_name))




@app.route("/get/",methods = ['GET','POST'])
def get(error = ''):
    if request.method == 'GET':
        #print(error)
        if error == '':
            return render_template("get.html",error = str(request.args.get('error')),form = True)
        else:
            return render_template("get.html",error = request.args.get('error'),form = True)
    else:
        user_name = request.form["user_name"]
        otp = request.form["otp"]
        #print(otp,user_name)
        list_of_entries = check_all_from_db(user_name,otp)  
        if len(list_of_entries) > 0: 
            for e in list_of_entries:
                pass
                #print(f"Present in database : {e}")
                #write_to_file(e[1],e[0].split('.')[0]+'routed.'+e[0].split('.')[1])
        else:
            return redirect(url_for('get', error = "File not found. Please enter a valid username and otp."))
        return render_template("get.html",download = "yes", user_name = user_name, otp = otp, form = False)
    


@app.route("/download/", methods = ['GET'])
def download():
    user_name = request.args.get('user_name')
    otp = request.args.get('otp')
    
    list_of_files = get_all_from_db(user_name,otp)  #this function also deletes the entry from teh database
    #print('number of files',len(list_of_files))
    if len(list_of_files) == 1:
        #print("single file printed")
        write_to_file(list_of_files[0][3],"temp_files/"+list_of_files[0][2])
        return send_file("temp_files/"+list_of_files[0][2],attachment_filename=list_of_files[0][2],as_attachment=True)
    else:
        #for multiple files
        zip_name = make_into_zip(list_of_files,user_name)
    #print(f"{zip_name} is now a zip file in your folder")
    return send_file(zip_name,attachment_filename = zip_name, as_attachment=True)

@app.route('/howitworks/')
def howitworks():
    return render_template("howitworks.html")


def delete_all_zip():
    list_of_files = os.listdir()
    for f in list_of_files:
        if os.path.splitext(f)[1]==".zip":
            os.remove(f)
            #print("clutter cleared :" ,f)

if __name__ == "__main__":
    global db_size
    db_size = get_size_of_db() 
    #this cycle happens when the app starts a new dyno
    delete_all_zip()    #for clearing up the clutter
    #delete the files in the folder 'temp_files' 
    list_of_files = os.listdir('temp_files')
    for f in list_of_files:
            os.remove("temp_files/"+f)
            #print("clutter cleared from temp_files:" ,f)
    app.run(debug = False)
    
