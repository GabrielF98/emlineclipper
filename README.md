# emlineclipper
Python library to clip emission lines in Supernova spectra.

# How it works
The code takes a spectrum from the user and plots it. It then asks the user to double click the plot at the edges of emission lines to remove.

On each click, a line is drawn. Every pair of clicks is assumed to bracket a line that needs to be removed, these are called bounding lines. Groups of emission lines can be bounded using just two bounding lines, provided they are sufficiently close (a couple of samples apart).

The code then iterates over each pair of bounding lines. The code selects a chunk of the input flux array +/-100Å away from the lower/upper bounding lines by default.

Values within the bounding lines in this chunk are removed before performing a spline fit to the flux (with 5 knots by default). If other user-defined emission lines are present in the fitting window, they are removed as well. 

Within the chunk, residuals between the spline and the original spectrum outside the bounding lines are computed. The mean and standard deviation of the difference array is calculated. This is used to resample the spectrum by adding noise to the spline between the bounding lines.

This is performed iteratively from the blue end of the spectrum for each pair of bounding lines.

The code returns the array of flux with the emission lines removed and resampled using hte uncertainty arrays generated during fitting.

**Note:** Even when a line has been fit, the code performs the next for the next line on the original spectrum, i.e. without removing the previously fit line.

<img width="794" alt="Screenshot 2024-06-04 at 16 20 23" src="https://github.com/GabrielF98/emlineclipper/assets/72733933/6f2493ba-fcb4-46dc-844a-20ee08509644">
