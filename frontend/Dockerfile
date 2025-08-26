# Frontend Dockerfile (no package-lock required)
FROM node:20-alpine...1234

WORKDIR /app

# Install deps without relying on a lockfile
COPY package.json ./
RUN npm install

# Copy source
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
