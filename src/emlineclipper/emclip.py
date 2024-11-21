"""
Take an input wavelength and flux.
Ask the user to choose the regions to clip.
Define a region in which to perform fiting. By default 100 Å either side of users emission line choice.
Compute spline fit using data in the fitting region.
Produce the residual spectrum between the spline and the original spectrum in the fitting region.
Compute the mean and variance of the residual spectrum.
Sample from a Gaussian distribution with this mean and std dev to create the noise for the selected region.
Add noise to the spline in the selected region.
Replace the input spectrm in the selected region with the new spectrum.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

DELTA = 100
KNOTS = 5


def click_regions(event, fig, ax, emlines):
    """
    Plots a vertical line at the location of the user's click.
    Appends the wavelength of this line to the emlines list.

    Args:
        event (matplotlib.backend_bases.MouseEvent): mouse click event.
        fig (matplotlib.figure.Figure): matplotlib figure on which to draw the lines.
        ax (matplotlib.Axes): axis accompanying the matplotlib figure.
        emlines (list): list of emline locations, which will be added to each time this function is used.
    """

    if event.dblclick:
        if event.button == 3:
            if len(plt.gca().lines) > 1:
                plt.gca().lines[-1].remove()
                fig.canvas.draw()
                emlines.pop(-1)

        if event.button == 1:
            ax.axvline(event.xdata, color="tab:pink")
            fig.canvas.draw()
            emlines.append(event.xdata)


def define_regions(wlen, flux):
    """
    Creates the plot where the user can double click to set the bounding regions of emission lines.

    Args:
        wlen (numpy.ndarray): Wavelength array.
        flux (numpy.ndarray): Flux array.

    Returns:
        emlines (list): list of emission line bounding wavelengths.
    """

    emlines = []

    fig, ax = plt.subplots()
    ax.plot(wlen, flux)
    fig.canvas.mpl_connect(
        "button_press_event", lambda event: click_regions(event, fig, ax, emlines)
    )
    plt.show()

    return emlines


def find_adjacent_emlines(
    emline_list, line_lower, line_upper, wlen_zoom, flux_zoom_nan
):
    """
    Find out if there are other emlines near the emline which is being removed.
    If there are then set their values to NaN so that they do not affect the fit for the emline in question (mean, stddev etc.).

    Args:
        emline_list (list): Full list of emline bounding lines.
        line_lower (float): The lower wavelength of the line to be removed.
        line_upper (float): The upper wavelength of the line to be removed.
        wlen_zoom (numpy.ndarray): An wavelength array 100 A either side of the emission line being removed.
        flux_zoom_nan (_type_): Spectral flux array corresponding to the wavelengths in wlen_zoom.

    Returns:
        _type_: An array of fluxes within 100 A of the emission line in question, where fluxes of other emission lines are set to NaN so they do not impact removal of the line in question.
    """

    new_emline_list = emline_list.copy()
    new_emline_list.remove(line_lower)
    new_emline_list.remove(line_upper)
    if len(new_emline_list) != 0:
        for i in range(0, len(new_emline_list), 2):
            if new_emline_list[i] >= min(wlen_zoom) and new_emline_list[i + 1] <= max(
                wlen_zoom
            ):  # Check if both edges are within the range.
                flux_zoom_nan[
                    (wlen_zoom >= new_emline_list[i])
                    & (wlen_zoom <= new_emline_list[i + 1])
                ] = np.nan
            elif new_emline_list[i] <= max(wlen_zoom) and new_emline_list[i + 1] >= max(
                wlen_zoom
            ):  # Is the upper line above the min wlen in the range.
                flux_zoom_nan[
                    (wlen_zoom >= new_emline_list[i]) & (wlen_zoom <= max(wlen_zoom))
                ] = np.nan
            elif new_emline_list[i] < min(wlen_zoom) and new_emline_list[i + 1] >= min(
                wlen_zoom
            ):  # Is the lower line below the max wlen in the range.
                flux_zoom_nan[
                    (wlen_zoom >= min(wlen_zoom))
                    & (wlen_zoom <= new_emline_list[i + 1])
                ] = np.nan

    return flux_zoom_nan


def clip_line(
    wlen, flux, line_lower, line_upper, emline_list, verbose=False, path=None
):
    """
    Zoom in to DELTA angstroms either side of the supplied emission line boundaries.
    Set the region between the bounding lines to NaN.
    Check whether there are other lines present in the region bounded by bounding lines +/- delta.
    If there are, set them to NaN.
    Remove the NaNs with a mask.
    Fit a cubic spline to the zoomed in, masked flux array.
    Compute the residuals between the data and the spline fit.
    Compute the mean and std dev of the residual distribution.
    Use the mean and std dev of the distribution to generate a noisy spectrum using the spline fit in the region of the emission line.
    Plot and save figures if verbose==True.
    Return the new section of flux in the region of the emission line.

    Args:
        wlen (numpy.ndarray): Wavelength array. Taken from the input spectrum.
        flux (numpy.ndarray): Flux array. Taken from the input spectrum.
        line_lower (float): The lower wavelength of the line to be removed.
        line_upper (float): The upper wavelength of the line to be removed.
        emline_list (list): Full list of emline bounding lines.
        verbose (bool, optional): Flag indicating whether to save a figure of the spectrum near each emission line removal. Defaults to False.
        path (_type_, optional): Output path for figures. Defaults to None.

    Returns:
        new_spec_sections numpy.ndarray: corrected spectrum in the zoomed region around the emission line.
    """

    # Zoom in to DELTA angstroms either side of the line.
    wlen_zoom = wlen[(wlen >= line_lower - DELTA) & (wlen <= line_upper + DELTA)]
    flux_zoom = flux[(wlen >= line_lower - DELTA) & (wlen <= line_upper + DELTA)]

    # Set the region of the line to NaN
    flux_zoom_nan = flux_zoom.copy()
    flux_zoom_nan[(wlen_zoom >= line_lower) & (wlen_zoom <= line_upper)] = np.nan

    # Check if other emlines are present in the region. If so the set them to NaN so they won't affect the spline fit.
    flux_zoom_nan = find_adjacent_emlines(
        emline_list, line_lower, line_upper, wlen_zoom, flux_zoom_nan
    )

    # Remove NaN.
    mask = ~np.isnan(flux_zoom_nan)
    wlen_zoom_nan_clean = wlen_zoom[mask]
    flux_zoom_nan_clean = flux_zoom_nan[mask]

    # Fit a cubic spline with KNOTS knots to the data
    t = np.linspace(line_lower - DELTA, line_upper + DELTA, KNOTS)[1:-1]
    spl = interpolate.splrep(wlen_zoom_nan_clean, flux_zoom_nan_clean, t=t)
    xnew = np.linspace(line_lower - DELTA, line_upper + DELTA)
    spl_eval = interpolate.splev(xnew, spl)

    # Create a noise distribution for the regions where we now only have the spline
    spl_eval2 = interpolate.splev(wlen_zoom_nan_clean, spl)
    diff_arr = flux_zoom_nan_clean - spl_eval2
    mean = np.mean(diff_arr)
    std = np.std(diff_arr)

    # Now rebuild the spectrum - only for the emline in question, we don't alter other emlines in the vicinity.
    wlen_zoom2 = wlen_zoom[(wlen_zoom >= line_lower) & (wlen_zoom <= line_upper)]
    noise = np.random.normal(mean, std, len(wlen_zoom2))
    new_spec_sections = noise + interpolate.splev(wlen_zoom2, spl)

    final_flux = flux.copy()
    final_flux[(wlen >= line_lower) & (wlen <= line_upper)] = new_spec_sections

    if verbose:
        fig, ax = plt.subplots(3, 1, sharex=True)
        ax[0].step(wlen, flux, label="Input")
        ax[0].set_xlim([line_lower - DELTA - 200, line_upper + DELTA + 200])
        ax[0].step(wlen_zoom, flux_zoom_nan, label="Fit region")
        ax[0].plot(xnew, spl_eval, label="Spline fit", color="tab:red")
        ax[0].set_ylim(
            min(flux_zoom) - 0.1 * np.median(flux_zoom),
            max(flux_zoom) + 0.1 * np.median(flux_zoom),
        )
        ax[0].set_ylabel("Flux [arb. units]")
        ax[0].legend()

        ax[1].axhline(0, color="k", alpha=0.7, linewidth=1)
        ax[1].plot(
            wlen_zoom_nan_clean,
            diff_arr,
            "o",
            color="tab:orange",
            markersize=2,
            label="Redisuals",
        )
        ax[1].set_xlim([line_lower - DELTA - 200, line_upper + DELTA + 200])
        ax[1].set_ylabel("Flux [arb. units]")
        ax[1].legend()

        ax[2].step(wlen, flux, "tab:blue", label="Input")
        ax[2].step(wlen, final_flux, "tab:green", label="Clipped")
        ax[2].set_xlim([line_lower - DELTA - 200, line_upper + DELTA + 200])
        ax[2].set_ylim(
            min(flux_zoom) - 0.1 * np.median(flux_zoom),
            max(flux_zoom) + 0.1 * np.median(flux_zoom),
        )
        ax[2].set_xlabel("Wavelength [$\AA$]")
        ax[2].set_ylabel("Flux [arb. units]")
        ax[2].legend()

        plt.tick_params(direction="in")
        plt.show()
        if path is not None:
            fig.savefig(
                f"{path}clipping_line{int(np.mean((line_upper, line_lower)))}.pdf"
            )
        else:
            fig.savefig(f"clipping_line{int(np.mean((line_upper, line_lower)))}.pdf")
        plt.close()
    return new_spec_sections


def clip_lines(wlen, flux, emline_list, *args, **kwargs):
    """
    Iterate over the list of emission lines.
    Call clip_line to remove them.
    Use the result of clip line to update the flux_clipd vector.
    Return the clipped spectrum.

    Args:
        wlen (numpy.ndarray): Wavelength array. Taken from the input spectrum.
        flux (numpy.ndarray): Flux array. Taken from the input spectrum.
        emline_list (list): Full list of emline bounding lines.

    Returns:
        flux_clipd (numpy.ndarray): An array containing the spectrum with emission lines removed.
    """

    flux_clipd = flux.copy()
    for i in range(0, len(emline_list), 2):
        line_lower = emline_list[i]
        line_upper = emline_list[i + 1]
        new_section = clip_line(
            wlen, flux, line_lower, line_upper, emline_list, *args, **kwargs
        )
        flux_clipd[(wlen >= line_lower) & (wlen <= line_upper)] = new_section
    return flux_clipd


def main():
    data = pd.read_csv("1997ef_1998-01-28_00-00-00_Lick-3m_KAST_SUSPECT.dat", sep=",")
    wlen = data["wave"].to_numpy()
    flux = data["flux"].to_numpy()
    emlines = define_regions(wlen, flux)
    flux_clipd = clip_lines(wlen, flux, emlines, verbose=True)
    data.loc[:, "flux_clipd"] = flux_clipd

    data.to_csv(
        "1997ef_1998-01-28_00-00-00_Lick-3m_KAST_SUSPECT_clipd.dat",
        sep=",",
        na_rep="",
        index=False,
    )

    plt.figure()
    plt.plot(wlen, flux, label="Input")
    plt.plot(wlen, flux_clipd, label="Clipped", color="tab:green")
    plt.xlabel("Wavelength [$\AA$]")
    plt.ylabel("Flux [arb. units]")
    plt.xlim([min(wlen), max(wlen)])
    plt.ylim([np.percentile(flux, 5) * 0.5, 1.5 * np.percentile(flux, 95)])
    plt.legend()
    plt.tick_params(direction="in")
    plt.savefig("example.pdf")
    plt.show()


if __name__ == "__main__":
    main()
