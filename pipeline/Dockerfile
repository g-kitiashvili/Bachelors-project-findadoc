# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

WORKDIR /app

COPY pyproject.toml ./
COPY pipeline ./pipeline
RUN pip install --no-cache-dir -e .

# Headed Chromium (needed for Aversi's Cloudflare bypass) requires an X server.
# Xvfb is preinstalled but not running; the entrypoint starts it as a background
# daemon so both the scheduler CMD and ad-hoc `docker compose exec` invocations
# share the same virtual display via $DISPLAY.
ENV DISPLAY=:99
RUN printf '#!/bin/sh\nXvfb :99 -screen 0 1280x1024x24 >/dev/null 2>&1 &\nexec "$@"\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "pipeline", "scheduler"]
