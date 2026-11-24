# Hosting the site

Target: `https://oscar.vonallmen.co`, served from the Hetzner server. Static files only, no build step.

## The server

Hetzner Cloud CX23, Ubuntu 24.04, Docker. It also runs Atrekos in production (Next.js, Postgres and more). Whatever terminates HTTPS for atrekos.com will also have to serve this site, so a mistake here can take Atrekos down. Change the proxy configuration in a quiet hour and check atrekos.com straight after.

Still unknown:

- Which container takes ports 80 and 443 (Caddy, Traefik, nginx, or the Next.js container itself). Run on the server:

  ```
  docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
  ```

- Where DNS for vonallmen.co is managed.

## Plan

1. **DNS:** an `A` record for `oscar.vonallmen.co` pointing at the server's IPv4 address, and `AAAA` for IPv6.
2. **Files:** the site lives in `/srv/oscar` on the host. A separate user `oscar-deploy` owns that folder and nothing else. It is not in the `docker` group, because membership there is equal to root.
3. **Serving:** the existing reverse proxy serves `/srv/oscar` for `oscar.vonallmen.co`, mounted read-only. If the proxy is Caddy, the block is:

   ```
   oscar.vonallmen.co {
       root * /srv/oscar
       file_server
       encode zstd gzip
       header {
           Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
           Referrer-Policy "no-referrer"
           X-Content-Type-Options "nosniff"
           Permissions-Policy "camera=(), microphone=(), geolocation=()"
       }
       @fonts path /assets/fonts/*
       header @fonts Cache-Control "public, max-age=31536000, immutable"
   }
   ```

   With Traefik, a small `caddy:2-alpine` or `nginx:alpine` container serves `/srv/oscar` read-only and gets Traefik labels for the host name. The headers stay the same. The policy allows nothing from other servers, which is what the site promises.
4. **Deploy key:** a new SSH key pair used only for this. Public key into `oscar-deploy`'s `authorized_keys`, ideally restricted to rsync. Private key, host, user (`oscar-deploy`), path (`/srv/oscar`) and the server's `known_hosts` line go into the repository secrets used by `deploy/deploy.yml`.
5. **First run:** move `deploy/deploy.yml` to `.github/workflows/deploy.yml`, push, run the workflow by hand once, and check the site on a phone and a laptop, in light and dark mode. Check atrekos.com too.
6. **Then:** add the `push` trigger to the workflow, so every push to `main` that touches `site/` deploys.

Publishing or changing the public site needs Alex's go-ahead each time.
