FROM python:3.13-alpine AS builder
RUN apk add --no-cache python3-dev libffi-dev
COPY . /app
WORKDIR /app
RUN python -m venv /venv && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# TODO: Fix dependencies copy
# FROM python:3.13-alpine
# COPY --from=builder /venv /venv
# ENV PATH=/venv/bin:$PATH
# RUN . /venv/bin/activate
# WORKDIR /app
# COPY . .
CMD ["python", "bot.py"]