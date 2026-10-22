FROM python:3.12-slim
RUN useradd --create-home forma && mkdir /data && chown forma:forma /data
WORKDIR /app
COPY --chown=forma:forma server.py ./
COPY --chown=forma:forma public ./public
USER forma
ENV FORMA_HOST=0.0.0.0 FORMA_DATA=/data FORMA_ENV=production PORT=8765 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8765
VOLUME ["/data"]
CMD ["python3", "server.py"]
