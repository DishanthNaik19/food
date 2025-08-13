# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 12:59:03 2025

@author: Dishanth
"""

import sqlite3

def get_connection():
    # Connect to SQLite database file in the same folder as app.py
    return sqlite3.connect("food.db")

