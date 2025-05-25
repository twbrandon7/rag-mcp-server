# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:22 AS build-stage

# Install pnpm
RUN npm install -g pnpm@latest-10

# Install Angular CLI
RUN npm install -g @angular/cli@latest

WORKDIR /app

COPY package*.json /app/

RUN pnpm install

COPY ./ /app/

RUN ng build --configuration production --output-path=dist

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/browser /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
