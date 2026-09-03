# Phase 8: Spatiotemporal ETAS & the Background Field $\mu(x,y)$

## 1. The Spatial Triggering Kernel
To extend the ETAS model to space, we introduce a spatial kernel $f(x-x_i, y-y_i; m_i)$ that describes how aftershocks are distributed around a parent event. Earthquakes scale self-similarly, so the rupture length (and thus the triggering zone) grows exponentially with the parent's magnitude.

The magnitude-dependent spatial kernel (often modeled as an isotropic power-law or Gaussian) is:
$$ f(r; m) = \frac{q-1}{\pi D(m)^2} \left( 1 + \frac{r^2}{D(m)^2} \right)^{-q} $$
where $r = \sqrt{(x-x_i)^2 + (y-y_i)^2}$ is the spatial distance, $q > 1$ controls the spatial decay, and $D(m) = d \, e^{\gamma (m - M_c)}$ is the characteristic triggering distance that scales with magnitude according to parameter $\gamma$.

**Normalization:** The kernel is explicitly normalized such that $\iint f(x, y) \, dx \, dy = 1$ over infinite 2D space. The prefactor $\frac{q-1}{\pi D(m)^2}$ ensures this integration constraint.

## 2. The Zhuang Iterative Coupling
In the purely temporal ETAS model, the background rate $\mu$ is a single scalar constant. In reality, background seismicity is highly localized along tectonic faults, so we need a 2D field $\mu(x, y)$.

Zhuang et al. (2002) introduced a powerful fixed-point iterative scheme to estimate $\mu(x,y)$ simultaneously with the ETAS parameters:
1. **Initialize:** Start with a uniform $\mu$ and run the temporal EM to get initial $\rho_{ij}$ and $bg_i$.
2. **KDE Step:** Use a 2D Kernel Density Estimator (KDE) on the event locations $(x_i, y_i)$, **weighted** by their background probabilities $bg_i$, to estimate the continuous spatial field $\mu(x,y)$.
3. **E-Step:** Recompute the triggering probabilities $\rho_{ij}$ and new background probabilities $bg_i$, this time using the spatial field $\mu(x_i, y_i)$ instead of a scalar $\mu$.
4. **M-Step:** Re-optimize the ETAS parameters given the new $\rho_{ij}$.
5. **Iterate:** Repeat steps 2-4 until the field $\mu(x,y)$ and the ETAS parameters strictly converge.

## 3. KDE Bandwidth via Likelihood Cross-Validation
The KDE requires a bandwidth parameter $h$ (which controls the smoothness of the spatial field). Helmstetter et al. (2007) prescribe using **likelihood cross-validation** to select $h$.
- We evaluate the likelihood of each event $i$ under a KDE model built from all *other* events $j \neq i$.
- We maximize the cross-validated log-likelihood: $\max_h \sum_i \log \hat{\mu}_{-i}(x_i, y_i; h)$.
- **Adaptive Bandwidth:** Because seismicity is highly clustered, a fixed bandwidth over-smooths dense faults and under-smooths empty regions. An adaptive nearest-neighbor bandwidth $h_i \propto d(i, k)$ (the distance to the $k$-th nearest neighbor) is strongly preferred.
