import datetime
import json
import os
from invoke import task

@task
def settingenv(ctx):
    print("***************************setting env*********************************")

    override_env = "$HOME/.override_env"
    if os.path.exists(override_env):
        os.remove(override_env)
    else:
        print(f"Can not delete the {override_env} file as it doesn't exists")

    envs = {
        "local_settings": str(_localsettings()),
        "site_url": os.environ.get("SITE_URL", 'http://localhost:8000/'),
        "db_url": os.environ.get("DATABASE_URL", 'postgres://debug:debug@postgres:5432/postgres'),
        "celery_broker_url": os.environ.get("REDIS_URL", 'redis://redis:6379/0'),
        "override_fn": override_env,
    }

    ctx.run("echo export DJANGO_SETTINGS_MODULE={local_settings} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export SITE_URL={site_url} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export DATABASE_URL={db_url} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export CELERY_BROKER_URL={celery_broker_url} >> {override_fn}".format(**envs), pty=True)


    ctx.run(f"source {override_env}", pty=True)
    print("****************************finalize env**********************************")
    ctx.run("env", pty=True)


@task
def waitfordbs(ctx):
    print("**************************wait for databases*******************************")
    ctx.run(f"/usr/bin/wait-for-databases", pty=True)

@task
def waitformigrations(ctx):
    print("**************************wait for migrations*******************************")
    ctx.run(f"/usr/bin/wait-for-migrations", pty=True)


@task
def migrations(ctx):
    print("**************************migrations*******************************")
    ctx.run(f"python manage.py migrate --noinput", pty=True)


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
    # # Method 1
    # import django
    # from django.contrib.auth import get_user_model
    #
    # django.setup()
    # User = get_user_model()
    # username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    #
    # if User.objects.filter(username=username).count() == 0:
    #     ctx.run("python manage.py createsuperuser --noinput", pty=True)
    # else:
    #     print('Superuser creation skipped.');

    # Method 2
    ctx.run("rm -rf /tmp/django_admin_docker.json", pty=True)
    _prepare_admin_fixture(
        os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
        os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@admin.com"),
        os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin@123")
    )
    ctx.run(f"python manage.py loaddata /tmp/django_admin_docker.json", pty=True)

def _prepare_admin_fixture(admin_user, admin_email, admin_password):
    from django.contrib.auth.hashers import make_password

    d = datetime.datetime.now()
    mdext_date = f"{d.isoformat()[:23]}Z"
    default_fixture = [
        {
            "model": "users.user",
            "pk": 1000,
            "fields": {
                 "password": make_password(admin_password),
                "last_login": mdext_date,
                "is_superuser": True,
                "username": admin_user,
                 "email": admin_email,
                "is_staff": True,
                "is_active": True,
                "date_joined": mdext_date,
                "name": "",
                "groups": [],
                "user_permissions": []
            }
        }
    ]
    with open("/tmp/django_admin_docker.json", "w") as fixturefile:
        json.dump(default_fixture, fixturefile)

def _localsettings():
    settings = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.local")
    return settings
