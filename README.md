# Oscar the Bot

Build log, plan and files for Oscar, a 3D-printed, tank-tracked Wall-E replica with a brain a child can talk to and teach.

The robot body follows [chillibasket's open-source Wall-E replica](https://wired.chillibasket.com/3d-printed-wall-e/). This project adds three AI layers on top: face following, a voice loop with a language model, and a game in which a child teaches the robot to recognise her toys.

Website: `https://oscar.vonallmen.co` (not live yet).

## What is in this repository

| Path | Content |
|---|---|
| `site/` | The website. Hand-written HTML pages, one stylesheet, no build step |
| `site/log.html` | Build log. New entries go at the top, from the template in the comment |
| `site/files/` | Our own files: fit model picture, component boxes (STEP), CadQuery script |
| `site/photos/` | Build photos, one folder per date, prepared with `tools/prep_photos.py` |
| `site/assets/` | Stylesheet, fonts (served from the site), the script that shows the latest log entries on the home page |
| `tools/prep_photos.py` | Resizes photos and removes all metadata, including location |
| `deploy/` | Notes for hosting on the server |
| `deploy/deploy.yml` | GitHub Actions workflow that copies `site/` to the server. Manual trigger only. Moves to `.github/workflows/` once the server is ready |

Robot code will be added here once there is code worth reading.

## View the site locally

```
cd site && python3 -m http.server 8000
```

Then open <http://localhost:8000>. Opening `site/index.html` directly from disk also works, except that the home page then shows a link to the build log instead of the latest entries.

The site makes no requests to other servers.

## Rules for the content

- No name or age of my daughter, and no photo, video or recording of her.
- Location data removed from every photo before it is committed.
- No private file paths, no email address.
- Other people's CAD files are linked, not copied, unless their licence allows it and the licence is stated next to the file.

## Credits

- [chillibasket](https://wired.chillibasket.com/3d-printed-wall-e/) designed the robot and published the CAD files and the [Arduino and web interface code](https://github.com/chillibasket/walle-replica) (GPL-3.0).
- The remixes used are by JaZzMaN251, ZDC, dmdiego, Guenter, Fendermann and rene1960, listed with links and licences on the site's design changes page.
- [WALL-E-DORA](https://mneuhaus.github.io/wall-e-dora) by mneuhaus is a more advanced build in the same lineage, and the source of the rear battery flap and front power button ideas.
- Font: Geist by Vercel, SIL Open Font License 1.1. Look based on the Grounded Precision design system, with Sunflower Yellow and Hot Pink from the build.

## Licence

MIT for the site's text and pictures and for CAD files and code made from scratch for this project. See [LICENSE](LICENSE) for the scope: parts derived from other people's files keep their original licence, and code derived from chillibasket's code is GPL-3.0.

## Disclaimer

This is an unofficial fan build and a personal project. WALL-E is a character owned by Disney and Pixar. This project is not affiliated with or endorsed by either company.
