FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY favicon.ico /
COPY nginx.conf /etc/nginx/conf.d
