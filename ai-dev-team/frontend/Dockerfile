## ── Stage 1: Build React app ──────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --silent
COPY . .
RUN npm run build

## ── Stage 2: Serve with Nginx ─────────────────────────────────────────────
FROM nginx:1.27-alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx template — nginx will run envsubst on startup
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080
# nginx official image handles envsubst and starts automatically
