FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY session_manager.py .
COPY automation_script.py .
COPY fieldnation_script.py .
COPY templates ./templates

CMD ["python", "session_manager.py"]