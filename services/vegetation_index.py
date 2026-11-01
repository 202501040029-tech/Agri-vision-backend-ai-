import numpy as np

def calculate_ndvi(red_band, nir_band):
    """Calculate NDVI only from aligned red and NIR arrays; RGB photos are not accepted."""
    if red_band is None or nir_band is None:
        raise ValueError('True NDVI requires both red and near-infrared bands; ordinary RGB photos are insufficient.')
    red=np.asarray(red_band,dtype=float); nir=np.asarray(nir_band,dtype=float)
    if red.shape != nir.shape: raise ValueError('Red and NIR bands must have matching dimensions.')
    denom=nir+red
    return np.divide(nir-red,denom,out=np.zeros_like(denom),where=denom!=0)
