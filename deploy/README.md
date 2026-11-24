# Hosting the site

Target: `https://oscar.vonallmen.co`. Static files only, no build step, served by the Caddy container of the Atrekos server on Hetzner.

- How the server hosts static sites, the one-time Atrekos change, and the step-by-step setup: [server/README.md](server/README.md)
- Caddy config for this site: [server/oscar.caddy](server/oscar.caddy), shared settings in [server/_static.caddy](server/_static.caddy)
- Workflow that uploads `site/` to `/srv/sites/oscar`: [deploy.yml](deploy.yml)

## Status, 24 Nov 2026

- DNS: done. Cloudflare zone `vonallmen.co`, proxied `A` and `AAAA` records for `oscar`.
- Server: waiting for the one-time Atrekos change and for `add-site.sh oscar`.
- Workflow: waiting for the repository secrets. Then move `deploy/deploy.yml` to `.github/workflows/deploy.yml` and run it by hand once.
- After the first good run, add the `push` trigger so every push to `main` that touches `site/` deploys.

Cloudflare caches CSS, JavaScript, fonts and images at its edge. `_static.caddy` sends `Cache-Control` headers so a changed stylesheet is served right after a deploy.

Publishing or changing the public site needs Alex's go-ahead each time.
