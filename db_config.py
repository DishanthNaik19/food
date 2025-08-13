# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 12:59:03 2025

@author: Dishanth
"""

import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # your MySQL username
        password="qwerty123456@#$", # your MySQL password
        database="food_wastage"
    )
