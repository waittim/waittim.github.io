---
layout:     post
title:      Simulation method comparison
subtitle:   Probability and Statistical Inference - 08
date:       2019-10-27
author:     Zekun
header-img: img/prob8-simulation.jpg
catalog: true
tags:
    - Probability
    - Simulation
    - R
    - Method of Moments
    - KDE
    - Bootstrap
---



# Situation description

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

Set up data generate a function that can generate the data based on normal distribution or gamma distribution. The distribution will be defined by the parameter “dist”. The default parameter of the gamma distribution is shape=1.4 and scale=3.

```{r}
generate_data <- function(N, dist, sh=1.4, sc=3){
  if(dist=="norm"){
    rnorm(N)
  }else if(dist=="gamma"){
    rgamma(N, shape=sh, scale=sc)
  }
}
```


## Confidence interval estimation function

Then define the function for calculating the confidence interval, which can estimate the distribution by method of moment with normal distribution, method of moment with gamma distribution, kernel density distribution, and bootstrap. At the same time, the function can use the function defined by “par.int” to calculate the parameter we want. The details will be introduced in the chunk.
```{r}
estimate.ci <- function(data, mod, par.int, R=10, smoo=0.3){
  # data: input data
  # mod: define the estimation method and the distribution.
  #      (MMnorm: method of moment with normal distribution,
  #       MMgamma: method of moment with gamma distribution,
  #       KDE: kernal density distribution,
  #       Boot: bootstrap)
  # par.int: the function what can get the parameter we want for the estimated distribution

  N <- length(data) # save N as the number of the inputted data
  sum.measure <- get(par.int) # make charactor can be used as function


  if(mod=="MMnorm"){
    # use method of moment with normal distribution to estimate

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
    # the output will be the 95% confidence interval of needed distribution

  }else if(mod=="MMgamma"){
    # use method of moment with gamma distribution to estimate

    mm.shape <- mean(data)^2/var(data)
    # get the original shape parameter of data
    mm.scale <- var(data)/mean(data)
    # get the original scale parameter of data

    #create a N*R array to reserve the gamma distributions
    sim.data <- array(rgamma(length(data)*R, shape=mm.shape, scale=mm.scale), dim=c(N, R))
    # use the function called by par.int for each column and reserve the results as a distribution
    samp.dist <- apply(sim.data, 2, FUN=sum.measure)
    return(quantile(samp.dist, c(0.05, 0.95)))
    # the output will be the 95% confidence interval of needed distribution

  }else if(mod=="KDE"){
    # use kernal density estimation

    ecdfstar <- function(t, data, smooth=smoo){
        # use pnorm function which has sd=smoo on the outer product of t and data.
        # t[i] is the quantile, data[j] is the mean for pnorm.
        # in other words, calculate the persentage under quantile "t" of distribution "data"
        outer(t, data, function(a,b){ pnorm(a, b, smooth)}) %>%
        rowMeans
        # then count the mean of each row, AKA, the mean persentage under quantile "t"
    }

    # create a 1 column data frame with a sequence from min-sd to max+sd of the data with break=0.01
    tbl <- data.frame(
        x = seq(min(data)-sd(data), max(data)+sd(data),
                by = 0.01)
    )

    tbl$p <- ecdfstar(tbl$x, data, smoo)
    # add a new column called p reserve the result of ecdfstar function
    tbl <- tbl[!duplicated(tbl$p),]
    # remove all of rows which contain the duplicated value in column "p".

    qkde <- function(ps, tbl){
      # convert "ps" to a factor with the break as column "p" in "tbl" data frame
      rows <- cut(ps, tbl$p, labels = FALSE)
      tbl[rows, "x"]
      # return the part of column "x" which match the rows number factor
    }

    U <- runif(N*R) # create a uniform distribution with the size=N*R

    # reserve the result of qkde as a N*R matrix
    sim.data <- array(qkde(U,tbl), dim=c(N, R))
    # use the function called by par.int for each column and reserve the results as a distribution
    samp.dist <- apply(sim.data, 2, sum.measure)

    return(quantile(samp.dist, c(0.05, 0.95), na.rm=TRUE))
    # the output will be the 95% confidence interval

  }else if(mod=="Boot"){
    # use bootstrap

    # get random sample with size=N from the data R times, reserve the result as a N*R matrix
    sim.data <- array(sample(data, N*R, replace=TRUE), dim=c(N,R))
    # use the function called by par.int for each column and reserve the results as a distribution
    samp.dist <- apply(sim.data, 2, sum.measure)

    return(quantile(samp.dist, c(0.05, 0.95), na.rm=TRUE))
    # the output will be the 95% confidence interval
  }
}
```

## Destination capture function

Create a function to justify that is the confidence interval matches the requirement. When the result is TRUE, return 1.
```{r}
capture_par <- function(ci, true.par){
  1*(ci[1] < true.par & true.par < ci[2])
}
```


# Simulation

## Calculation prepare

Now we can set the size of distribution N is 201. When use gamma distribution, we will use the shape 1.4 and scale 3.
```{r}
N <- 201
shape.set <- 1.4
scale.set <- 3
```

Define the capture destinations.
```{r}
true.norm.med <- qnorm(0.5)
true.norm.min <- mean(apply(array(rnorm(N*10000), dim=c(N, 10000)),2,min))
true.gamma.med <- qgamma(0.5, shape = shape.set, scale=scale.set)
true.gamma.min <- mean(apply(array(rgamma(N*10000, shape=shape.set, scale=scale.set), dim=c(N, 10000)),2,min))
```
For the standard min of distribution part, we expand the data size for 10000 times and get the mean min value as the standard min.

Create a table called "simsettings" to reserve the results of each estimation method and the target parameter.
```{r}
simsettings <- expand.grid(dist=c("norm", "gamma"), model=c("MMnorm", "MMgamma", "KDE", "Boot"), par.int=c("median", "min"), cov.prob=NA,  stringsAsFactors = FALSE, KEEP.OUT.ATTRS = FALSE)
```

Add a new column to reserve the capture destinations.
```{r}
simsettings$truth <- c(true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.med, true.gamma.med, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min, true.norm.min, true.gamma.min)
```

## Calculation

Base on the "simsettings" table, calculate the capture probabilities and reserve them in the table.
```{r}
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
```{r}
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

Definitely, for the method of moment part, when the data distribution matches the model distribution (e.g. norm - MMnorm, gamma - MMgamma), the capture probabilities are more than 90%. When the distributions do not match with each other, the results will be close to 0% or NA.

And for kernel density estimation, when we need to get the median of the distributions, the results are pretty good as close to 100%. But when we need to get the min of the distributions, the capture probabilities of normal and gamma are really different. For the normal distribution, it works well, but for gamma distribution, it is about 37%. The reason might be that gamma distribution is a skewed distribution.

For the bootstrap part, the results are not as good as others. When we want to get the median of the distributions, the capture probabilities are just about 90%. And when it comes to min of the distributions, the probabilities become 50%. Obviously, it is because selecting a sample randomly is too difficult to get the min point every time.
