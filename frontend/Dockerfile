FROM node:20-alpine
WORKDIR /app
COPY frontend/package.json ./package.json
RUN npm install
COPY frontend .
ENV NEXT_PUBLIC_API_BASE=http://localhost:8000
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start"]
