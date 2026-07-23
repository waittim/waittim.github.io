---
layout:     post
title:      Coverage Probability of MLE
subtitle:   Probability and Statistical Inference - 07
date:       2019-10-15
author:     Zekun Wang
description: "Examine the coverage probability of maximum-likelihood confidence intervals through simulation."
header-img: img/headers/prob7-coverage.jpg
catalog: true
mathjax: true
dark_chart_images: invert
series: Probability and Statistical Inference
series_nav_title: Coverage Probability
series_order: 6
tags:
    - Statistics
    - Simulation
    - R
    - MLE
---



# Introduction

>In statistics, maximum likelihood estimation (MLE) is a method of estimating the parameters of a probability distribution by maximizing a likelihood function, so that under the assumed statistical model the observed data is most probable. The point in the parameter space that maximizes the likelihood function is called the maximum likelihood estimate. The logic of maximum likelihood is both intuitive and flexible, and as such the method has become a dominant means of statistical inference.
*From [Wikipedia - Maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation)*

Given i.i.d. observations $x_1,\ldots,x_n$ from a density $f(x\mid\theta)$, the MLE is

$$
\hat\theta
=
\arg\max_{\theta}\, L(\theta)
=
\arg\max_{\theta}\, \prod_{i=1}^{n} f(x_i\mid\theta)
=
\arg\min_{\theta}\,
\bigl(-\sum_{i=1}^{n}\log f(x_i\mid\theta)\bigr).
$$

Under a normal model, $\hat\theta=(\hat\mu,\hat\sigma)$ defines the plugged-in distribution $F_X^{\mathrm{mle}}=N(\hat\mu,\hat\sigma^2)$. The interval for the median constructed below is a **parametric bootstrap / plug-in** interval: draw replicates from $F_X^{\mathrm{mle}}$, compute their sample medians, and take empirical quantiles of that sampling distribution. Coverage probability is an important operating characteristic of methods for constructing interval estimates, particularly confidence intervals. For a nominal $95\%$ CI of a parameter $\theta_0$,

$$
\mathrm{Coverage}
=
P\bigl(\theta_0 \in [\ell,u]\bigr).
$$

The goal of this post is to perform a simulation to calculate the coverage probability of the $95\%$ confidence interval of the median when computed from $F_X^{\mathrm{mle}}$. For $N(\mu,\sigma^2)$, the MLE of $\mu$ is the sample mean; the MLE of $\sigma$ uses divisor $n$, while R's `sd()` uses $n-1$. Step 1 below calls `stats4::mle`; the repeated experiments in Step 4 use `mean` / `sd` as a close plug-in (for large $N$ the $\sigma$ difference is negligible).

```r
library(stats4)
library(tidyverse)
```

# Step 1: Single sample
**Generate a single sample from a standard normal distribution of size N = 201.**

First, let’s set the sample size (N) to 201 and create a sample from a standard normal distribution.
```r
N <- 201
sample1 <- rnorm(201)
median(sample1)
```

Then use the MLE function we learned before.
```r
nll <- function(mean, sd) {
  fs <- dnorm(sample1,
              mean = mean,
              sd = sd,
              log = TRUE)
  - sum(fs, na.rm = T)
}

fit <- stats4::mle(
  nll,
  start = list(mean = 0, sd = 1),
  method = "L-BFGS-B",
  lower = c(0, 0.01)
)
```

From the MLE result, we can get the estimated mean and standard deviation of the sample distribution above.
```r
coef(fit)
sample1_mean <- coef(fit)[[1]]
sample1_sd <- coef(fit)[[2]]
```
The estimated mean is `sample1_mean` and the estimated standard deviation is `sample1_sd`.

# Step 2: Approximate median distribution
**Approximate the sampling distribution of the median, conditional on the estimate of the distribution in the previous step.**

In the previous step, we get a pair of estimated values for the mean and standard deviation. Based on these parameters, we can generate new distributions to simulate the original distribution.

Now we need to get the median of the new distribution. If we repeat the process many times, we can get the sampling distribution of the median for the estimated distribution.
```r
median_list <- rep(NA, 500)
for (i in seq_along(median_list)) {
  median_list[i] <-
    median(rnorm(N, mean = sample1_mean, sd = sample1_sd))
}
#hist(median_list,breaks = 100)
```


