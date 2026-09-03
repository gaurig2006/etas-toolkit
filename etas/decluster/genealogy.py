import numpy as np
from etas.catalog.model import Catalog
from etas.calibrate.estep import e_step_spatial
from typing import Tuple, Dict

def compute_triggering_matrix(catalog: Catalog, 
                              params: Dict[str, float], 
                              mu_field: np.ndarray,
                              mc: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the full background probability vector and rho_ij triggering matrix
    from a calibrated ETAS model.
    
    Cites: 03 Zhuang et al. 2002, Eq. 1.
    
    Args:
        catalog: Calibrated event catalog.
        params: Fitted ETAS parameters.
        mu_field: Fitted spatial background field.
        mc: Magnitude of completeness.
        
    Returns:
        Tuple of (bg_probs, rho_matrix).
    """
    df = catalog.df.dropna(subset=["time_days", "magnitude"]).sort_values("time_days")
    t = df["time_days"].values
    x = df["longitude"].values
    y = df["latitude"].values
    m = df["magnitude"].values
    
    K = params.get("K", 0.05)
    alpha = params.get("alpha", 1.0)
    c = params.get("c", 0.05)
    p = params.get("p", 1.2)
    d = params.get("d", 1.0)
    q = params.get("q", 1.5)
    gamma = params.get("gamma", 1.0)
    
    bg_probs, rho_matrix, _ = e_step_spatial(
        t, x, y, m, mc, mu_field, K, alpha, c, p, d, q, gamma
    )
    
    return bg_probs, rho_matrix
