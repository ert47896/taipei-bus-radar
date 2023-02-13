FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY bus.conf /etc/nginx/sites-available/

RUN mkdir -p /etc/nginx/sites-enabled/\
    && ln -s /etc/nginx/sites-available/bus.conf /etc/nginx/sites-enabled/

CMD ["nginx", "-g", "daemon off;"]
