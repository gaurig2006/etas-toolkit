# Phase 4: Magnitude of Completeness (Mc)

This document explains the MAXC and GFT methods for estimating the Magnitude of Completeness ($M_c$) as outlined in Wiemer and Wyss (2000), and discusses why corrections are necessary.

## 1. Maximum Curvature (MAXC)
The MAXC method estimates $M_c$ as the magnitude bin with the highest number of events in the non-cumulative frequency-magnitude distribution (FMD). Essentially, it identifies the peak of the histogram of earthquake magnitudes.
- **Advantages:** It is computationally extremely fast and stable, making it ideal for large spatial grids or sliding window analyses.
- **The Problem:** Wiemer and Wyss (2000) show that MAXC consistently underestimates $M_c$. The peak of the FMD represents the point where detection capability begins to drop off rapidly, but the catalog is often already partially incomplete immediately above this peak due to network heterogeneity or temporary outages.

### The +0.2 Correction (F-score patch)
To mitigate the underestimation inherent in MAXC while retaining its computational speed, researchers often apply a bulk correction factor. Based on empirical comparisons with more robust methods (like GFT), adding $+0.2$ to the MAXC estimate provides a much safer, more conservative estimate of $M_c$ that ensures the data strictly follows the Gutenberg-Richter power law. 

## 2. Goodness-of-Fit Test (GFT)
The GFT method evaluates how well the observed FMD matches a synthetic Gutenberg-Richter distribution. 
- For a given assumed $M_c$ cutoff, the $a$ and $b$ values are estimated (typically via Maximum Likelihood).
- A synthetic power-law distribution is generated.
- The Goodness-of-Fit ($R$) is calculated by comparing the absolute differences between the observed number of events ($B_i$) and the synthetic number ($S_i$) in each magnitude bin:
  $$ R = 100 - \left( \frac{\sum |B_i - S_i|}{\sum B_i} \right) \times 100 $$
- The algorithm tests progressively higher cutoff magnitudes. The true $M_c$ is defined as the lowest magnitude bin where $R \ge 90\%$ (or $95\%$).

**Advantages vs MAXC:** GFT is much more robust and physically motivated than MAXC because it explicitly tests for power-law behavior. However, it is computationally much heavier, making it slower for dense spatial grid mapping compared to the simple MAXC + 0.2 heuristic.
