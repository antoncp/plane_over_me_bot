FROM python:3.12-slim
WORKDIR /plane_over_me_bot
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]