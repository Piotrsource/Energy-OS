# =============================================================================
# Dockerfile — Multi-Stage Build for the React Frontend
# =============================================================================
# Stage 1 (build): Install dependencies and build the production bundle.
# Stage 2 (serve): Serve the static files with nginx.
# =============================================================================

# ---------------------------------------------------------------------------
# STAGE 1: BUILD
# ---------------------------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
# STAGE 2: SERVE
# ---------------------------------------------------------------------------
FROM nginx:alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
