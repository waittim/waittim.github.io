---
layout:     post
title:      What’s the difference between Absolute Error and Relative Error?
subtitle:   Probability and Statistical Inference - 02
date:       2019-09-06
author:     Zekun Wang
description: "Compare absolute and relative error with simulations, and see when each metric better reflects estimation quality."
header-img: img/headers/prob2-error.jpeg
catalog: true
mathjax: true
dark_chart_images: invert
permalink: /2019/09/06/absolute-relative-error/
redirect_from:
  - /2019/09/06/absolute&relative-error/
  - /2019/09/06/absolute&relative-error
series: Probability and Statistical Inference
series_nav_title: Absolute vs Relative Error
series_order: 2
tags:
    - Statistics
    - Simulation
    - R
---


Absolute error and relative error are calculated in slightly different ways, but that small difference leads to an important change in interpretation. Absolute error is influenced by sample size, while relative error better reflects the scale of the error itself.

>when used as a measure of precision—is the ratio of the absolute error of a measurement to the measurement being taken. In other words, this type of error is relative to the size of the item being measured. RE is expressed as a percentage and has no units.

*From [Statistics How To](https://www.statisticshowto.datasciencecentral.com/relative-error/)*


## Absolute Error

Let $\hat{p}$ be the sample proportion from a $\mathrm{Binomial}(n,p)$ draw, and let $p$ be the true probability. Absolute error is

$$
\mathrm{AE} = \bigl|\hat{p} - p\bigr|.
$$

In the simulation below we report the Monte Carlo mean of this quantity,

$$
\overline{\mathrm{AE}} = \frac{1}{R}\sum_{r=1}^{R}\bigl|\hat{p}_r - p\bigr|,
\qquad R = 10{,}000.
$$

>The difference between the measured or inferred value of a quantity $x_0$ and its actual value $x$.


First, let's create a table to store the 14*5 simulation results.
```r
n <- rep(NA, 14)
for(i in 1:14){n[i] <- 2^(i+1)}
T <- matrix(NA,14,5)
p <- c(0.01,0.05,0.10,0.25,0.5)
```

Then we randomly generate 1s and 0s 10,000 times for each setting and calculate the absolute error.
```r
for(x in 1:length(p)){
  for(y in 1:length(n)){
    TS <- rep(NA,10000)
    for(m in 1:10000){
      TS[m] <- abs(rbinom(1,n[y],p[x])/n[y]-p[x])
    }
    T[y,x] <- mean(TS)
  }
}
```

Change the y-scale to log_10.
```r
T <- log10(T)
```

Finally, we plot the graph to show the relationship between p and absolute error.
```r
plot(T[,5],xlim=c(0,14),ylim=range(T),col="red",type="b",xaxt="n",xlab="N(log_2 scale)",ylab="Absolute Error",pch=16, lwd=3)
lines(T[,2],col="purple",type="b",pch=16, lwd=3)
lines(T[,3],col="blue",type="b",pch=16, lwd=3)
lines(T[,4],col="green",type="b",pch=16, lwd=3)
lines(T[,1],col="gray",type="b",pch=16, lwd=3)

lname <- c("0.01","0.05","0.10","0.25","0.50")
lname_p <- paste0("p = ",lname)
xname <- c("4","8","16","32","64","128","256","512","1024","2048","4096","8192","16384","32768")

axis(1, at=1:14,las=2, lab=xname)
text(1,T[1,],lname_p,pos=2,cex=0.6)
```
<img class="chart-invert" src="{{ "/img/posts/2019-09-06-absolute&relative-error/absolute-error.png" | relative_url }}" alt="Absolute error versus sample size on a log10 scale" width="1258" height="748" loading="lazy" decoding="async">

Absolute error is the absolute difference between the observed value and the expected value. In this simulation, we calculate the absolute error 10,000 times and take its mean for each setting. After transforming the y-axis to log_10, it is clear that x and y have a linear relationship. The larger p is, the larger the absolute error becomes.

# Relative Error

Relative error scales absolute error by the true probability $p$:

$$
\mathrm{RE} = \frac{\bigl|\hat{p} - p\bigr|}{p},
\qquad
\overline{\mathrm{RE}} = \frac{1}{R}\sum_{r=1}^{R}\frac{\bigl|\hat{p}_r - p\bigr|}{p}.
$$

Then we do the same thing as before, but when calculating the error, we divide the absolute error by the true probability $p$.
We plot this graph as well.

```r
n <- rep(NA, 14)
for(i in 1:14){n[i] <- 2^(i+1)}

T2 <- matrix(NA,14,5)
p <- c(0.01,0.05,0.10,0.25,0.5)

for(x in 1:length(p)){
  for(y in 1:length(n)){
    T2S <- rep(NA,10000)
    for(m in 1:10000){
      T2S[m] <- abs(rbinom(1,n[y],p[x])/n[y]-p[x])/p[x]
    }
    # T2[y,x] <- abs(rbinom(1,n[y],p[x])/n[y]-p[x])/p[x]
    T2[y,x] <- mean(T2S)
  }
}

T2 <- log10(T2)

xname <- c("4","8","16","32","64","128","256","512","1024","2048","4096","8192","16384","32768")
lname <- c("0.01","0.05","0.10","0.25","0.50")
lname_p <- paste0("p = ",lname)

plot(T2[,1],xlim=c(0,14),ylim=range(T2),col="red",type="b",pch=16,xaxt="n",xlab="N(log_2 scale)",ylab="Relative Error", lwd=3)
lines(T2[,2],col="purple",type="b",pch=16, lwd=3)
lines(T2[,3],col="blue",type="b",pch=16, lwd=3)
lines(T2[,4],col="green",type="b",pch=16, lwd=3)
lines(T2[,5],col="gray",type="b",pch=16, lwd=3)
axis(1, at=1:14,las=2, lab=xname)
text(1,T2[1,],lname_p,pos=2,cex=0.6)
```
<img class="chart-invert" src="{{ "/img/posts/2019-09-06-absolute&relative-error/relative-error.png" | relative_url }}" alt="Relative error versus sample size on a log10 scale" width="1258" height="748" loading="lazy" decoding="async">

Compared with absolute error, relative error is calculated by dividing the absolute error by p, the expected value. This process accounts for the scale of the value and focuses on the error itself. When we transform the y-axis to log_10, the x-y relationship is also linear. However, the larger p is, the smaller the relative error becomes.
