# SpaceX Launch Analytics

Live site: [https://spacex-launch-analytics.netlify.app/](https://spacex-launch-analytics.netlify.app/)

A browser-only port of `spacex-dash-app.py`, using the same CSV from IBM's Applied Data Science Capstone Module 3. Its UI retains the Dash app's launch-site selector, success pie chart, payload-mass range slider (0–10,000 kg, with marks every 1,000 kg) and outcome-versus-payload scatter chart grouped by booster category. Its editable minimum and maximum fields accept precise custom values, such as 857 to 9,002 kg.

## Publish updates

Deploy the contents of this folder to the existing Netlify project, `spacex-launch-analytics`. The folder itself is the publish directory; `index.html`, `_headers`, `404.html`, `robots.txt`, and `sitemap.xml` must all be at its root. No build command is needed.

The canonical URL, sitemap, and social preview tags use the live Netlify address above. Update those values together if the site gets a custom domain. `favicon.ico` is generated from `favicon-48.png`, which uses the X mark from [SpaceX's own website](https://www.spacex.com/assets/favicon-spacex.ico). The Apple touch icon uses the [X-only logo artwork on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:SpaceX-Logo-Xonly.svg). The social card shows successful launches by site from the included CSV, with `social-card.svg` as its editable source. This educational dashboard is not affiliated with SpaceX.

`robots.txt` points crawlers to the one-page sitemap. `_headers` sets a few browser security headers. Netlify serves `404.html` for missing paths. This site has no client-side routes, installable app, or security contact process, so it does not use `_redirects`, `site.webmanifest`, or `.well-known/security.txt`.

The site has no build tools, Python backend, or paid-plan requirement. Plotly.js loads from a CDN, so visitors need an internet connection.

## Important distinction

This is a JavaScript **functional port** of the Python Dash app, not a hosted Dash Python process. Retain and submit the original `.py` script to demonstrate the Dash coursework requirement. The static site reproduces the dashboard's dataset, aggregations, selections, slider filtering and Plotly chart behavior; minor visual differences between the Dash and browser controls may remain.

## Test locally

Open via GitHub Pages/Netlify, or serve the folder over HTTP (e.g., `python -m http.server 8000`) and visit `http://localhost:8000`. Opening `index.html` as a `file://` URL may prevent the browser from loading the CSV because of browser security rules.
