FROM python:3.13
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    && apt-get clean
RUN pip install selenium pytest
# Set display environment variable for headless mode
ENV DISPLAY=:99

# Run Xvfb in the background and then run pytest
CMD ["sh", "-c", "Xvfb :99 & pytest Tests/test_useInsider.py"]