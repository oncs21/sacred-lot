# Sacred Lot

## Current features

- Flutter dashboard for iOS and web, with an illustrative housing and parking model.
- Local address suggestions backed by SQLite full-text search, with Photon fallback when no local matches exist.
- A FastAPI endpoint for parcel lookup and preliminary housing estimates.
- An importer for Colorado public address data.

Explore connects address suggestions and parcel details to the API. Dashboard still uses sample data.

## Requirements

- Flutter with Dart 3.13.2 or newer
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- macOS and Xcode for the iOS simulator, or Chrome for the web app

## Backend

From the repository root:

```sh
cd services/api
uv sync
uv run python -m uvicorn app.main:app --reload
```

### Address database

Address suggestions require a local database. Obtain the Colorado public address geodatabase from the state's GIS data distribution. 

Extract the complete geodatabase folder here:

```text
data/raw/Master_Address_Public.gdb/
```

From the repository root, install dependencies and build the search database:

```sh
uv sync --project services/api
uv run --project services/api python scripts/import_addresses.py
```

This creates `data/processed/addresses.sqlite`. The importer skips blank addresses, invalid coordinates, and duplicate records.

### Configuration

Set environment variables before starting the API:

| Variable | Default |
| --- | --- |
| `SACRED_LOT_ADDRESS_DATABASE` | Repository's `data/processed/addresses.sqlite` |
| `SACRED_LOT_GEOCODING_BBOX` | `-109.06,36.99,-102.04,41.00` |

The bounding box uses west, south, east, north coordinates. Settings are cached per process; restart the API after changing them. `.env` files are not loaded automatically.

### Endpoints

```sh
curl --get http://127.0.0.1:8000/search/addresses \
  --data-urlencode 'address=1820 15th Boulder' \
  --data-urlencode 'limit=5'

curl --get http://127.0.0.1:8000/search/parcel-details \
  --data-urlencode 'address=1820 15th St, Boulder, CO' \
  --data-urlencode 'density=0.3'
```

Address suggestions return `address`, `latitude`, and `longitude`. Queries require 3–200 characters and a limit of 1–10 results. A missing or incompatible database returns HTTP 503.

## Flutter app

From the repository root:

```sh
cd apps/mobile
flutter pub get
flutter run -d chrome
```

For iOS, open an iPhone simulator and run `flutter run` from the same directory, selecting the simulator if prompted.

Start the backend before using Explore. The app defaults to `http://127.0.0.1:8000` for the iOS simulator. Override it with `--dart-define=API_BASE_URL=https://your-api-host` for another server. Browser API access requires backend CORS configuration, which is not included yet.

## Tests

Backend, from the repository root:

```sh
cd services/api
uv run python -m pytest
```

Flutter, from the repository root:

```sh
cd apps/mobile
flutter analyze
flutter test
```

Backend tests use synthetic data and mocked external services; they do not require the downloaded geodatabase or a live Photon connection.

## Layout

```text
apps/mobile/       Flutter application
services/api/      FastAPI application and backend tests
scripts/           Dataset import tools
data/raw/          Original downloads
data/processed/    Generated databases
```

### Boulder zoning

Download the City of Boulder zoning boundaries from the repository root:

```sh
uv run --project services/api python scripts/download_zoning.py
```

The downloaded CSV contains district attributes but no boundaries. The downloader retrieves geometry from the official GIS service and writes `data/processed/boulder_zoning.geojson`, including the source URL and retrieval time. Refresh it by running the command again. Override the file path with `SACRED_LOT_ZONING_DATASET`.

`/search/parcel-details` includes a `zoning` result with district codes, descriptions, source metadata, and a status: `matched`, `partial`, `no_match`, or `unavailable`. Boundary-only contact does not count as overlap. No match does not establish jurisdiction or imply that the property is unzoned. Zoning rules and housing permissions are not evaluated, and these results do not change the illustrative housing calculation.
