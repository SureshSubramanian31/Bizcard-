# importing the Library 

from types import resolve_bases
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
from typing_extensions import Concatenate
import io
import sqlite3


def Business_Card(path):
  Buss_Card_1 = Image.open(path)

# Converting the Image to Array Format:
  Buss_Array = np.array(Buss_Card_1)

  extract = easyocr.Reader(['en'])
  Extracted = extract.readtext(Buss_Array, detail = 0)

  return Extracted, Buss_Card_1


def Business_Card_D(details):
    Emp_Lis = {
        "Name": [],
        "Role": [],
        "Company_Name": [],
        "Contact": [],
        "E-mail": [],
        "Website": [],
        "Location": [],
        "Pincode": []
    }

    Emp_Lis["Name"].append(details[0])
    Emp_Lis["Role"].append(details[1])

    for i in range(2, len(details)):
        detail = details[i]

        if detail.startswith("+") or (detail.replace("-", "").isdigit() and "-" in detail):
            Emp_Lis["Contact"].append(detail)

        elif "@" in detail and ".com" in detail:
            Emp_Lis["E-mail"].append(detail)

        elif any(sub in detail.lower() for sub in ["www", "http"]):
            Emp_Lis["Website"].append(detail.lower())

        elif any(state in detail for state in ["Tamil Nadu", "TamilNadu"]) or detail.isdigit():
            Emp_Lis["Pincode"].append(detail)

        elif re.match(r'^[A-Za-z]', detail) and not any(ext in detail.lower() for ext in [".com", "@", "www", "http"]):
            Emp_Lis["Company_Name"].append(detail)

        else:
            Loc = re.sub(r'[,;]', '', detail)
            Emp_Lis["Location"].append(Loc)

    for key,value in Emp_Lis.items():
      if len(value)>0:
        Concatenate = "".join(value)
        Emp_Lis[key] = [Concatenate]

      else:
          value = "N/A"
          Emp_Lis[key] = [value]

    return Emp_Lis

# Streamlit Part

st.set_page_config(layout = "wide")

select = st.selectbox("Main Menu", ["Home", "Upload & Modify", "Delete"])

# Creating the Home Button
if select =="Home":
  st.markdown("Python, Easy OCR, Streamlit, SQL, Pandas are used.")

  st.write(" A Python application called Bizcard is made to extract data from business cards.")

  st.write("Bizcard's primary goal is to automate the process of obtaining vital information from business card images, including the name, position, organization, contact information, and other pertinent facts. Through the utilization of Easy OCR's Optical Character Recognition (OCR) capabilities, Bizcardis is capable of extracting text from the photos.")

elif select == "Upload & Modify":
  UP_MO = st.file_uploader("Upload The Image", type = ["png","jpg","jpeg"])

  if UP_MO is not None:
    st.image(UP_MO,  width = 300)

    Extracted_Text, Buss_Card_Image = Business_Card(UP_MO)

    Text = Business_Card_D (Extracted_Text)

    if Text:
      st.success ("Text has been extracted from the uploaded image!")

    df = pd.DataFrame(Text)

# Converting the images into Bytes:
    I_into_B = io.BytesIO()
    Buss_Card_Image.save(I_into_B, format = "PNG")

    Image_Data = I_into_B.getvalue()

    data = {"Image":[Image_Data]}

    df_1 = pd.DataFrame(data)

    concat_df = pd.concat([df,df_1],axis = 1)

    st.dataframe(concat_df)

    button_1 = st.button("Save The Extracted Data", use_container_width = True)

    if button_1:
# Creating the  SQLite DataBase
      mydb = sqlite3.connect("BizCard.db")
      cursor = mydb.cursor()
# Creating a Table
      Query01 = """CREATE TABLE IF NOT EXISTS Bizcard( Name varchar(255),
                                                    Role varchar(255),
                                                    Company_Name varchar(255),
                                                    Contact int,
                                                    Email varchar(255),
                                                    Website text,
                                                    Location text,
                                                    Pincode Varchar(255),
                                                    Image text)"""

      cursor.execute(Query01)
      mydb.commit()

