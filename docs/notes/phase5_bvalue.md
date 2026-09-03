# Phase 5: b-value Statistics

This document compares the least-squares approach to estimating the $b$-value of the Gutenberg-Richter distribution with the Aki-Utsu Maximum Likelihood Estimator (MLE), and explains the Shi & Bolt (1982) standard error.

## 1. Least-Squares vs. Maximum Likelihood Estimator (MLE)

### Least-Squares (Linear Regression)
Historically, the $b$-value was often estimated by plotting the log of the cumulative frequency of earthquakes against magnitude and fitting a straight line using ordinary least squares (OLS) regression:
$$ \log_{10} N(\ge M) = a - bM $$
**Why it is biased:** OLS assumes that the variance of the residuals is constant (homoscedasticity) and that the data points (the bins) are independent. Neither is true for the cumulative Gutenberg-Richter distribution. The cumulative counts are highly correlated (the count for $M=3.0$ includes all events from $M=4.0$), and the variance is vastly different for large bins vs. small bins. This leads to heavy bias, causing OLS to systematically misestimate the true slope.

### Aki-Utsu MLE
Aki (1965) and Utsu (1965) derived the Maximum Likelihood Estimator for the $b$-value, assuming earthquake magnitudes follow an exponential distribution above a threshold $M_c$. 
$$ b = \frac{\log_{10}(e)}{\langle M \rangle - (M_c - \Delta M_{bin} / 2)} $$
where $\langle M \rangle$ is the mean magnitude of all events $\ge M_c$, and $\Delta M_{bin}$ is the bin width (typically 0.1).
**Why it is better:** The MLE approach rigorously models the underlying statistical probability of the magnitudes without the flawed assumptions of OLS. It is statistically unbiased for large samples, computationally simpler (no matrix inversion), and vastly more robust.

## 2. Standard Error of the b-value: Proof of Shi & Bolt (1982)
While Aki (1965) provided an asymptotic standard error estimate ($b / \sqrt{N}$), Shi & Bolt (1982) proved a more robust formula that accounts for the sample variance of the magnitudes directly.

**Proof:**
By definition, the Aki MLE for $b$ is:
$$ b = \frac{\log_{10}(e)}{\langle M \rangle - M_c} $$
Using first-order Taylor expansion (error propagation), the variance of $b$ as a function of the mean magnitude $\langle M \rangle$ is:
$$ \text{Var}(b) \approx \left( \frac{\partial b}{\partial \langle M \rangle} \right)^2 \text{Var}(\langle M \rangle) $$

First, compute the derivative of $b$ with respect to $\langle M \rangle$:
$$ \frac{\partial b}{\partial \langle M \rangle} = -\frac{\log_{10}(e)}{(\langle M \rangle - M_c)^2} $$
Substituting the definition of $b$, this simplifies to:
$$ \frac{\partial b}{\partial \langle M \rangle} = -b \left( \frac{1}{\langle M \rangle - M_c} \right) = -b \left( \frac{b}{\log_{10}(e)} \right) = - \frac{b^2}{\log_{10}(e)} $$
Since $1/\log_{10}(e) = \ln(10) \approx 2.30$, we have:
$$ \left( \frac{\partial b}{\partial \langle M \rangle} \right)^2 \approx (2.3 b^2)^2 $$

Next, substitute the standard unbiased sample variance for the mean magnitude $\langle M \rangle$:
$$ \text{Var}(\langle M \rangle) = \frac{\sum (M_i - \langle M \rangle)^2}{N(N-1)} $$

Combining these yields the variance of $b$:
$$ \text{Var}(b) \approx (2.3 b^2)^2 \left[ \frac{\sum (M_i - \langle M \rangle)^2}{N(N-1)} \right] $$
Taking the square root gives the Shi & Bolt (1982) standard error:
$$ \delta b = 2.3 b^2 \sqrt{ \frac{\sum (M_i - \langle M \rangle)^2}{N(N-1)} } $$

This standard error metric correctly penalizes small sample sizes and widely dispersed magnitude measurements, offering a much more realistic confidence bound than the purely asymptotic formula.
