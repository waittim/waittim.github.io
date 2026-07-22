---
layout:     post
title:      Power and Sample Size Calculations for Correlational Studies
subtitle:   Probability and Statistical Inference - 10
date:       2019-11-22
author:     Zekun Wang
header-img: img/headers/prob10-power&sample.jpg
catalog: true
dark_chart_images: invert
tags:
    - Statistics
    - Simulation
    - R
    - Correlation
---


A common research objective is to demonstrate that two measurements are highly correlated. One measurement, call it A, may reflect the severity of disease but is difficult or costly to collect. Another measurement, call it B, may be easier to collect and potentially related to measurement A. If there is a strong association between A and B, a cost-effective strategy for diagnosis may be to collect measurement B instead of A.

The researcher will collect both measurements on N individuals. The analysis will proceed by calculating a one-sided confidence interval. If the confidence interval is completely within the range from 0.8 to 1, then the researcher will consider the study to be a success: A conclusive demonstration that the correlation between A and B is greater than 0.8.

Power is the probability that the study will end in success when the true underlying correlation has a given value. The code below provides the power calculation for a single combination of N and population correlation.

```r
set.seed(1122)
suppressPackageStartupMessages(require(mvtnorm))
N <- 50
rho <- .95
null_correlation <- 0.8
R <- 5000

sigma <- array(c(1,rho,rho,1), c(2,2))
mu <- c(0,0)

detect <- rep(NA, R)
for(i in 1:R){
  data <- rmvnorm(N, mean = mu, sigma = sigma)
  results <- cor.test(x = data[,1], y = data[,2], alternative = "greater")
  detect[i] <- results$conf.int[1] > null_correlation
}
power <- mean(detect)
```

For the simulation part, we need to use correlations from 0.8 to 0.95 and the sample size from 25 to 100. Now, let's create a table to save the generated powers.

```r
corr_list <-  seq(0.8,0.95,0.01)
N_list <- seq(25,100,25)
result <- expand.grid(corr=corr_list, N = N_list, power=NA)
```

Then use a for loop to apply all the correlations and sample sizes and calculate the power values.

```r
for (j in 1:nrow(result)){
  N <- result[j,2]    #50
  rho <- result[j,1]  #.8
  null_correlation <- 0.8
  R <- 5000

  sigma <- array(c(1,rho,rho,1), c(2,2))
  mu <- c(0,0)

  detect <- rep(NA, R)
  for(i in 1:R){
    data <- rmvnorm(N, mean = mu, sigma = sigma)
    results <- cor.test(x = data[,1], y = data[,2], alternative = "greater")
    detect[i] <- results$conf.int[1] > null_correlation
  }
  power <- mean(detect)
  result[j,3] <- power
}
```

Transform the table into a data frame and plot the graph.

```r
result_df <- as.data.frame(result) %>%
  mutate(N=factor(N))

result_df %>%
  ggplot()+
  geom_line(aes(x=corr,y=power,color=N),size=1)+
  theme_bw()+
  labs(x="Correlation",y="Power")
```
![](https://i.postimg.cc/02c64Qkt/image.png)

As we can see, as N increases, the power for a given correlation also increases. In other words, when we can collect more samples, the probability that the study will end in success is higher. When the true correlation is higher, the probability is also higher.
