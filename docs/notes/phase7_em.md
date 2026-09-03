# Phase 7: EM Calibration

## 1. The Challenge of Direct MLE
The incomplete-data log-likelihood for the ETAS model over window $[0, T]$ is:
$$ \log L(\theta) = \sum_{i=1}^N \log \left( \mu + \sum_{j: t_j < t_i} \kappa(m_j) g(t_i - t_j) \right) - \Lambda(\theta) $$
where $\theta = \{\mu, K, \alpha, c, p\}$. The difficulty in maximizing this directly lies in the logarithm of a sum inside the first term. This non-linearity couples all the parameters together, preventing closed-form solutions and making the numerical optimization landscape highly non-convex with many local maxima.

## 2. Latent Parentage and Complete-Data Likelihood
To decouple the parameters, Veen & Schoenberg (2008) introduce a latent branching structure. For every event $i$, we define a latent random variable $u_i$. If $u_i = 0$, event $i$ is a background event. If $u_i = j$, event $i$ was triggered by a past event $j$. 

If we knew $u_i$ (the "complete data"), the log-likelihood $Q(\theta)$ would factorize beautifully into separate sums:
$$ Q(\theta) = - \mu T + \sum_{i: u_i = 0} \log \mu - \sum_j I_j(\theta_{trig}) + \sum_{i: u_i = j} \log(\kappa(m_j) g(t_i - t_j)) $$
where $I_j$ is the integrated compensator for event $j$'s aftershock sequence.

## 3. The Expectation Step (E-step)
Since we don't actually know $u_i$, we compute its expected value given the current parameter estimates $\hat{\theta}$. This gives the posterior probabilities:
- Background probability for event $i$: 
  $$ bg_i = P(u_i = 0 \mid H_{t_i}, \hat{\theta}) = \frac{\hat{\mu}}{\lambda(t_i \mid \hat{\theta})} $$
- Triggering probability (event $j$ triggered event $i$): 
  $$ \rho_{ij} = P(u_i = j \mid H_{t_i}, \hat{\theta}) = \frac{\hat{\kappa}(m_j) \hat{g}(t_i - t_j)}{\lambda(t_i \mid \hat{\theta})} $$
By definition, these probabilities must sum to 1 for every event $i$:
$$ bg_i + \sum_{j: t_j < t_i} \rho_{ij} = 1 $$

## 4. The Maximization Step (M-step)
We substitute these expectations back into the complete-data log-likelihood and maximize with respect to $\theta$. Because the parameters are decoupled, we get closed-form updates for some parameters:
- **$\mu$ update:** $\hat{\mu} = \frac{\sum_i bg_i}{T}$
- **$K$ update:** $\hat{K} = \frac{\sum_{i>j} \rho_{ij}}{\sum_j e^{\alpha(m_j - M_c)} \int g(t) dt}$
- **$\alpha$ update:** Found by setting the derivative of the $Q$ function with respect to $\alpha$ to zero (often solved via a 1D root-finding method like Newton-Raphson or Brent's method). Veen & Schoenberg provide the equation:
  $$ \sum_{i>j} \rho_{ij} (m_j - M_c) - \hat{K} \sum_j (m_j - M_c) e^{\alpha(m_j - M_c)} \int g(t) dt = 0 $$
- **$c$ and $p$ updates:** No closed-form solution exists. They are found by numerically maximizing their specific terms in the $Q$-function using bounded optimization algorithms.

## 5. Approximate M-step vs. Full GEM
Veen & Schoenberg (2008) present "Algorithm 3", which employs an approximate M-step. Instead of numerically solving for $c$ and $p$ by exactly maximizing the $Q$-function at every step, they take a single Newton-Raphson step or use a simplified proxy gradient. 
However, an exact Generalized EM (GEM) variant utilizes `scipy.optimize.minimize` (or equivalent) to strictly maximize the $c, p$ sub-objective within the M-step. This guarantees strict monotonicity of the overall log-likelihood at every iteration, whereas the approximate step can sometimes cause small oscillations or divergence if the approximation drifts too far from the true maximum. We implement the strictly monotone GEM variant to ensure stability.
