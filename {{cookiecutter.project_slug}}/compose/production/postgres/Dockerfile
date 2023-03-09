FROM kartoza/postgis:{{ cookiecutter.postgresql_version }}

LABEL maintainer="Truong Thanh Tung <ttungbmt@gmail.com>"

###########################################################################
# Set Timezone
###########################################################################

ARG TIMEZONE=Asia/Ho_Chi_Minh
ENV TIMEZONE ${TIMEZONE}

###########################################################################
# Set Extensions
###########################################################################
ARG POSTGRES_MULTIPLE_EXTENSIONS='postgis,hstore,postgis_topology,postgis_raster,unaccent'
ENV POSTGRES_MULTIPLE_EXTENSIONS ${POSTGRES_MULTIPLE_EXTENSIONS}

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
