---
layout:     post
title:      Simulation Method Comparison
subtitle:   Probability and Statistical Inference - 08
date:       2019-10-27
author:     Zekun Wang
header-img: img/headers/prob8-simulation.jpg
catalog: true
tags:
    - Probability
    - Statistics
    - Simulation
    - R
    - Method of Moments
    - KDE
    - Bootstrap
---



# Situation Description

This time, I will perform a 2 × 4 × 2 factorial simulation study to compare the coverage probability of various methods of calculating **90%** confidence intervals. The three factors in the experiment are:

1.  True, underlying distribution
    -   standard normal
    -   gamma(shape = 1.4, scale = 3)
2.  Model
    -   method of moments with normal
    -   method of moments with gamma
    -   kernel density estimation
    -   bootstrap
3.  Parameter of interest
    -   sample min (1st order statistic)
    -   median
Other settings in the experiment that will not change are:
-   Sample size, *N* = 201
-   *Outside the loop* estimation

# Define functions

## Data generation function

Set up a data-generation function that can generate data from either a normal distribution or a gamma distribution. The distribution is defined by the parameter “dist”. The default parameters of the gamma distribution are shape=1.4 and scale=3.

```r
generate_data <- function(N, dist, sh=1.4, sc=3){
  if(dist=="norm"){
    rnorm(N)
  }else if(dist=="gamma"){
    rgamma(N, shape=sh, scale=sc)
  }
}
```


## Confidence interval estimation function

Then define the function for calculating the confidence interval. It can estimate the distribution by the method of moments with a normal distribution, the method of moments with a gamma distribution, kernel density estimation, or bootstrap. At the same time, the function can use the function defined by “par.int” to calculate the parameter we want. The details are introduced in the chunk.
```r
estimate.ci <- function(data, mod, par.int, R=10, smoo=0.3){
  # data: input data
  # mod: define the estimation method and the distribution.
  #      (MMnorm: method of moment with normal distribution,
  #       MMgamma: method of moment with gamma distribution,
  #       KDE: kernel density distribution,
  #       Boot: bootstrap)
  # par.int: the function that can get the parameter we want for the estimated distribution

  N <- length(data) # save N as the number of the inputted data
  sum.measure <- get(par.int) # make a character value usable as a function


  if(mod=="MMnorm"){
    # use the method of moments with a normal distribution to estimate

    mm.mean <- mean(data) # get the original mean of data
    mm.sd <- sd(data) # get the original standard deviation of data

    samp.dist <- NA #
    for(i in 1:R){
      sim.data <-rnorm(length(data), mm.mean, mm.sd)
      # use the mean & sd of data to generate a new normal distribution
      if(par.int=="median"){
        samp.dist[i] <- median(sim.data)
        # save the median of generated distribution
      }else if(par.int=="min"){
        samp.dist[i] <- min(sim.data)
        # save the min of generated distribution
      }
    }
    return(quantile(samp.dist, c(0.05, 0.95)))
    # the output will be the 95% confidence interval of the target distribution

  }else if(mod=="MMgamma"){
    # use the method of moments with a gamma distribution to estimate

    mm.shape <- mean(data)^2/var(data)
    # get the original shape parameter of data
    mm.scale <- var(data)/mean(data)
    # get the original scale parameter of data

    # create an N*R array to store the gamma distributions
    sim.data <- array(rgamma(length(data)*R, shape=mm.shape, scale=mm.scale), dim=c(N, R))
    # use the function called by par.int for each column and store the results as a distribution
    samp.dist <- apply(sim.data, 2, FUN=sum.measure)
    return(quantile(samp.dist, c(0.05, 0.95)))
    # the output will be the 95% confidence interval of the target distribution

  }else if(mod=="KDE"){
    # use kernel density estimation

    ecdfstar <- function(t, data, smooth=smoo){
        # use pnorm function which has sd=smoo on the outer product of t and data.
        # t[i] is the quantile, data[j] is the mean for pnorm.
        # in other words, calculate the percentage under quantile "t" of distribution "data"
        outer(t, data, function(a,b){ pnorm(a, b, smooth)}) %>%
        rowMeans
        # then count the mean of each row, AKA, the mean percentage under quantile "t"
    }

    # create a 1 column data frame with a sequence from min-sd to max+sd of the data with break=0.01
    tbl <- data.frame(
        x = seq(min(data)-sd(data), max(data)+sd(data),
                by = 0.01)
    )

    tbl$p <- ecdfstar(tbl$x, data, smoo)
    # add a new column called p to store the result of the ecdfstar function
    tbl <- tbl[!duplicated(tbl$p),]
    # remove all rows that contain duplicated values in column "p".

    qkde <- function(ps, tbl){
      # convert "ps" to a factor with the break as column "p" in "tbl" data frame
      rows <- cut(ps, tbl$p, labels = FALSE)
      tbl[rows, "x"]
      # return the part of column "x" that matches the row-number factor
    }

    U <- runif(N*R) # create a uniform distribution with the size=N*R

    # store the result of qkde as an N*R matrix
    sim.data <- array(qkde(U,tbl), dim=c(N, R))
    # use the function called by par.int for each column and store the results as a distribution
    samp.dist <- apply(sim.data, 2, sum.measure)

    return(quantile(samp.dist, c(0.05, 0.95), na.rm=TRUE))
    # the output will be the 95% confidence interval

  }else if(mod=="Boot"){
    # use bootstrap

    # get random samples with size=N from the data R times, and store the result as an N*R matrix
    sim.data <- array(sample(data, N*R, replace=TRUE), dim=c(N,R))
    # use the function called by par.int for each column and store the results as a distribution
    samp.dist <- apply(sim.data, 2, sum.measure)

    return(quantile(samp.dist, c(0.05, 0.95), na.rm=TRUE))
    # the output will be the 95% confidence interval
  }
}
```

