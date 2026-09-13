# Stage 1: build the Vite/React static bundle.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# Same-origin API/media in production - nginx below proxies /api and /media
# to the backend container, so the frontend calls relative paths.
ENV VITE_API_BASE_URL=""
RUN npm run build

# Stage 2: serve the built static files + reverse-proxy to the backend.
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
