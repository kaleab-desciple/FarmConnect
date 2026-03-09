# ===================================================================
# FarmConnect Frontend Dockerfile
# Multi-stage build for Development and Production
# ===================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install node_modules
# -----------------------------------------------------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (use --prefer-offline for faster local caching)
RUN npm ci --prefer-offline || npm install

# -----------------------------------------------------------------------------
# Stage 2: Development - Run dev server with hot reload
# -----------------------------------------------------------------------------
FROM node:20-alpine AS development

WORKDIR /app

# Copy dependency files from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source files
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Environment variables for development
ENV NODE_ENV=development

# Start Vite dev server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# -----------------------------------------------------------------------------
# Stage 3: Production Build - Build optimized assets
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source files
COPY . .

# Set production environment
ENV NODE_ENV=production

# Build the application
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 4: Production - Serve with Nginx
# -----------------------------------------------------------------------------
FROM nginx:alpine AS production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

# ===================================================================
# USAGE INSTRUCTIONS
# ===================================================================
#
# Development (hot reload):
#   docker build --target development -t farmconnect:dev .
#   docker run -p 5173:5173 -v $(pwd):/app farmconnect:dev
#
# Production build:
#   docker build --target builder -t farmconnect:builder .
#   docker run -p 80:80 farmconnect:builder
#
# Full production image:
#   docker build -t farmconnect:prod .
#   docker run -p 80:80 farmconnect:prod
#
# Docker Compose integration (add to docker-compose.yml):
#
#   frontend:
#     build:
#       context: ./frontend
#       target: development  # Change to 'production' for prod
#     ports:
#       - "5173:5173"      # 80:80 for production
#     volumes:
#       - ./frontend:/app
#       - /app/node_modules
#     environment:
#       - NODE_ENV=development
#       - VITE_API_URL=http://api:8000
#       - VITE_KEYCLOAK_URL=http://localhost:8080
#     depends_on:
#       - api
#
# ===================================================================
