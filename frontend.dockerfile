FROM node:20-alpine AS build
WORKDIR /app
# Install only what we need to build CSS deterministically
COPY frontend/package.json ./package.json
COPY frontend/package-lock.json ./package-lock.json
RUN npm ci --omit=optional --no-audit --no-fund
COPY frontend/scss ./scss
RUN mkdir -p css && npx sass --no-source-map --style=compressed scss/main.scss css/app.css

FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
COPY --from=build /app/css/app.css /usr/share/nginx/html/css/app.css
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
