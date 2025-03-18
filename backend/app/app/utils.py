import datetime
from sqlalchemy.orm import Session
import random
from app.core.config import settings
from datetime import datetime, timedelta, date, time
import string
from app.core.config import settings
from app.models import *
from sqlalchemy import or_, and_
import sys
import math
import os
import shutil
import smtplib
from email_validator import validate_email, EmailNotValidError  # type: ignore
import tracemalloc

tracemalloc.start()



"""This file storage fuction is used to 
   store the file,image,videos in represented path
   
   base_dir-> the path that the files want to store
   dt -> used  to make the file name unique
   txt1 -> extention of thr file
   save_full_path -> to pass the path to frontend
   file_exe -> this is for backend purpose to store in database 
"""

def file_storage(file_name, f_name):

    base_dir = settings.BASE_UPLOAD_FOLDER+"/innov_ycc"

    dt = str(int(datetime.now().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(
            dir=base_dir, err=e))

    output_dir = base_dir + "/"

    filename = file_name.filename
    
    # Split file name and extension
    txt = filename[::-1]
    splitted = txt.split(".", 1)
    txt1 = splitted[0][::-1]
   
    files_name = f_name.split(".")

    save_full_path = f'{output_dir}{files_name[0]}{dt}.{txt1}'

    file_exe = f"innov_ycc/{f_name}{dt}.{txt1}"
    with open(save_full_path, "wb") as buffer:
        shutil.copyfileobj(file_name.file, buffer)

    return save_full_path, file_exe

"""The paginate function is used to generate a structured
   response for paginated data. Pagination is a common technique
   in software development where large datasets are divided into smaller,
   more manageable chunks, or "pages," to be displayed or processed sequentially.
   """
def get_pagination(row_count=0, current_page_no=1, default_page_size=10):
    current_page_no = current_page_no if current_page_no >= 1 else 1
    total_pages = math.ceil(row_count / default_page_size)

    if current_page_no > total_pages:
        current_page_no = total_pages

    limit = current_page_no * default_page_size
    offset = limit - default_page_size

    if limit > row_count:
        limit = offset + (row_count % default_page_size)

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [total_pages, offset, limit]

""" This paginate function is used to give
    the final result of the listed data 
    that are already paginated
    
    total_page -> total page to show all the data
    total_count -> total datas in that list ( non paginated)"""

def paginate(page, size, data, total_page,total_count:int=None):
    reply = {"items": data, "total_page": total_page, "page": page, "size": size}
    
    if total_count:
        reply["total_count"] = total_count
        
    return reply

""" This Check Email function is used 
    to the supplied Email id was valid or not """
def checkEmail(email):
    try:
        v = validate_email(email)
        email = v["email"]
        return True
    except EmailNotValidError as e:
        return False