FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy only the application code — never the whole context (.env, .venv, db).
COPY manage.py ./
COPY foodhub ./foodhub
COPY accounts ./accounts
COPY restaurants ./restaurants
COPY carts ./carts
COPY orders ./orders
RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser
EXPOSE 8000
CMD ["gunicorn", "foodhub.wsgi", "--bind", "0.0.0.0:8000"]
