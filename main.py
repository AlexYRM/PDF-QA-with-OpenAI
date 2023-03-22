import csv
import shutil
import pathlib
import AI
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException


app = FastAPI()



# post request to upload a file
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(description="Load a PDF file(should be in English)! Press TRY IT OUT")):
    # make sure to receive PDF file, give error in case we don't
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=404, detail="Invalid Document. Upload a PDF file")
    # create a copy of the temp file to "Uploaded Files"
    with open(f"Uploaded Files\{file.filename}", "wb") as stored_file:
        shutil.copyfileobj(file.file, stored_file)
        stored_file_path = str(pathlib.Path().absolute()) + f"\\Uploaded Files\\{file.filename}"
    # create a log file to detect if the uploaded file is already stored
    with open('file_info.csv', mode='a+', newline='') as csv_file:
        # Check if the file is empty
        csv_file.seek(0)
        is_file_empty = csv_file.read(1) == ''
        # Move the file pointer back to the beginning
        csv_file.seek(0)
        # Create a CSV reader object and skip header
        csv_reader = csv.reader(csv_file)
        if not is_file_empty:
            next(csv_reader)
        # Check if the first column of any row matches your variable, if not, write the data
        for row in csv_reader:
            if row[0] == file.filename:
                return {f"File with the name '{file.filename}' is already in database. Copy the file name to "
                        f"use when asking questions": file.filename}
        csv.writer(csv_file).writerow([file.filename, stored_file_path, datetime.now()])
        return {"File was uploaded. Copy the file name to use when asking questions": file.filename}


# get request to ask question in which we must give input the filename from which we will ask
@app.get("/ask_question/")
async def ask_question(Question: str, FileName: str):

    response = f"Q: {Question}  " \
               f"A: {AI.answer_questions(Question, FileName)}"
    return {response: Question}
