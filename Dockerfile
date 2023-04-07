FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY  *.py .

RUN mkdir "Embedded_Files"
RUN mkdir "Uploaded_Files"

CMD ["python", "./GUI.py"]