import datetime
import json
import os
from invoke import task
import sys
import time
import psycopg2

@task
def settingenv(ctx):
    print("***************************setting env*********************************")

    override_env = "$HOME/.override_env"
    if os.path.exists(override_env):
        os.remove(override_env)
    else:
        print(f"Can not delete the {override_env} file as it doesn't exists")

    envs = {
        "siteurl": os.environ.get("SITEURL", 'http://localhost:8000/'),
        "override_fn": override_env,
    }

    ctx.run("echo export SITEURL={siteurl} >> {override_fn}".format(**envs), pty=True)

    ctx.run(f"source {override_env}", pty=True)
    print("****************************finalize env**********************************")
    ctx.run("env", pty=True)

@task
def waitfordbs(ctx):
    print("**************************wait for databases*******************************")
    # db_host = os.getenv("DATABASE_HOST", "db")
    # ctx.run(f"/usr/bin/wait-for-databases {db_host}", pty=True)

    suggest_unrecoverable_after = 60
    start = time.time()

    dbname = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")

    while True:
        try:
            psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
            )
            break
        except psycopg2.OperationalError as error:
            sys.stderr.write("Waiting for PostgreSQL to become available...\n")

            if time.time() - start > suggest_unrecoverable_after:
                sys.stderr.write(
                    "  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(
                        error))

        time.sleep(1)

    ctx.run("echo PostgreSQL is available", pty=True)


@task
def waitformigrations(ctx):
    print("**************************wait for migrations*******************************")

@task
def migrations(ctx):
    print("**************************migrations*******************************")
    ctx.run(f"python manage.py migrate --noinput", pty=True)
    # try:
    #     ctx.run(f"python manage.py rebuild_index --noinput", pty=True)
    # except Exception:
    #     pass

@task
def collectstatic(ctx):
    print("**************************collectstatic*******************************")
    try:
        ctx.run("mkdir -p /mnt/volumes/statics/{static,uploads}")
        ctx.run(f"python manage.py collectstatic --noinput", pty=True)
    except Exception:
        import traceback

        traceback.print_exc()

@task
def preparefixture(ctx):
    print("**********************prepare fixture***************************")


@task
def loaddata(ctx):
    print("**************************load data********************************")
    # ctx.run(f"python manage.py loaddata sample_admin", pty=True)
    # ctx.run(f"python manage.py loaddata /tmp/default_oauth_apps_docker.json", pty=True)
    # ctx.run(f"python manage.py loaddata geonode/base/fixtures/initial_data.json", pty=True)

@task
def initialized(ctx):
    print("**************************init file********************************")
    ctx.run("date > /mnt/volumes/statics/django_init.lock")


@task
def updateadmin(ctx):
    print("***********************update admin details**************************")
    # docker-compose -f local.yml run --rm django python manage.py createsuperuser --noinput
    # ctx.run("rm -rf /tmp/django_admin_docker.json", pty=True)
    # _prepare_admin_fixture(os.environ.get("ADMIN_PASSWORD", "admin"), os.environ.get("ADMIN_EMAIL", "admin@example.org"))
    # ctx.run(f"django-admin.py loaddata /tmp/django_admin_docker.json", pty=True,)

# def _prepare_admin_fixture(admin_password, admin_email):
#     from django.contrib.auth.hashers import make_password
#
#     d = datetime.datetime.now()
#     mdext_date = f"{d.isoformat()[:23]}Z"
#     default_fixture = [
#         {
#             "fields": {
#                 "date_joined": mdext_date,
#                 "email": admin_email,
#                 "first_name": "",
#                 "groups": [],
#                 "is_active": True,
#                 "is_staff": True,
#                 "is_superuser": True,
#                 "last_login": mdext_date,
#                 "last_name": "",
#                 "password": make_password(admin_password),
#                 "user_permissions": [],
#                 "username": "admin",
#             },
#             "model": "people.Profile",
#             "pk": 1000,
#         }
#     ]
#     with open("/tmp/django_admin_docker.json", "w") as fixturefile:
#         json.dump(default_fixture, fixturefile)
