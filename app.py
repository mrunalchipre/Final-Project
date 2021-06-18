import streamlit as st
import cv2
from predict import predict
import os
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# DB Management
import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Security
# passlib,hashlib,bcrypt,scrypt
import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def main():
    st.title("_Histopathologic Cancer Detection_")

    menu = ["🏠 Home", "↪ Login", "⬆ SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)
    image = Image.open('logo.png')
    st.sidebar.image(image, caption='', use_column_width=True)
    if choice == "🏠 Home":
        st.subheader("AI based Digital Pathology for Lung Cancer")
        image = Image.open('brain.jpg')
        st.image(image, caption='AI changing the world', use_column_width=False)
        st.markdown(">Designed and developed by **Batch-04**")

    elif choice == "↪ Login":
        # st.subheader("Please Login to take test")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password")
        if st.sidebar.checkbox("Login"):

            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))

            if result:
                st.success("Logged In as {}".format(username))
                # User Interface
                st.title("Cancer Detector AI")
                st.markdown(">AI powered Web app that can detect Cancer in Histopathologic Scan Images.")
                st.write("")
                uploaded_file = st.file_uploader("Choose an image...", type=("jpg", "png", "jpeg", "tif"))
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    image.save('./test/uploaded/temp.png')
                    image = cv2.imread('./test/uploaded/temp.png')
                    st.image(uploaded_file, caption='Uploaded Image.', width=360)
                    st.markdown("Hurray, AI is making prediction!")
                    st.write("")
                    st.markdown("**AI**: Content of Cancerous cells is...")
                    chance = predict(image)
                    st.success(f"{chance}%")
                    #st.balloons()
                    #st.markdown('Prediction Graph')
                    #chance = pd.DataFrame(
                        #np.random.randn(10, 1),
                        #columns=['a'])
                    #st.line_chart(chance)
                    st.markdown('Reference Table')
                    st.write(pd.DataFrame({
                        'Percentage': ["Less than 30%", "30-70%", "More than 70%"],
                        'Respective Stage': ["Stage-I", "Stage-II", "Stage-III"]
                    }))

                    st.subheader("Prediction-Plot")
                    out_of = 100-chance
                    if chance < 1:
                        st.success("Graph cannot be plotted for too low chances...!")
                    else:
                        labels = 'Cancerous', 'Non-Cancerous'
                        values = [chance, out_of]
                   # explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

                        fig1, ax1 = plt.subplots()
                        ax1.pie(values, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                        st.pyplot()

                    # Delete Image as soon as we make prediction
                    os.remove('./test/uploaded/temp.png')
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "⬆ SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password")

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")


if __name__ == '__main__':
    main()
