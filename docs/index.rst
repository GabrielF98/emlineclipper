.. emlineclipper documentation master file, created by
   sphinx-quickstart on Thu Nov 21 15:02:05 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

emlineclipper
=============

.. |GitHub Release| image:: https://img.shields.io/github/v/release/GabrielF98/emlineclipper?color=teal
   :alt: GitHub Release

.. |Publish with PyPI| image:: https://github.com/GabrielF98/emlineclipper/actions/workflows/python-publish.yml/badge.svg
   :target: https://github.com/GabrielF98/emlineclipper/actions/workflows/python-publish.yml
   :alt: Publish with PyPI

|GitHub Release| |Publish with PyPI|

Python library to clip emission lines in supernova spectra. Developed by Gabriel Finneran at University College Dublin, Ireland. 

A brief description of the tool is given here. Full documentation is available at `readthedocs <https://emlineclipper.readthedocs.io/en/latest/>`_. Further information may be found in `Finneran et al. (2024) <https://arxiv.org/abs/2411.11503>`_ (see below for how to cite this work!).

This package can be installed from `PyPI <https://pypi.org/project/emlineclipper/>`_ using pip:

.. code-block:: bash

    pip install emlineclipper


The source code can be found on `GitHub <https://github.com/GabrielF98/emlineclipper>`_. Issues can be logged `here <https://github.com/GabrielF98/emlineclipper/issues>`_.

You can also contact me at `by email <mailto:gabfin15@gmail.com>`_.

.. image:: _static/example.png
  :width: 794
  :alt: Example of emission line removal.

.. image:: _static/example1.png
   :width: 794
   :alt: Example of emission line removal.

Spectra of SN1997ef from the Weizmann Interactive Supernova Data Repository `WISeREP <https://www.wiserep.org/object/4567>`_.

How to cite this code in your work
----------------------------------
If you use emlineclipper in your work, please consider citing `Finneran et al. (2024) <https://arxiv.org/abs/2411.11503>`_ (see below for bibtex). I would also appreciate if you could add an acknowledgement such as:

.. code-block:: latex

   To remove emission lines from supernova spectra, 
   this work has made use of \texttt{emlineclipper}, 
   developed by Gabriel Finneran and available at: 
   \url{https://github.com/GabrielF98/emlineclipper}.
   
.. code-block:: bibtex

   @article{2024arXiv241111503F,
         author = {{Finneran}, Gabriel and {Cotter}, Laura and {Martin-Carrillo}, Antonio},
         title = "{Velocity evolution of broad-line Ic supernovae with and without gamma-ray bursts}",
         journal = {arXiv e-prints},
      keywords = {Astrophysics - High Energy Astrophysical Phenomena},
            year = 2024,
         month = nov,
            eid = {arXiv:2411.11503},
         pages = {arXiv:2411.11503},
   archivePrefix = {arXiv},
         eprint = {2411.11503},
   primaryClass = {astro-ph.HE},
         adsurl = {https://ui.adsabs.harvard.edu/abs/2024arXiv241111503F},
         adsnote = {Provided by the SAO/NASA Astrophysics Data System},
   }

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   example
   api
