# Static sites on the Atrekos server

The Hetzner server (CX23, Ubuntu 26.04, `2.31.28.22`) runs Atrekos with Docker. Its Caddy container (`atrekos-caddy-1`) holds ports 80 and 443, so every other site on this server goes through the same Caddy.

The Caddy config and the compose file belong to the Atrekos release bundle and are rewritten on every Atrekos release. Static sites therefore live in a folder of their own, outside the bundle. After one change to Atrekos, adding or changing a site never touches Atrekos again.

| Site | Domain | Web root | Upload user | Caddy file | State |
|---|---|---|---|---|---|
| Oscar the Bot | `oscar.vonallmen.co` | `/srv/sites/oscar` | `oscar-deploy` | `oscar.caddy` | DNS done, waiting for Caddy |
| Personal website | `www.vonallmen.co`, `vonallmen.co` forwards to it | `/srv/sites/www` | `www-deploy` | `www.caddy.disabled` | Prepared, not live |

## Layout on the server

```
/srv/sites/                  root, 755. Mounted read-only into Caddy at the same path
├── caddy/                   root, 755. Imported by the Atrekos Caddyfile
│   ├── _static.caddy        shared settings: files, compression, security and cache headers
│   ├── oscar.caddy
│   └── www.caddy.disabled   ignored until renamed to www.caddy
├── oscar/                   oscar-deploy, 755. Uploaded by GitHub Actions
└── www/                     www-deploy, 755
```

Each upload user can only rsync into its own folder (`rrsync` in its `authorized_keys`). It has no shell and is not in the `docker` group. Only root changes the Caddy files.

## Step 1: one-time change in the Atrekos repository

Make this where the bundle is built, so the next Atrekos release brings it. Two edits:

`docker-compose.yml`, service `caddy`, one more volume:

```yaml
      - /srv/sites:/srv/sites:ro
```

`caddy/Caddyfile`, one line at the end, after all Atrekos site blocks:

```
import /srv/sites/caddy/*.caddy
```

If the folder is empty or missing, Caddy logs a warning and starts normally, so Atrekos does not depend on these sites. The new volume needs the Caddy container recreated, not just reloaded, so atrekos.com is unreachable for a few seconds during that release.

Before the release, run Step 2 so the folder exists. After it:

```
cd /srv/atrekos
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
```

## Step 2: prepare the folders and Oscar

Copy this folder's files to the server, then as root:

```
sudo ./add-site.sh oscar "$(cat oscar_deploy.pub)"
sudo install -m 644 -o root -g root _static.caddy oscar.caddy www.caddy.disabled /srv/sites/caddy/
```

`oscar_deploy.pub` is the public half of the deploy key made on the Mac:

```
ssh-keygen -t ed25519 -f ~/.ssh/oscar_deploy -N "" -C "oscar-the-bot deploy"
```

If you already created `/srv/oscar` and `oscar-deploy` from the earlier instructions, run the same command anyway. It keeps the user and moves nothing, so delete the empty `/srv/oscar` by hand.

## Step 3: secrets in the Oscar repository

```
gh secret set DEPLOY_HOST --body "2.31.28.22"
gh secret set DEPLOY_USER --body "oscar-deploy"
gh secret set DEPLOY_PATH --body "."
gh secret set DEPLOY_KEY < ~/.ssh/oscar_deploy
ssh-keyscan -t ed25519 2.31.28.22 | gh secret set DEPLOY_KNOWN_HOSTS
```

`DEPLOY_PATH` is `.` because `rrsync` already pins uploads to the site's folder. If the Hetzner firewall allows SSH only from certain addresses, GitHub's runners will be blocked. In that case the workflow needs to run on one of the Atrekos self-hosted runners instead.

## Step 4: reload Caddy after a Caddy file changes

```
cd /srv/atrekos
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
```

A reload does not drop connections. Uploading site files needs no reload.

## Launch www.vonallmen.co

1. On the server: `sudo ./add-site.sh www "$(cat www_deploy.pub)"`.
2. Deploy the site once into `/srv/sites/www`, with the same workflow as Oscar and its own secrets.
3. `sudo mv /srv/sites/caddy/www.caddy.disabled /srv/sites/caddy/www.caddy`, then Step 4.
4. Cloudflare, zone `vonallmen.co`: proxied `A` and `AAAA` records for `www` and for the bare domain `vonallmen.co`, pointing at the server. The records for the bare domain do not affect email (iCloud MX and DKIM records stay as they are).
5. Open both addresses. The bare domain should forward to `https://www.vonallmen.co`.

Do step 4 last. Proxied records without a matching Caddy site show a Cloudflare error page.

The shared security policy allows nothing from other servers. If the personal site needs something else, give `www.caddy` its own `header` lines instead of changing `_static.caddy`, which Oscar uses too.

## Cloudflare zone vonallmen.co, settings as of 24 Nov 2026

SSL mode Full (strict), minimum TLS 1.2, email obfuscation off, Always Use HTTPS off (Caddy redirects to HTTPS itself). Records for these sites are proxied, so the server's address stays hidden behind Cloudflare, as it is for atrekos.com.
