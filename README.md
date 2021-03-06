
![](./rfpy/examples/picture/RfPy_logo.png)

## Teleseismic receiver function calculation and post-processing 

RfPy is a software to calculate single event-station receiver functions from the spectral deconvolution technique. Methods are available to post-process the receiver function data to calculate H-k stacks and back-azimuth harmonics. The code uses the ``StDb`` package for querying and building a station database and can be used through command-line scripts.

[![Build Status](https://travis-ci.com/paudetseis/RfPy.svg?branch=master)](https://travis-ci.com/paudetseis/RfPy)
[![codecov](https://codecov.io/gh/paudetseis/RfPy/branch/master/graph/badge.svg)](https://codecov.io/gh/paudetseis/RfPy)

Installation, Usage, API documentation and scripts are described at 
https://paudetseis.github.io/RfPy/.

<!-- #### Citing

If you use `SplitPy` in your work, please cite the 
[`Zenodo DOI`](https://zenodo.org/badge/latestdoi/211722700).
 -->
#### Contributing

All constructive contributions are welcome, e.g. bug reports, discussions or suggestions for new features. You can either [open an issue on GitHub](https://github.com/paudetseis/RfPy/issues) or make a pull request with your proposed changes. Before making a pull request, check if there is a corresponding issue opened and reference it in the pull request. If there isn't one, it is recommended to open one with your rationale for the change. New functionality or significant changes to the code that alter its behavior should come with corresponding tests and documentation. If you are new to contributing, you can open a work-in-progress pull request and have it iteratively reviewed.

Examples of straightforward contributions include editing the documentation or adding notebooks that describe published examples of teleseismic receiver functions. Suggestions for improvements (speed, accuracy, flexibility, etc.) are also welcome.

#### References

- Audet, P. (2010) Temporal Variations in Crustal Scattering Structure near Parkfield, California, Using Receiver Functions, Bulletin of the Seismological Society of America (2010) 100 (3): 1356-1362. https://doi.org/10.1785/0120090299

- Tarayoun, A., P. Audet, S. Mazzotti, and A. Ashoori (2017) Architecture of the crust and uppermost mantle in the northern Canadian Cordillera from receiver functions, J. Geophys. Res. Solid Earth, 122, 5268–5287, https://doi.org/10.1002/2017JB014284.
