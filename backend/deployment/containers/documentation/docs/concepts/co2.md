# CO2e calculcation

For each [Booking](bookings.md) that is finished or update, a Wallet entry is created or updated 
that reflects the CO2-equivalent emission of that booking.

The wallet technically is capable of managing different datasets, but currently, it is used only for recording
CO2-equivalent emission associated with the bookings (`wallet=CO2e`).

There are different sources of the actual quantity of grams of CO2-equivalent emissions:

1. External systems (like RRive) can directly report CO2e values. These are always used when available.
2. For bookings that have a [distance](bookings.md#distance), the emission is calculated from that distance, multiplied
   by an emissions intensity as described below.

## Emission intensities

To decide, which mode of transport causes how much emission, the values from 
**`/admin-backend/` -> Administration -> CO2e Emissions** are used.

The initial values are taken from the [Umweltbundesamt](https://www.umweltbundesamt.de/bild/vergleich-der-durchschnittlichen-emissionen-0).

## Export

A CSV file of all wallet entries can be generated via
**`/admin-backend/` -> Administration -> CO2e Emissions -> Export**.