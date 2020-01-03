FROM python:3

COPY . .

RUN pip install --no-cache-dir -r debug_requirements.txt

CMD ["python", "src/debug.py"]