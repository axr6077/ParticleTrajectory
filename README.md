# Tracing object path in a Black hole orbit
Study of the GRS1915+105 BHXRB system to trace an arbitrary object around this particular BH. The simulation is based on Schwarzschild geodesic ODEs and integrating them around several parameters. The path is realistic and based on real time data collected from GRANAT data releases. The accretion disk is defined by the predictive model of X-ray light curves classifiers determined through various deep learning models. 

## Parameters
The parameters defined for modelling the simulation is derived from backend tools and machine learning algorithms as presented in 

## Requirements
* Chrome/Firefox/Microsoft Edge
* Considerable GPU power for 30+ fps

## Validation
Based on real spectral data and predictive models with external parameters affecting orbit. It considers superluminal speeds as well. It doesn't consider presence of dark matter yet. The entity is a stellar mass BH hence validating the visual GR model. 

## Factors to consider
* Texture sampling issues might affect star brightness instability
* Light paths may tend to bend a bit more than they should due to low ODE solver step counts, however, this seems to happen in a systematic way so that the image looks very similar in comparison to a more accurate simulation.

## Contributions and License
Feel free to create PR. Licensed under MIT license [available here](https://github.com/axr6077/ParticleTrajectory/blob/master/LICENSE). 
