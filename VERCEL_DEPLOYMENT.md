# Deploy CARWA To Vercel

## Important limitation

This project uses SQLite and local image uploads. On Vercel, serverless files are temporary:

- The bundled `database.db` is copied to `/tmp` so the app can run.
- New leads, admin changes, wishlist rows, and uploaded images can reset when Vercel refreshes the serverless function.
- For a permanent production website, move the database to a hosted database such as Supabase Postgres, Neon, or Vercel Postgres, and move uploads to Cloudinary or Vercel Blob.

## Deployment steps

1. Push this project to GitHub.
2. Go to Vercel and choose **Add New Project**.
3. Import the GitHub repository.
4. Keep the default framework setting as **Other**.
5. Add this environment variable in Vercel:

   ```text
   SECRET_KEY=choose-a-long-random-secret
   ```

6. Deploy.

## Local check before deploy

```bash
.venv/bin/python -m py_compile app.py api/index.py
.venv/bin/flask --app app run --port 5001
```

## Size warning

The `static` folder is large because it contains many car photos. Vercel serves those files as static assets, while `vercel.json` excludes `static/**` from the Python function bundle using `functions.api/index.py.excludeFiles`.

`.vercelignore` also excludes unused duplicate HEIC originals from the deployment upload.

If Vercel still rejects the deployment because of size, compress the remaining images or host them on Cloudinary/Vercel Blob and store image URLs in the database.
