---
layout:     post
title:      How often does the better team win the World Series?
subtitle:   Probability and Statistical Inference - 03
date:       2019-09-09
author:     Zekun Wang
description: "Use probability simulation to ask how often the stronger team actually wins a best-of-seven World Series."
header-img: img/headers/prob3-worldseries.jpg
catalog: true
mathjax: true
dark_chart_images: invert
series: Probability and Statistical Inference
series_nav_title: World Series
series_order: 3
tags:
    - Statistics
    - Simulation
    - R
---

First, import the package.

```r
library(tidyverse)
```

# Introduction

> The World Series is the annual championship series of Major League Baseball (MLB) in North America, contested since 1903 between the American League (AL) champion team and the National League (NL) champion team. The winner of the World Series championship is determined through a best-of-seven playoff, and the winning team is awarded the Commissioner's Trophy. As the series is played during the fall season in North America, it is sometimes referred to as the Fall Classic.  
*From [Wikipedia - World Series](https://en.wikipedia.org/wiki/World_Series)*

In this blog, we are going to calculate probabilities for several questions about the Braves and the Yankees in the World Series.

First, we need to define some parameters.

$$
P_B = \text{per-game win probability for the Braves},\qquad
P_Y = 1 - P_B.
$$

Parameter | Explanation
---|---|---
$P_B$ | In any given game, the probability that the Braves win
$P_Y = 1 - P_B$ | In any given game, the probability that the Yankees win

# Questions
### 1. What is the probability that the Braves win the World Series given that $P_B=0.55$?

First, we need to set the values of $P_B$ and $P_Y$.
```r
PB <- 0.55
PY <- 1- PB
```

Create a function to calculate the probability of winning the series. A series win is defined as winning 4 games in a best-of-7 series. Equivalently, the number of losses before the 4th win follows a negative binomial law, and

$$
P(\text{Braves win WS}\mid P_B=p)
=
\sum_{k=0}^{3}\binom{3+k}{k}(1-p)^k p^{4}
=
P\bigl(X \le 3\bigr),
$$

where $X$ is the number of losses before the 4th win (R's negative-binomial failures-before-successes convention with $r=4$).
```r
calc_prob <- function(p){
  pnbinom(3, 4, p)
}
```

Now calculate the probability given that $P_B=0.55$.
```r
calc_prob(PB)
```

When $P_B$ is $0.55$, the probability that the Braves win the World Series is $0.608$.




### 2. What is the probability that the Braves win the World Series given that P<sub>B</sub>=x?
Now P<sub>B</sub> is not fixed, so we assume x can be any number between 0.5 and 1.

First, we need to generate a series of P<sub>B</sub> and the probability results.
```r
PBseries <- seq(0.5, 1, 0.01)
win_prob <- rep(NA, length(PBseries))
```

Now use the function from before to calculate the probability for every P<sub>B</sub>.
```r
for(i in 1:length(win_prob)){
  win_prob[i] <- calc_prob(PBseries[i])
}
```

In order to interpret the relationship between P<sub>B</sub> and the probability that the Braves win, we can draw a graph for them.
```r
plot(x = PBseries,
     y = win_prob,
     xlim = c(0.5,1),
     ylim = 0:1,
     xlab = "Probability of the Braves winning a head-to-head matchup",
     ylab = "P(Braves win World Series)",
     main = "Probability of winning the World Series")
```
<img class="chart-invert" src="{{ "/img/posts/2019-09-09-world-series/win-probability.png" | relative_url }}" alt="Probability that the Braves win the World Series as a function of per-game win probability" width="1258" height="749" loading="lazy" decoding="async">

As we can see from this graph, when P<sub>B</sub> increases, the probability that the Braves win the World Series also increases. In fact, when we change the x-axis scale to 0.0-1.0, the line looks like a logistic curve.




### 3. Suppose one could change the World Series to be best-of-9 or some other best-of-X series. What is the shortest series length so that P(Braves win World Series|P<sub>B</sub>=0.55) ≥ 0.8?

As in the first question, P<sub>B</sub> needs to be 0.55. Now the series length is uncertain. The series length should be an odd number.
```r
PB <- 0.55
series_length <- seq(1, 999, 2)
```

Now we need to create a function to calculate the probability when the series length is a parameter.
```r
calc_prob_sl <- function(sl){
  win_threshold <- ceiling(sl/2)
  pnbinom(win_threshold - 1, win_threshold, 0.55)
}
```

Finally, for each series length, calculate the probability that the Braves win the World Series. When the probability is at least 0.8, stop the loop and return the series length and the probability.
```r
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

Now we have the shortest series length. It should be 71. In that situation, the probability that the Braves win the World Series is about 0.802.


### 4. What is the shortest series length so that P(Braves win World Series|P<sub>B</sub>= x) ≥ 0.8? This will be a figure (see below) with P<sub>B</sub> on the x-axis and series length on the y-axis.
Now P<sub>B</sub> is not fixed again, so we assume x can be any number between 0.51 and 1.

First, we need to generate a sequence of P<sub>B</sub> values and a vector to save the length results for different P<sub>B</sub> values. In addition, we need a sequence of possible series lengths to test. The upper limit is 9999. If that is not enough, we can set a larger limit.
```r
PBseries <- seq(0.51, 1, 0.01)
length_record <- rep(NA, length(PBseries))
series_length <- seq(1, 9999, 2)
```


To calculate the probability that the Braves win the World Series, we need a new function with two inputs because both the series length and P<sub>B</sub> are variables.
```r
calc_prob_sl_p <- function(sl,pb){
  win_threshold <- ceiling(sl/2)
  pnbinom(win_threshold - 1, win_threshold, pb)
}
```

Now, calculate the shortest series length when P<sub>B</sub> is changing. Save the values in *length_record*.
```r
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

We have now obtained the shortest series length for different P<sub>B</sub> values. Let's draw a figure to show the relationship between them.
```r
plot(x = PBseries,
     y = length_record,
     xlim = c(0.5,1),
     xlab = "Probability of the Braves winning a head-to-head matchup",
     ylab = "Series length",
     main = "Shortest series so that P(Win WS given p)>=0.8")
```
<img class="chart-invert" src="{{ "/img/posts/2019-09-09-world-series/shortest-series.png" | relative_url }}" alt="Shortest series length needed for an 80 percent World Series win probability" width="1258" height="749" loading="lazy" decoding="async">

In this graph, as P<sub>B</sub> increases, the shortest series length required for the Braves to win the World Series with probability greater than 0.8 approaches 1. When P<sub>B</sub> is greater than 0.8, the shortest series length is 1.



### 5. Calculate $P(P_B=0.55\mid\text{Braves lose 3 games before winning a 4th game})$ under the assumption that either $P_B=0.55$ or $P_B=0.45$. Explain your solution.

Let $A=\{P_B=0.55\}$ and let $B$ be the event that the Braves incur exactly 3 losses before their 4th win. Bayes' theorem gives

$$
P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)}.
$$

