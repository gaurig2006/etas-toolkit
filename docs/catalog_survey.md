# Phase 0: Global and Regional Earthquake Catalog Survey

## 1. Survey Overview
Technical assessment of 17 catalog sources across 7 global aggregators and 8 focus regions.

| Source Agency | Target Region | Spatial Coverage | Temporal Range | Min Mag ($M_{\min}$) | Access Interface | Output Formats | Auth? | Result Caps | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **USGS ComCat** | Global / US | Global | 1900–present | $M \ge 0.0$ (US), $M \ge 4.0$ (Global) | FDSN Web Service (`/fdsnws/event/1/`), GeoJSON | QuakeML, GeoJSON, CSV | No | 20,000 events/query | **Clean API** (Auto-windowing) |
| **ISC Bulletin** | Global | Global | 1904–present | $M \ge 3.5$ | FDSN Web Service (`/fdsnws/event/1/`) | QuakeML, CSV, IMS1.0 | No | Windowing recommended | **Clean API** |
| **ISC-GEM** | Global | Global | 1904–2020 | $M_w \ge 5.5$ | Static bulk file download | CSV | No | None | **Clean / Bulk File** |
| **EMSC-CSEM** | Euro-Med / Global | Global | 1998–present | $M \ge 1.5$ (Euro-Med), $M \ge 4.0$ (Global) | FDSN Web Service, WebSocket | QuakeML, GeoJSON, CSV | No | 20,000 events/query | **Clean API** |
| **IRIS / EarthScope** | Global | Global | 1970–present | Variable | FDSN Web Service (`/fdsnws/event/1/`) | QuakeML, TEXT, GeoJSON | No | Standard FDSN limits | **Clean API** |
| **GEOFON (GFZ)** | Global | Global | 2007–present | $M \ge 4.0$ | FDSN Web Service (`/fdsnws/event/1/`) | QuakeML, GeoJSON, CSV | No | Standard FDSN limits | **Clean API** |
| **Global CMT** | Global | Global | 1976–present | $M_w \ge 5.0$ | Bulk `.ndk` catalog download | NDK format | No | File-based | **Bulk File** |
| **SCEDC / NCEDC** | California | Southern / Northern CA | 1932–present (SC), 1967–present (NC) | $M \ge 1.0$ | FDSN Web Service | QuakeML, CSV, Text | No | Windowing recommended | **Clean API** |
| **INGV (ISIDe)** | Italy | Italy / Central Med | 1985–present | $M \ge 0.5$ | FDSN Web Service | QuakeML, GeoJSON, Text | No | 10,000 events/query | **Clean API** |
| **INGV HORUS** | Italy | Italy | 1960–present | $M_w \ge 4.0$ | Bulk file download | Tab-delimited Text | No | Historical snapshot | **Needs Parsing** |
| **NOA** | Greece | Greece & Aegean | 1964–present | $M \ge 1.0$ | FDSN Web Service | QuakeML, CSV | No | Standard limits | **Clean API** |
| **AUTH** | Greece | Greece | 1981–present | $M \ge 1.0$ | Web HTML listing | HTML `<pre>` tables | No | Date-range limits | **Needs Scraping** |
| **AFAD** | Türkiye | Türkiye region | 1990–present | $M \ge 0.5$ | Custom REST API (`/apiv2/event/filter`) | JSON | No | API pagination | **Clean API** |
| **KOERI** | Türkiye | Türkiye / Marmara | 1900–present | $M \ge 1.0$ | Web HTML listings | HTML text / `<pre>` | No | Query range limits | **Needs Scraping** |
| **GeoNet** | New Zealand | New Zealand | 1940–present | $M \ge 1.5$ | FDSN Web Service, QuakeSearch / WFS | QuakeML, GeoJSON, CSV | No | CSV first-class | **Clean API** |
| **JMA / NIED** | Japan | Japan | 1923–present | $M \ge 0.0$ | Web form / FTP | Fixed-width deck format | **Yes** | Form limits | **Needs Scraping & Registration** |
| **CSN** | Chile | Chile | 2000–present | $M \ge 2.0$ | Daily HTML tables / Zenodo snapshot | HTML / CSV | No | No direct query API | **Needs Scraping** |
| **CWA GDMS** | Taiwan | Taiwan | 1991–present | $M \ge 1.0$ | GDMS portal / Data.gov.tw snapshot | Form download / CSV | **Yes** | Portal limits | **Needs Scraping / Registration** |
