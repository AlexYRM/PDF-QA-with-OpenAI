from nicegui import ui, events
import csv
import time
import datetime


ui.label("Upload File")
ui.label('(Drag and drop into the box below, or use the "+" button to select a PDF file)')


def handle_upload(event: events.UploadEventArguments):
    skipable = True
    ui.notify(f'Uploaded {event.name}')
    time.sleep(1)

    if event.type != "application/pdf":
        ui.notify(message="Invalid Document. Your upload is not a PDF file", type="negative",
                  color="red", position="top")
        ui.notify(message="Refresh the page and upload a PDF file", type="info",
                  position="top")
    else:
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
            if skipable:
                for row in csv_reader:
                    if row[0] == event.name:
                        ui.notify(message=f"File with the name '{event.name}' is already in database. Copy the file "
                                          f"name to use when asking questions", type="info")
                        skipable = False
            # Do not write the file name again in the log file
            if skipable:
                csv.writer(csv_file).writerow([event.name, datetime.datetime.now()])
        with event.content as f:
            with open(f"{event.name}", "wb") as file:
                for line in f.readlines():
                    file.write(line)
