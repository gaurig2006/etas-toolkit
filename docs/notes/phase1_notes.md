# Phase 1: Catalog Data Model & Ingestion Architecture

## 1. Required Catalog Row Fields
To support consistent ETAS modeling, spatial kernel evaluation, and quality analysis, every ingested event row must carry the following core fields:
- `event_id` (str): Unique alphanumeric identifier from the originating agency.
- `time` (datetime64[ns, UTC]): Absolute UTC origin time of the event.
- `time_days` (float64): Continuous elapsed time in decimal days relative to the catalog origin $t_0$ ($t_i = (T_i - T_0) / 86400$)[cite: 1].
- `longitude` (float64): Geographic longitude in decimal degrees ($[-180.0, 180.0]$)[cite: 1].
- `latitude` (float64): Geographic latitude in decimal degrees ($[-90.0, 90.0]$)[cite: 1].
- `depth` (float64): Hypocentral focal depth in kilometers below the sea level datum[cite: 1].
- `magnitude` (float64): Reported event magnitude[cite: 1].
- `magnitude_type` (str): Magnitude scale identifier (`Mw`, `ML`, `mb`, `Ms`)[cite: 1].
- `agency` (str): Contributing seismological agency (e.g., `USGS`, `SCEDC`, `INGV`)[cite: 1].
- `x_km`, `y_km` (float64, optional): Local Cartesian projected coordinates in kilometers relative to the regional anchor[cite: 1].

## 2. Magnitude Scales ($M_L$, $M_w$, $m_b$, $M_s$) and Non-Interchangeability
Earthquake magnitude scales measure different seismic wave properties across distinct frequency bands; therefore, raw values cannot be used interchangeably without homogenization[cite: 1]:
- **Local Magnitude ($M_L$)**: Empirical peak-amplitude scale on Wood-Anderson seismographs ($\sim 1\text{–}10\text{ Hz}$). Saturates severely above $M_L \approx 6.5$ because high-frequency ground motion caps while fault rupture area continues expanding.
- **Body-Wave Magnitude ($m_b$)**: Measured on teleseismic P-waves ($\sim 1\text{ Hz}$). Saturates near $m_b \approx 6.0\text{–}6.5$ due to attenuation and spectral corner frequency shifts.
- **Surface-Wave Magnitude ($M_s$)**: Measured on 20-second Rayleigh waves. Effective for shallow earthquakes but saturates around $M_s \approx 8.0\text{–}8.4$.
- **Moment Magnitude ($M_w$)**: Grounded in scalar seismic moment $M_0 = \mu A D$ via $M_w = \frac{2}{3} (\log_{10} M_0 - 9.1)$ ($M_0$ in $\text{N}\cdot\text{m}$)[cite: 1]. $M_w$ has no physical saturation ceiling, making it the standard for ETAS productivity scaling[cite: 1].

Mixing raw $M_L$ and $M_w$ in an ETAS kernel introduces severe bias in the productivity term $K e^{\alpha(m_i - m_0)}$, as a 0.5 unit divergence scales estimated aftershock productivity exponentially by $e^{0.5 \alpha} \approx 2.2\times$[cite: 1].

## 3. Hypocenter vs. Epicenter
- **Hypocenter (Focus)**: The true 3D spatial point origin $(x, y, z)$ within the crust where the rock begins rupturing. It includes the depth coordinate $z$, which governs seismic energy propagation and aftershock depth distribution.
- **Epicenter**: The 2D geographic projection $(x, y)$ of the hypocenter directly onto the Earth's surface directly above the rupture origin.

## 4. QuakeML Standard
QuakeML is an XML-based schema established by the FDSN (International Federation of Digital Seismograph Networks) for standardizing seismic event parameters[cite: 1]. It structures event metadata hierarchically:
- `<eventParameters>`: Root container.
- `<event>`: Unique seismic incident containing origins and magnitudes.
- `<origin>`: Contains evaluated spatial hypocenters (`latitude`, `longitude`, `depth`, `time`, and evaluation status).
- `<magnitude>`: Contains estimated magnitudes, standard deviations, and magnitude types (`mag`, `type`).
Using ObsPy's `read_events()` parses QuakeML trees across global FDSN nodes into unified data structures[cite: 1].
