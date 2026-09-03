# Phase 6: The Point Process & Temporal ETAS Model

## 1. ETAS Conditional Intensity
The Epidemic-Type Aftershock Sequence (ETAS) model describes the earthquake generation process as a Hawkes point process. The conditional intensity function, given the history $H_t$ of all events up to time $t$, is (Ogata 1988, Eq. 2 and Appendix B):
$$ \lambda(t, x, y, m \mid H_t) = \mu(x, y) + \sum_{i: t_i < t} K e^{\alpha(m_i - m_0)} g(t - t_i) f(x - x_i, y - y_i; m_i) $$
Where the parameters are:
- $\mu(x, y)$: Background seismicity rate (time-independent, spatial).
- $K$: Baseline productivity (expected number of offspring from a magnitude $M_c$ event).
- $\alpha$: Productivity scaling parameter (how much more a large event triggers compared to a small one).
- $g(t)$: The normalized temporal Omori decay kernel, parameterized by $\{c, p\}$.
- $f(x, y)$: The spatial triggering kernel, often parameterized by $\{d, q\}$.
- $M_c$: The magnitude of completeness cutoff (the reference magnitude).

*(Note: In the pure temporal formulation, the spatial terms $\mu(x,y)$ and $f(\Delta x, \Delta y)$ integrate out, leaving $\lambda(t) = \mu + \sum K e^{\alpha(m_i - M_c)} g(t - t_i)$.)*

## 2. Derivation of the Modified-Omori Compensator
The normalized temporal Omori kernel is defined as:
$$ g(t) = \frac{p-1}{c} \left( 1 + \frac{t}{c} \right)^{-p} $$
To find the compensator (the expected number of events over a time window), we need the definite integral $\int_a^b g(t) dt$. Let $u = 1 + \frac{t}{c}$, then $dt = c \, du$.
$$ \int g(t) dt = \int \frac{p-1}{c} u^{-p} (c \, du) = (p-1) \int u^{-p} du $$
Integrating $u^{-p}$ for $p \neq 1$:
$$ (p-1) \left[ \frac{u^{1-p}}{1-p} \right] = -u^{1-p} = - \left( 1 + \frac{t}{c} \right)^{1-p} $$
Evaluating from $t=a$ to $t=b$:
$$ \int_a^b g(t) dt = \left( 1 + \frac{a}{c} \right)^{1-p} - \left( 1 + \frac{b}{c} \right)^{1-p} $$
*(Ogata 1988)*

## 3. Why $p > 1$ is required
The total integral of the kernel from $t=0$ to $t \to \infty$ represents the total expected fraction of aftershocks over infinite time. Evaluating the compensator bound:
$$ \lim_{t \to \infty} \left[ 1 - \left( 1 + \frac{t}{c} \right)^{1-p} \right] $$
If $p \le 1$, the exponent $1-p \ge 0$, and the limit diverges to infinity (the sequence never ends and produces infinite aftershocks). For the kernel to be a valid, finite probability density (integrating to exactly 1), we strictly require $p > 1$.

## 4. Transformed-Time Residual Analysis
In point process theory, the conditional compensator $\Lambda(t) = \int_0^t \lambda(s \mid H_s) ds$ maps the highly clustered, irregular sequence of real event times $t_i$ into a transformed time domain $\tau_i = \Lambda(t_i)$. 
According to the Time Rescaling Theorem (Ogata 1988), if the fitted model $\lambda(t)$ perfectly describes the underlying true process, the transformed times $\tau_i$ will behave exactly as a stationary, homogeneous Poisson process with rate 1. 
**Diagnostic:** This means the inter-event times in the $\tau$ domain should follow an exponential distribution $e^{-\tau}$, and the cumulative number of events plotted against $\tau$ should form a perfectly straight line with slope 1. Deviations from this (visualized via a Kolmogorov-Smirnov test on the transformed residuals) indicate mis-specified parameters or missing physics in the model.