## Target capture function

Create a function to determine whether the confidence interval matches the requirement. When the result is TRUE, return 1.
```r
capture_par <- function(ci, true.par){
  1*(ci[1] < true.par & true.par < ci[2])
}
```


# Simulation

## Calculation Preparation

Now we can set the sample size N to 201. When using the gamma distribution, we use shape 1.4 and scale 3.
```r
N <- 201
shape.set <- 1.4
scale.set <- 3
```

Define the target values for coverage.
```r
true.norm.med <- qnorm(0.5)
true.norm.min <- mean(apply(array(rnorm(N*10000), dim=c(N, 10000)),2,min))
true.gamma.med <- qgamma(0.5, shape = shape.set, scale=scale.set)
true.gamma.min <- mean(apply(array(rgamma(N*10000, shape=shape.set, scale=scale.set), dim=c(N, 10000)),2,min))
```
For the true minimum of the distribution, we expand the data size 10,000 times and use the mean minimum value as the true minimum.

Create a table called "simsettings" to store the results of each estimation method and the target parameter.
```r
simsettings <- expand.grid(dist=c("norm", "gamma"), model=c("MMnorm", "MMgamma", "KDE", "Boot"), par.int=c("median", "min"), cov.prob=NA,  stringsAsFactors = FALSE, KEEP.OUT.ATTRS = FALSE)
```

Add a new column to store the target values.
```r
simsettings$truth <- c(true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min)
```

## Calculation

Based on the "simsettings" table, calculate the coverage probabilities and store them in the table.
```r
for(k in c(1:2,4:10,12:16)){
  dist1 <- simsettings[k,1]
  model1 <- simsettings[k,2]
  par.int1 <- simsettings[k,3]
  true.par1 <- simsettings[k,5]

  cover <- NA
  for(sims in 1:100){
    cover[sims] <- generate_data(N, dist1) %>%
    estimate.ci(mod=model1, par.int=par.int1, R=1000) %>%
    capture_par(true.par = true.par1)
  }
  simsettings[k,4] <- mean(cover)
}

```


# Conclusion

Show the result table.
```r
simsettings
```
```
##     dist   model par.int cov.prob       truth
## 1   norm  MMnorm  median     0.99  0.00000000
## 2  gamma  MMnorm  median     0.01  3.25311453
## 3   norm MMgamma  median       NA  0.00000000
## 4  gamma MMgamma  median     0.97  3.25311453
## 5   norm     KDE  median     0.94  0.00000000
## 6  gamma     KDE  median     0.93  3.25311453
## 7   norm    Boot  median     0.94  0.00000000
## 8  gamma    Boot  median     0.90  3.25311453
## 9   norm  MMnorm     min     1.00 -2.74462674
## 10 gamma  MMnorm     min     0.00  0.07277036
## 11  norm MMgamma     min       NA -2.74462674
## 12 gamma MMgamma     min     0.99  0.07277036
## 13  norm     KDE     min     0.94 -2.74462674
## 14 gamma     KDE     min     0.35  0.07277036
## 15  norm    Boot     min     0.40 -2.74462674
## 16 gamma    Boot     min     0.57  0.07277036
```

For the method of moments, when the data distribution matches the model distribution (e.g. norm - MMnorm, gamma - MMgamma), the coverage probabilities are more than 90%. When the distributions do not match each other, the results are close to 0% or NA.

For kernel density estimation, when we need to estimate the median of the distributions, the results are quite good and close to 100%. But when we need to estimate the minimum of the distributions, the coverage probabilities for normal and gamma are very different. For the normal distribution, it works well, but for the gamma distribution, it is about 37%. The reason might be that the gamma distribution is skewed.

For the bootstrap method, the results are not as good as the others. When we want to estimate the median of the distributions, the coverage probabilities are only about 90%. When it comes to the minimum of the distributions, the probabilities drop to about 50%. This is probably because random sampling makes it difficult to capture the minimum point every time.
