FROM python:3.9-slim
WORKDIR /plane_over_me_bot
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]