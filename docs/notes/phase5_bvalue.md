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

## 2. Standard Error of the b-value
While Aki (1965) provided an asymptotic standard error estimate ($b / \sqrt{N}$), Shi & Bolt (1982) proved a more robust formula that accounts for the sample variance of the magnitudes directly:
$$ \delta b = 2.3 b^2 \sqrt{ \frac{\sum (M_i - \langle M \rangle)^2}{N(N-1)} } $$
where $N$ is the number of events $\ge M_c$. This standard error metric correctly penalizes small sample sizes and widely dispersed magnitude measurements, offering a much more realistic confidence bound on the calculated $b$-value compared to naive approaches.
