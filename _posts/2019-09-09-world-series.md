---
layout:     post
title:      How often does the better team win the World Series?
subtitle:   Probability and Statistical Inference - 03
date:       2019-09-09
author:     Zekun
header-img: img/prob3-worldseries.jpg
catalog: true
tags:
    - Probability
    - Simulation
    - R
---

Import the package at the very first.

```{r}
library(tidyverse)
```

# Introduction

![WORLD SERIES](https://cdn.technadu.com/wp-content/uploads/2019/05/World-Series-Logo.png)

> The World Series is the annual championship series of Major League Baseball (MLB) in North America, contested since 1903 between the American League (AL) champion team and the National League (NL) champion team. The winner of the World Series championship is determined through a best-of-seven playoff, and the winning team is awarded the Commissioner's Trophy. As the series is played during the fall season in North America, it is sometimes referred to as the Fall Classic.  
*From [Wikipedia - World Series](https://en.wikipedia.org/wiki/World_Series)*

In this blog, we are going to calculate the probability of several questions about the Braves and the Yankees in the World Series.

First, we need to define some parameter.

Parameter | Explaination
---|---|---
P<sub>B</sub> | In any given game, the probability that the Braves win
P<sub>Y</sub> = 1 - P<sub>B</sub> | in any given game, the probability that the Yankees win

# Questions
### 1. What is the probability that the Braves win the World Series given that P<sub>B</sub>=0.55?

First,we need to set the value of P<sub>B</sub> and P<sub>Y</sub>.
```{r}
PB <- 0.55
PY <- 1- PB
```

Create a function to calculate the probability of win. Win is defined as win 4 times in 7 games.
```{r}
calc_prob <- function(p){
  pnbinom(3, 4, p)
}
```

Now calculate the probability given that P<sub>B</sub>=0.55.
```{r}
calc_prob(PB)
```

Obviously, when the P<sub>B</sub> is 0.55, the probability that Braves win the World Series is 0.608.




### 2. What is the probability that the Braves win the World Series given that P<sub>B</sub>=x?
Now the P<sub>B</sub> is not defined yet, so we should assume the x could be any number between 0.5 to 1.

First, we need to generate the series of P<sub>B</sub> and the probability results.
```{r}
PBseries <- seq(0.5, 1, 0.01)
win_prob <- rep(NA, length(PBseries))
```

Now use the function we used before to calculate the probability given every P<sub>B</sub>.
```{r}
for(i in 1:length(win_prob)){
  win_prob[i] <- calc_prob(PBseries[i])
}
```

In order to intepret the relationship between P<sub>B</sub> and the probability that the Braves win, we can draw a graph for them.
```{r}
plot(x = PBseries,
     y = win_prob,
     xlim = c(0.5,1),
     ylim = 0:1,
     xlab = "Probability of the Braves winning a head-to-head matchup",
     ylab = "P(Braves win World Series)",
     main = "Probability of winning the World Series")
```
![](https://i.loli.net/2019/12/22/Bh7NjCIcKU2Myab.png)

As we can see, in this graph, when P<sub>B</sub> is increasing, the probability that the Braves win the World Series is increasing too. In fact, when we change the x scale to 0.0-1.0, we will find the line looks like a logistic curve.




### 3. Suppose one could change the World Series to be best-of-9 or some other best-of-X series. What is the shortest series length so that P(Braves win World Series|P<sub>B</sub>=0.55) ≥ 0.8?

As same as the first question, the P<sub>B</sub> needs to be 0.55. And now the game series length is not a certain. Definitely, the series length should be an odd number.
```{r}
PB <- 0.55
series_length <- seq(1, 999, 2)
```

Now we need to create a function to calculate the probability when the series length is parameter.
```{r}
calc_prob_sl <- function(sl){
  win_threshhold <- ceiling(sl/2)
  pnbinom(win_threshhold - 1, win_threshhold, 0.55)
}
```

In the end, given every series length, calculate the probability that the Braves win World Series. When the probability is equal to or more than 0.8, stop running and give the series length value and the probability.
```{r}
for(i in 1:length(series_length)){
  pb_win <- calc_prob_sl(series_length[i])
  if(pb_win >= 0.8){
    shortest <- series_length[i]
    p_shortest <- pb_win
    break}
}
shortest
p_shortest
```

Now we get the the shortest series length. It should be 71. In that situation, the probability that the Braves win World Series is about 0.802.


### 4. What is the shortest series length so that P(Braves win World Series|P<sub>B</sub>= x) ≥ 0.8? This will be a figure (see below) with P<sub>B</sub> on the x-axis and series length is the y-axis.
Now the P<sub>B</sub> is not defined again, so we should assume the x could be any number between 0.51 to 1.

First, we need to generate the series of P<sub>B</sub> and a series to save the length results given different P<sub>B</sub>. But the way, we also need a series of the possible series length we will test. Now the ceiling is 9999. If it's not enough, we can set a bigger limitation.
```{r}
PBseries <- seq(0.51, 1, 0.01)
length_record <- rep(NA, length(PBseries))
series_length <- seq(1, 9999, 2)
```


In order to calculate the probabilty that the Braves win the WS, we need a new function with 2 input, because both of the series length and P<sub>B</sub> are variables.
```{r}
calc_prob_sl_p <- function(sl,pb){
  win_threshhold <- ceiling(sl/2)
  pnbinom(win_threshhold - 1, win_threshhold, pb)
}
```

Now, calculate the shortest series length when P<sub>B</sub> is changing. Save the values in *length_record*.
```{r}
for(j in 1:length(PBseries)){
  for(i in 1:length(series_length)){
  pb_win <- calc_prob_sl_p(series_length[i],PBseries[j])
  if(pb_win >= 0.8){
    shortest <- series_length[i]
    break}
  }
  length_record[j] <- shortest
}
```

We have already get the shortest series length given different P<sub>B</sub>. Let's draw the figure to show the relationship between them.
```{r}
plot(x = PBseries,
     y = length_record,
     xlim = c(0.5,1),
     xlab = "Probability of the Braves winning a head-to-head matchup",
     ylab = "Series length",
     main = "Shortest series so that P(Win WS given p)>=0.8")
```
![](https://i.loli.net/2019/12/22/jA2LkzaNK5tF6OB.png)

in this graph, when P<sub>B</sub> is increasing, the shortest series length, when the probability that the Braves win the World Series is more than 0.8, is approching 1. When the P<sub>B</sub> is bigger than 0.8, the shortest series length is 1.



### 5. Calculate P( P<sub>B</sub>=0.55|Braves lose 3 games before winning a 4th game) under the assumption that either  P<sub>B</sub>=0.55 or  P<sub>B</sub>=0.45. Explain your solution.

According to Conditional probability formula，we can get:

$$
P(A|B)=\frac{P(A)P(B)}{P(B)}  \to  P(A)P(B)=P(A|B)P(B)\\
P(B|A)=\frac{P(A)P(B)}{P(A)}  \to  P(A)P(B)=P(B|A)P(A)\\
\to P(A|B)P(B)=P(A)P(B)=P(B|A)P(A)\\
\to P(A|B)=\frac{P(B|A)P(A)}{P(B)}
$$

Now the P(A) = P(P<sub>B</sub>=0.55), P(B) = P(Braves lose 3 games before winning a 4th game).
As a result, P( P<sub>B</sub>=0.55|Braves lose 3 games before winning a 4th game) = P(Braves lose 3 games before winning a 4th game|P<sub>B</sub>=0.55) * P(P<sub>B</sub>=0.55) ÷ P(Braves lose 3 games before winning a 4th game).

P(P<sub>B</sub>=0.55) = 0.5

Then use *dnbinom()* calculate P(Braves lose 3 games before winning a 4th game) and P(Braves lose 3 games before winning a 4th game|P<sub>B</sub>=0.55):
```{r}
(dnbinom(3,4,0.45)+dnbinom(3,4,0.55))/2
dnbinom(3,4,0.55)
```
P(Braves lose 3 games before winning a 4th game) = 0.1516092

P(Braves lose 3 games before winning a 4th game \| P<sub>B</sub>=0.55) = 0.1667701

P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) = P(Braves lose 3 games before winning a 4th game\|P<sub>B</sub>=0.55) * P(P<sub>B</sub>=0.55) ÷ P(Braves lose 3 games before winning a 4th game)
```{r}
0.1667701 * 0.5 / 0.1516092
```

P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) = 0.1667701 * 0.5 ÷ 0.1516092 = 0.5499999

Therefore, P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) is 0.5499999, about 0.55.