With a uniform prior on the two candidate strengths, $P(A)=1/2$, and by the law of total probability

$$
P(B)
=
\frac12\,P(B\mid P_B=0.55)
+
\frac12\,P(B\mid P_B=0.45),
$$

where each likelihood is a negative-binomial PMF,

$$
P(B\mid P_B=p)=\binom{6}{3}p^{4}(1-p)^{3}.
$$

Then use *dnbinom()* to calculate $P(B)$ and $P(B\mid P_B=0.55)$:
```r
(dnbinom(3,4,0.45)+dnbinom(3,4,0.55))/2
dnbinom(3,4,0.55)
```
P(Braves lose 3 games before winning a 4th game) = 0.1516092

P(Braves lose 3 games before winning a 4th game \| P<sub>B</sub>=0.55) = 0.1667701

P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) = P(Braves lose 3 games before winning a 4th game\|P<sub>B</sub>=0.55) * P(P<sub>B</sub>=0.55) ÷ P(Braves lose 3 games before winning a 4th game)
```r
0.1667701 * 0.5 / 0.1516092
```

P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) = 0.1667701 * 0.5 ÷ 0.1516092 = 0.5499999

Therefore, P( P<sub>B</sub>=0.55\|Braves lose 3 games before winning a 4th game) is 0.5499999, about 0.55.
