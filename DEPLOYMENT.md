# Deploying ParkManager to Render

The repository includes a Render Blueprint (`render.yaml`) for deploying the Django app and provisioning a PostgreSQL database.

## Deploy

1. Sign in to [Render](https://render.com/) and connect your GitHub account.
2. In the Render dashboard, choose **New → Blueprint** and select `JakuarOvi/Parking-Management-System`.
3. Review the services in `render.yaml` and choose **Apply**. Render will build the backend, collect static files, run database migrations, and start the web service.
4. Open the generated `https://park-management-system.onrender.com` URL. The health endpoint is `/api/health/`.
5. Create an administrator account from the service shell with `python manage.py createsuperuser` (the service root directory is `ParkManager_Fixed/backend`). Do not use any demo credentials in production.

The Blueprint configures `SECRET_KEY` using Render's generated secret and links `DATABASE_URL` to the PostgreSQL service. The included free-tier plans may have limits or change; check Render's current pricing and service availability before applying.

## Important notes

- This app uses Django session authentication. Use HTTPS in production; Render's service URL provides HTTPS.
- The app's current `ALLOWED_HOSTS` is `.onrender.com`. If you attach a custom domain, add that domain to the service's `ALLOWED_HOSTS` environment variable.
- Uploaded profile images and generated media files are stored on the web service filesystem by default. Ephemeral hosting filesystems do not provide durable media storage; configure persistent/object storage before relying on uploaded media.
- Redis-backed Channels and Celery are optional for the basic HTTP app, but features depending on Redis or scheduled Celery tasks need a Redis service and worker/beat processes configured separately.
- Review the application’s existing tests and security settings before using it with real users or payments.
