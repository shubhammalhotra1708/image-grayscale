from hashlib import new
from pickle import FALSE
from app import app
import cv2 as cv
import numpy as np
from PIL import Image as im
#for emailing images
import smtplib
import imghdr
from email.message import EmailMessage
# from numpy import ndarray

import os
from flask import render_template, request, redirect, jsonify, make_response, send_from_directory, abort
from werkzeug.utils import secure_filename

# @app.route("/about")
# def about():
#     return "All about Flask"

# basedir = os.path.abspath(os.path.dirname(__file__))

# app.config["CLIENT_IMAGES"] = "C:/Users/shubh/Desktop/Projects/image-grayscale/app/static/client/img"
app.config["CLIENT_IMAGES"] ="/c/Users/shubh/Desktop/Projects/image-grayscale/app/static/client/img"
app.config["CLIENT_CSV"] = "C:/Users/shubh/Desktop/Projects/image-grayscale/app/static/client/csv"
app.config["CLIENT_PDF"] = "C:/Users/shubh/Desktop/Projects/image-grayscale/app/static/client/pdf"

app.config['IMAGE_UPLOADS'] = "C:/Users/shubh/Desktop/Projects/image-grayscale/app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]

def allowed_image(filename):
#checks extensions:
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/",methods=["GET","POST"])
def index():
    
    if request.method == "POST":

        if request.files and request.form["size"]:
            size = int(request.form["size"])
           
            image = request.files["image"]

            if image.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_image(image.filename):
                #secures the filename(removes spaces,full paths etc)
                filename = secure_filename(image.filename)
                # print(filename)
                pth = os.path.join(app.config["IMAGE_UPLOADS"], filename)
                image.save(pth)
                print(pth)

                # converting it to grayscale
                num_image = cv.imread(os.path.join(app.config["IMAGE_UPLOADS"], filename),cv.IMREAD_UNCHANGED)
                image_copy = np.copy(num_image)
                gray = cv.cvtColor(image_copy, cv.COLOR_RGB2GRAY)

                # resizing images

                width = int(gray.shape[1] * size/100)
                height = int(gray.shape[0] * size/100)
                dimension = (width, height)
                
                resized_image = cv.resize(gray,dimension,interpolation = cv.INTER_AREA)

                gray_im = im.fromarray(resized_image)

                gray_im.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                print("Image processed and saved")
                nexturl=f"{request.url}get-image/{filename}"
                print("download link",nexturl)

                #sending this image on email
                recemail=request.form["email"]
                if recemail!="" :
                    Sender_Email = "shubhammalhotracr7@gmail.com"
                    Reciever_Email = recemail
                    Password="fsmvbeajzdjermax"

                    newMessage = EmailMessage()    #creating an object of EmailMessage class
                    newMessage['Subject'] = "Image converted to black and white." 
                    newMessage['From'] = Sender_Email  #Defining sender email
                    newMessage['To'] = Reciever_Email  #Defining reciever email
                    new_line='\n'
                    msg=f"Hi, here is your Black & White image resized accordingly.{new_line}"
                    newMessage.set_content(msg) 
                    
                    pathemail=os.path.join(app.config["IMAGE_UPLOADS"], filename)
                    with open(pathemail, 'rb') as f:
                        image_data = f.read()
                        image_type = imghdr.what(f.name)
                        image_name = f.name
                    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(Sender_Email, Password) #Login to SMTP server
                        smtp.send_message(newMessage)
                    
                    return redirect(request.url) #for refreshing the home page
                    
                return  redirect(nexturl) #for auto download on browser

            else:
                print("That file extension is not allowed")
                return redirect(request.url)
        
    return render_template("index.html")

#sending/downloading files
@app.route("/get-image/<image_name>")
def get_image(image_name):

    try:
        return send_from_directory(app.config["IMAGE_UPLOADS"], path=image_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)
