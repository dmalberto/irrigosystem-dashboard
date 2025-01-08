FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos da aplicação para o diretório de trabalho
COPY . .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar variáveis de ambiente
ENV COOKIE_SECRET_PASSWORD=53r9HgjDRNMCi6OnuZxjp3v9
ENV API_URL=http://54.86.43.17

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
