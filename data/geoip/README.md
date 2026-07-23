# GeoIP data (local only)

This directory intentionally does **not** ship MaxMind database files.

For the [GeoIP tutorial post](/2020/07/20/get-ip-info/), download **GeoLite2-City** from MaxMind and place it here as:

```text
data/geoip/GeoLite2-City.mmdb
```

Official sources:

- [GeoLite2 free databases](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [Downloadable databases overview](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data/#downloadable-databases)

The `.mmdb` files are gitignored because they are large, redistributable under MaxMind’s license terms, and update regularly.
