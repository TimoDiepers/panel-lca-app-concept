FROM python:3.11

WORKDIR /code

# set home + cache dirs to writable locations
ENV HOME=/code
ENV XDG_CACHE_HOME=/code/.cache
ENV XDG_DATA_HOME=/code/.local/share
ENV BRIGHTWAY2_DIR=/tmp/

RUN mkdir -p "$BRIGHTWAY2_DIR" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" && chmod -R 777 /code

# Copy source code first
COPY . .

# Install requirements and the package itself
COPY ./requirements.txt /code/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -e .

CMD ["panel", "serve", "/code/app/app.py", "--address", "0.0.0.0", "--port", "7860", "--allow-websocket-origin", "*"]