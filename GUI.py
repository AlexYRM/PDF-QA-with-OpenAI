import AI
import csv
import time
import os.path
import datetime
from nicegui import ui, events

question = ""
select = ""
file_storage = []
skippable = True
updated = False


# function to append any new file to file_info.csv(contains names and added date of all the files in memory)
# and duplicate the names in file_info.csv to file_storage
def update_source_file(name):
    global file_storage, updated, skippable
    with open('file_info.csv', mode='a+', newline='') as csv_file:
        csv_file.seek(0)
        # check if uploaded file is already stored
        for row in csv.reader(csv_file):
            if row[0] == name:
                ui.notify(message=f"File with the name '{name}' is already in database. Copy the file "
                                  f"name to use when asking questions", type="info")
                file_storage.append(row[0])
                skippable = False
        # if not in file_info.csv write it to file and append it to file_storage
        if skippable:
            csv.writer(csv_file).writerow([name, datetime.datetime.now()])
            file_storage.append(name)
    updated = True  # need to check if new file was added or not


# function that handles the uploaded file
def handle_upload(event: events.UploadEventArguments):
    ui.notify(f'Uploaded {event.name}')
    time.sleep(2)
    # check if the uploaded file is a PDF format, if not, return warning message and instructions
    if event.type != "application/pdf":
        ui.notify(message="Invalid Document. Your upload is not a PDF file", type="negative",
                  color="red", position="top")
        ui.notify(message="Refresh the page and upload a PDF file", type="info",
                  position="top")
    else:
        update_source_file(event.name)
        # if file is not found in file_info.csv write it to memory
        if skippable:
            with event.content as f:
                path = os.path.join("Uploaded_Files", event.name)
                with open(path, "wb") as file:
                    for line in f.readlines():
                        file.write(line)


# store user input question
def update_question(e):
    global question
    question = e.value


# choices for user to select one source from the files in memory
def source_files():
    if not updated:
        with open('file_info.csv', mode='a+', newline='') as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row[0] not in file_storage:
                    file_storage.append(row[0])
    return file_storage


# store user input file selection
def update_selection(e):
    global select
    select = e.value


# use AI to give answer to user input question
def AI_answer():
    if select == "":
        response = "You did not select the source from the dropdown column \n" + "-"*60
    else:
        response = f"Q: {question}  \n" \
                   f"A: {AI.answer_questions(question, select)}\n" + "-"*60
    log.push(response)


# greetings and brief instructions
with ui.column().classes("items-center w-full mb-5 my-2"):
    ui.label("Upload File").classes("text-lg font-medium tracking-wide text-fuchsia-700")
    ui.label("Use the '+' button to select a PDF file").classes("text-lg font-medium tracking-wide text-purple-600")
    ui.label("If you want to upload another file, please delete the question so the file list may update")\
        .classes("text-lg font-medium tracking-wide text-purple-600")


with ui.row().classes('w-full justify-around'):
    ui.upload(on_upload=handle_upload, auto_upload=True).classes("h-40")
    with ui.row().classes("justify-around"):
        text_input = ui.input(label='Ask your question', placeholder='Write here', on_change=update_question).\
            classes("text-lg w-80")
        with ui.column():
            ui.label("Select source document").bind_visibility_from(text_input, "value").\
                classes("text-purple-600 text-lg underline decoration-dotted "
                        "decoration-purple-600 underline-offset-2 mb-14")
            select_source = ui.select(options=source_files(), with_input=True, on_change=update_selection).\
                bind_visibility_from(text_input, "value").classes("w-80 text-base")

    log = ui.log(max_lines=10).classes('w-10/12 mt-20 h-40 text-sm text-center leading-tight'
                                       ' container mx-auto p-4 whitespace-pre-wrap')
    button = ui.button('Find the AI\'s answer', on_click=AI_answer).bind_visibility_from(text_input, "value").\
        classes("w-1/6 mt-2")

ui.run(title="Submit File", dark=True, host="0.0.0.0", port=60)