# Step 3: Calculate 95% CI
**Calculate a 95% confidence interval from the approximated sampling distribution.**

For the median distribution we got in the previous step, we can use the *quantile()* function to get the 95% confidence interval.
```r
sample1_quantile95 <- quantile(median_list, c(0.025, 0.975))
sample1_quantile95
```


# Step 4: Calculate coverage probability
**Now we will explain the concept of coverage probability and calculate it.**

First, create a matrix to save the distributions we are going to generate. Each column is one distribution. Then use the method from the previous steps to generate all the distributions.
```r
samples <- matrix(nrow = N, ncol = 1000)
for (i in 1:ncol(samples)) {
  samples[, i] <- rnorm(N)
}
```

Now create a matrix to save the estimated parameters of each distribution. Here `mean` / `sd` stand in for the normal plug-in parameters discussed above.
```r
coef <- matrix(nrow = 2, ncol = ncol(samples))
for (i in 1:ncol(samples)) {

  coef[1, i] <- mean(samples[, i]) #coef(fit)[[1]]
  coef[2, i] <- sd(samples[, i]) #coef(fit)[[2]]

}
```

Now create a matrix to save the 95% confidence intervals.
```r
quantile95_list <- matrix(nrow = 2, ncol = ncol(samples))
```

For each pair of estimated parameters, create an estimated distribution and then get the median. Repeat this process `N` times, calculate the 95% confidence interval, and save the interval in the matrix.
```r
for (j in 1:ncol(samples)) {
  median_list <- rep(NA, N)
  for (i in seq_along(median_list)) {
    norm_dist <- rnorm(N, mean = coef[1, j], sd = coef[2, j])
    median_list[i] <- median(norm_dist)
  }
  quantile95 <- quantile(median_list, c(0.025, 0.975))
  quantile95_list[1, j] <- quantile95[[1]]
  quantile95_list[2, j] <- quantile95[[2]]

}
```

To calculate the coverage probability, we can save all the judgment results in a vector. With true median $\theta_0=0$ for the standard normal, an interval $[\ell_j,u_j]$ “covers” when $\ell_j \le 0 \le u_j$. The Monte Carlo coverage estimate is

$$
\widehat{\mathrm{Coverage}}
=
\frac{1}{M}\sum_{j=1}^{M}
\mathbf{1}\{\ell_j \le 0 \le u_j\}.
$$
```r
interest <- rep(NA, ncol(samples))
for (i in seq_along(interest)) {
  interest[i] <-
    case_when(
      quantile95_list[1, i] > 0 | quantile95_list[2, i] < 0 ~ 0,
      quantile95_list[1, i] <= 0 &
        quantile95_list[2, i] >= 0 ~ 1,
    )
}
coverage_probability <- sum(interest) / length(interest)
sum(interest)
coverage_probability
```
This time, the coverage probability is `coverage_probability`.

```r
sum(quantile95_list[2,] < 0)
sum(quantile95_list[1,] > 0)

```

# Step 5: Simulation visualization
**Perform the simulation.**

To make the results more intuitive, we can use the *geom_linerange()* function in *ggplot* to draw the 95% confidence interval. We set the intervals that did not capture the true median of the original distribution, 0, as red lines.
```r
quantile95_df <- as.data.frame(t(quantile95_list))
quantile95_df["sample_num"] <- seq(1:ncol(samples))
quantile95_df["interest"] <- interest
ggplot(quantile95_df) +
  geom_linerange(aes(x = sample_num,
                     ymin = V1,
                     ymax = V2),
                 color = case_when(interest == 1 ~ "blue",
                                   interest == 0 ~ "red")) +
  geom_hline(yintercept = 0,
             color = "gray",
             alpha = 0.7) +
  coord_flip() +
  theme_bw()
```
<img class="chart-invert" src="{{ "/img/posts/2019-10-15-coverage-probability/coverage-intervals.png" | relative_url }}" alt="Ninety-five percent confidence intervals for the median; rust intervals miss zero" width="1128" height="1420" loading="lazy" decoding="async">

# Step 6: Future work
**How to change the simulation to learn more about the operating characteristics of the chosen method for constructing the 95% confidence interval.**

I would choose larger sample sizes to test the process, for example by setting N to 5000 or 10000. I could also calculate other quantiles of the distributions to see whether there are any differences. After that, I might use distributions other than the standard normal distribution, such as gamma or beta distributions.
