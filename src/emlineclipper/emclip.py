'''
Take an input wavelength and flux.
Ask the user to choose the regions to clip.
Define a region in which to perform fiting.
Compute spline fit using data in the fitting region.
Produce the difference spectrum between the spline and the original spectrum in the fitting region.
Compute the mean and variance of this region.
Sample from this distribution to create the noise for the clip region.
Add noise to the spline in the clip region.
Assign the new spectrum in the clip region to the orignal spectrum.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

DELTA = 100
KNOTS = 5

def click_regions(event, fig, ax, emlines):
    if event.dblclick:
        if event.button == 3:
            if len(plt.gca().lines)>1:
                plt.gca().lines[-1].remove()
                fig.canvas.draw()
                emlines.pop(-1)

        if event.button == 1:
            ax.axvline(event.xdata, color='tab:pink')
            fig.canvas.draw()
            emlines.append(event.xdata)

def define_regions(wlen, flux):
    emlines = []

    fig, ax = plt.subplots()
    ax.plot(wlen, flux)
    fig.canvas.mpl_connect('button_press_event', lambda event: click_regions(event, fig, ax, emlines))
    plt.show()

    return emlines


def clip_lines(wlen, flux, emline_list, *args, **kwargs):
    for i in range(0, len(emline_list), 2):
        line_lower = emline_list[i]
        line_upper = emline_list[i+1]
        flux = clip_line(wlen, flux, line_lower, line_upper, *args, **kwargs)

    return flux

def clip_line(wlen, flux, line_lower, line_upper, verbose=False, path=None):



    # Zoom in to DELTA angstroms either side of the line.
    wlen_zoom = wlen[(wlen>line_lower-DELTA) & (wlen<line_upper+DELTA)]
    flux_zoom = flux[(wlen>line_lower-DELTA) & (wlen<line_upper+DELTA)]

    flux_zoom_nan = flux_zoom.copy()
    flux_zoom_nan[(wlen_zoom>line_lower) & (wlen_zoom<line_upper)] = np.nan

    mask = ~np.isnan(flux_zoom_nan)
    wlen_zoom_nan_clean = wlen_zoom[mask]
    flux_zoom_nan_clean = flux_zoom_nan[mask]



    # Fit a cubic spline with KNOTS knots to the data
    t = np.linspace(line_lower-DELTA, line_upper+DELTA, KNOTS)[1:-1]
    spl = interpolate.splrep(wlen_zoom_nan_clean, flux_zoom_nan_clean, t=t)
    xnew = np.linspace(line_lower-DELTA, line_upper+DELTA)
    spl_eval = interpolate.splev(xnew, spl)


    # Create a noise distribution for the regions where we now only have the spline
    spl_eval2 = interpolate.splev(wlen_zoom_nan_clean, spl)
    diff_arr = flux_zoom_nan_clean-spl_eval2
    mean = np.mean(diff_arr)
    std = np.std(diff_arr)



    # Now rebuild the spectrum
    noise = np.random.normal(mean, std, np.isnan(flux_zoom_nan).sum())
    inverse_mask = np.isnan(flux_zoom_nan)
    new_spec_sections = noise+interpolate.splev(wlen_zoom[inverse_mask], spl)

    new_flux = flux_zoom_nan.copy()
    new_flux[(mask==False)] = new_spec_sections

    final_flux = flux.copy()
    final_flux[(wlen>line_lower-DELTA) & (wlen<line_upper+DELTA)] = new_flux


    if verbose:
        fig, ax = plt.subplots(3, 1, sharex=True)
        ax[0].step(wlen, flux, label='Input')
        # ax[0].plot(wlen_zoom, flux_zoom, label='Emission line')
        ax[0].set_xlim([line_lower-DELTA-200, line_upper+DELTA+200])
        ax[0].step(wlen_zoom, flux_zoom_nan, label='Fit region')
        ax[0].plot(xnew, spl_eval, label='Spline fit', color='tab:red')
        ax[0].set_ylim(min(flux_zoom)-0.1*np.median(flux_zoom), max(flux_zoom)+0.1*np.median(flux_zoom))
        ax[0].set_ylabel('Flux [arb. units]')
        ax[0].legend()

        ax[1].axhline(0, color='k', alpha=0.7, linewidth=1)
        ax[1].plot(wlen_zoom_nan_clean, diff_arr, 'o', color='tab:orange', markersize=2, label='Redisuals')
        ax[1].set_xlim([line_lower-DELTA-200, line_upper+DELTA+200])
        ax[1].set_ylabel('Flux [arb. units]')
        ax[1].legend()

        ax[2].step(wlen, flux, 'tab:blue', label='Input')
        ax[2].step(wlen, final_flux, 'tab:green', label='Clipped')
        ax[2].set_xlim([line_lower-DELTA-200, line_upper+DELTA+200])
        ax[2].set_ylim(min(flux_zoom)-0.1*np.median(flux_zoom), max(flux_zoom)+0.1*np.median(flux_zoom))
        ax[2].set_xlabel('Wavelength [$\AA$]')
        ax[2].set_ylabel('Flux [arb. units]')
        ax[2].legend()

        plt.show()
        if path is not None:
            fig.savefig(f'{path}clipping_line{int(np.mean((line_upper, line_lower)))}.pdf')
        else:
            fig.savefig(f'clipping_line{int(np.mean((line_upper, line_lower)))}.pdf')
        plt.close()
    return final_flux

def main():
    data = pd.read_csv('SN1997ef_1997-12-29_07-12-00_FLWO-1.5m_FAST_CfA-Stripped.flm', sep='\t')
    wlen = data['#wave'].to_numpy()
    flux = data['flux'].to_numpy()
    emlines = define_regions(wlen, flux)
    new_flux = clip_lines(wlen, flux, emlines)

    plt.figure()
    plt.plot(wlen, flux, label='Input')
    plt.plot(wlen, new_flux, label='Clipped', color='tab:green')
    plt.xlabel('Wavelength [$\AA$]')
    plt.ylabel('Flux [arb. units]')
    plt.xlim([min(wlen), max(wlen)])
    plt.ylim([np.percentile(flux, 5)*0.5, 1.5*np.percentile(flux, 95)])
    plt.legend()
    plt.show()

if __name__=='__main__':
    main()