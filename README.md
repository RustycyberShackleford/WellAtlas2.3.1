# WellAtlas 2.3

## Features
- Customers → Sites → Jobs hierarchy
- Interactive map with MapTiler satellite
- "Find Sites Near Me" button (centers map, does not drop pins)
- Demo seed data (5 presidents × 5 sites × 4 jobs each)

## Deployment
1. Upload to GitHub.
2. On Render, set **Start Command** = `web: gunicorn app:app`
3. No env vars needed yet (MapTiler key can be swapped in index.html).
