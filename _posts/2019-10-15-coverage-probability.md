---
layout:     post
title:      Coverage probability of MLE
subtitle:   Probability and Statistical Inference - 07
date:       2019-10-15
author:     Zekun
header-img: img/prob7-coverage.jpg
catalog: true
tags:
    - Probability
    - Simulation
    - R
    - MLE
---



# Introduction

>In statistics, maximum likelihood estimation (MLE) is a method of estimating the parameters of a probability distribution by maximizing a likelihood function, so that under the assumed statistical model the observed data is most probable. The point in the parameter space that maximizes the likelihood function is called the maximum likelihood estimate. The logic of maximum likelihood is both intuitive and flexible, and as such the method has become a dominant means of statistical inference.
*From [Wikipedia - Maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation)*

Coverage probability is an important operating characteristic of methods for constructing interval estimates, particularly confidence intervals.

The destination of this blog is that performing a simulation to calculate the coverage probability of the 95% confidence interval of the median when computed from F<sub>X</sub><sup>mle</sup>.

```{r}
library(stats4)
library(tidyverse)
```

# Step 1: Single sample
**Generate a single sample from a standard normal distribution of size N = 201.**

Fisrt, let's set the size of distribution (N) as 201, and create a standard normal distribution as sample.
```{r}
N <- 201
sample1 <- rnorm(201)
median(sample1)
```

Then use the MLE function we learned before.
```{r}
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

By the result of MLE, we can get the estimated mean and standard deviation of the sample distribution before.
```{r}
coef(fit)
sample1_mean <- coef(fit)[[1]]
sample1_sd <- coef(fit)[[2]]
```
The estimated mean is `r sample1_mean` and the estimated standard deviation is `r sample1_sd`.

# Step 2: Approximate median distribution
**Approximate the sampling distribution of the median, conditional on the estimate of the distribution in the previous step.**

In the previous step, we get a pair of estimated mean and standard deviation. Based on the parameter, we can generate new distributions to simulate the original distribution.

Now we need to get the median of the new distribution, and if repeat the process for lots of time, we can get the distribution of median of the estimated distribution.
```{r}
median_list <- rep(NA, 500)
for (i in seq_along(median_list)) {
  median_list[i] <-
    median(rnorm(N, mean = sample1_mean, sd = sample1_sd))
}
#hist(median_list,breaks = 100)
```


# Step 3: Calculate 95% CI
**Calculate a 95% confidence interval from the approximated sampling distribution.**

For the median distribution we got in the previous step, we can use *quantile()* function to get the 95% confidence interval.
```{r}
sample1_quantile95 <- quantile(median_list, c(0.025, 0.975))
sample1_quantile95
```


# Step 4: Calculate coverage probability
**Now we will explain the concept of coverage probability. And calculating the coverage probability.**

First, create a matrix to save the distributions we are going to generate. Every column is one distribution. Than use the method in the previous steps, generate all of the distributions.
```{r}
samples <- matrix(nrow = N, ncol = 1000)
for (i in 1:ncol(samples)) {
  samples[, i] <- rnorm(N)
}
```

Now create a matrix to save the estimated parameters of each distribution.
```{r}
coef <- matrix(nrow = 2, ncol = ncol(samples))
for (i in 1:ncol(samples)) {

  coef[1, i] <- mean(samples[, i]) #coef(fit)[[1]]
  coef[2, i] <- sd(samples[, i]) #coef(fit)[[2]]

}
```

Now create a matrix to save 95% confidence interval.
```{r}
quantile95_list <- matrix(nrow = 2, ncol = ncol(samples))
```

For each pair of estimated parameters, create a eatimated distribution, than get the median number. Than also do the process for `r N` times, get the 95% confidence interval and save them in the matrix.
```{r}
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

For calculating the coverage probability, we can save all of the results of judgement in a vector. Definitely, the coverage probability is the number of successful capture divede by the number of distribution.
```{r}
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
 This time, the coverage probability is `r coverage_probability`.

```{r}
sum(quantile95_list[2,] < 0)
sum(quantile95_list[1,] > 0)

```

# Step 5: Simulation visualization
**Perform the simulation.**

In order to make the results more intuitive, we can use *geom_linerange()* function in *ggplot* to draw the 95% confidence interval. And set the 95% confidence interval which did not capture the real mean of original distribution, "0" as a red line.
```{r}
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
![](https://i.postimg.cc/9MPrGHm9/prob7-1.png)

# Step 6: Future works
**How to change the simulation to learn more about the operating characteristics of the chosen method for constructing the 95% confidence interval.**

I think I will choose to use bigger distribution to test the process, likes set the *N* as 5000 or 10000. And I could calculate the other quantile of the distributions to find out is there any different. After that, maybe I will use other distribution but not standard normal distribution, such as gamma or beta distribution.