# Inserting the values intio the table
      Insert_Query = """INSERT INTO Bizcard(Name, Role, Company_Name, Contact, Email, Website, Location, Pincode, Image)
                  Values(?, ?, ?, ?, ?, ?, ?, ?, ?)"""


      Datas = concat_df.values.tolist()[0]
      cursor.execute(Insert_Query, Datas)
      mydb.commit()

      st.success("The Data has been Saved Successfully")

  method = st.selectbox("Select The Method",["None","Preview", "Modify"])

  if method == "None":
    st.write("Please Click the Below Options")

# Creating the Preview Button 
  if method == "Preview":

    mydb = sqlite3.connect("BizCard.db")
    cursor = mydb.cursor()

    select_query = "SELECT * FROM Bizcard"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("Name", "Role", "Company_Name", "Contact", "Email", "Website", "Location", "Pincode", "Image"))
    st.dataframe(table_df)

# # Creating the Modify Button
  elif method == "Modify":

    mydb = sqlite3.connect("BizCard.db")
    cursor = mydb.cursor()

    select_query = "SELECT * FROM Bizcard"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("Name", "Role", "Company_Name", "Contact", "Email", "Website", "Location", "Pincode", "Image"))
    st.dataframe(table_df)

    col1, col2 = st.columns(2)
    with col1:
      Selected_Name = st.selectbox("Select The Name", table_df["Name"])

    df_3 = table_df[table_df["Name"] == Selected_Name]

    df_4 = df_3.copy()

    col1, col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("NAME", df_3["Name"].unique()[0])
      mo_Role = st.text_input("ROLE", df_3["Role"].unique()[0])
      mo_com_name = st.text_input("COMPANYNAME", df_3["Company_Name"].unique()[0])
      mo_contact = st.text_input("CONTACT", df_3["Contact"].unique()[0])
      mo_email = st.text_input("EMAIL", df_3["Email"].unique()[0])

      df_4["Name"] = mo_name
      df_4["Role"] = mo_Role
      df_4["Company_Name"] = mo_com_name
      df_4["Contact"] = mo_contact
      df_4["Email"] = mo_email

    with col2:
      mo_website = st.text_input("WEBSITE", df_3["Website"].unique()[0])
      mo_location = st.text_input("LOCATION", df_3["Location"].unique()[0])
      mo_pincode = st.text_input("PINCODE", df_3["Pincode"].unique()[0])
      mo_image = st.text_input("IMAGE", df_3["Image"].unique()[0])

      df_4["Website"] = mo_website
      df_4["Location"] = mo_location
      df_4["Pincode"] = mo_pincode
      df_4["Image"] = mo_image

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:
      button_3 = st.button("Modify", use_container_width = True)

      if button_3:

        mydb = sqlite3.connect("BizCard.db")
        cursor = mydb.cursor()

        cursor.execute(f" DELETE FROM Bizcard WHERE Name = '{Selected_Name}'")
        mydb.commit()

        Insert_Query = """INSERT INTO Bizcard(Name, Role, Company_Name, Contact, Email, Website, Location, Pincode, Image)
                        Values(?, ?, ?, ?, ?, ?, ?, ?, ?)"""


        Datas = df_4.values.tolist()[0]
        cursor.execute(Insert_Query, Datas)
        mydb.commit()

        st.success("The Data has been Modified and Saved Successfully")

# Creating the Delete Button
elif select == "Delete":
  
  mydb = sqlite3.connect("BizCard.db")
  cursor = mydb.cursor()

  col1, col2 = st.columns(2)
  with col1:

    select_query = "SELECT Name FROM Bizcard"

    cursor.execute(select_query)
    table1 = cursor.fetchall()
    mydb.commit()

    names = []

    for i in table1:
      names.append(i[0])

    name_select = st.selectbox("Select the name", names)

  with col2:

    select_query = f"SELECT Role FROM Bizcard WHERE Name ='{name_select}'"

    cursor.execute(select_query)
    table2 = cursor.fetchall()
    mydb.commit()

    roles = []

    for j in table2:
      roles.append(j[0])

    role_select = st.selectbox("Select the role", roles)

  if name_select and role_select:
    col1, col2, col3 = st.columns(3)

    with col1:
      st.write(f"Selected Name: {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Selected Role: {role_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("Delete", use_container_width = True)

      if remove:

        cursor.execute(f"DELETE FROM Bizcard WHERE Name = '{name_select}' AND Role = '{role_select}'")

        mydb.commit()

        st.warning("The Data has been Deleted")


