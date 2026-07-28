# LMS Maintenance Documentation

> Learning Management System maintenance page

## Overview

The LMS infrastructure includes maintenance and static pages for both ctc-research.com and structa.cloud.

## Maintenance Page

```html
<!-- compose/lms/maintenance.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maintenance Mode</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        p { font-size: 1.25rem; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Maintenance Mode</h1>
        <p>We're performing scheduled maintenance. Please check back soon.</p>
    </div>
</body>
</html>
```

## Usage

The maintenance page is served by Nginx when the application is in maintenance mode:

```nginx
# Enable maintenance mode
if ($maintenance = on) {
    return 503;
}

error_page 503 @maintenance;
location @maintenance {
    root /var/www/lms;
    try_files /maintenance.html =503;
}
```

## Related Documentation

- [Traefik Documentation](../../traefik/README.md)
- [Nginx Documentation](../../nginx/README.md)
- [PostgreSQL Documentation](../../postgres/README.md)
- [Main Infrastructure](../README.md)
