---
layout:     post
title:      For data scientist, what should we do?
subtitle:   Data science application analysis, taking product launching processes as an example
date:       2019-12-11
author:     Zekun
header-img: img/post-ds-application.jpg
catalog: true
tags:
    - Career
    - Talk
---

# Summary

3 big parts in Data Science jobs:
- Use **EXPLORATION** to turn the unknown into the known.
- Use **INFERENCE** to help find new old.
- Use **PREDICTION** to make better decisions.

# Scene Setting

> Imagine a scenario in which our superior asked us to make suggestions for the launch of a new product, and all we have is a data set that contains the past relevant situation of this type of product.
>
> What can we do now? What should we do?

This is a common scenario for the industry. Maybe different backgrounds, different fields, but the same purpose: we need to start with pure data and go on to obtain a product that can be implemented.

**So what are the key steps in this process?**
Overall, we can divide it into three parts:
01. EXPLORATION
02. INFERENCE
03. PREDICTION

# Concepts & Connections

#### 01 Exploration

It is also called **visualization**. Use visual exploration to understand what is in a dataset and the characteristics of the data.

Identify potential relationships or insights that may be hidden in the data which will help **inference** and **prediction**.

#### 02 Inference

Use data analysis to deduce the properties of a dataset. The properties will give the analyst a more accurate perception of the data and provide a theoretical basis for **prediction**.

#### 03 Prediction

Reference **exploration** and **inference** results encompass a variety of techniques from data mining, predictive modeling, and machine learning, that analyze current and historical facts to make predictions about unknown events.

# 01 Exploration (Visualization)

It is difficult for humans to process large numbers quickly, especially if the numbers are not specifically ordered. Not to mention the quick calculation of the proportional relationship between the numbers, the information within the group under certain conditions.

But the **human eye can quickly process image information** and extract key content from it. Therefore, facing a new data set, visualizing the data is one of the best ways to understand it.

> For product data, we can explore the sales of this type of product under different channels, delivery costs, and changes over time. We can also compare the differences between different sub-categories under this large category of products to help differentiate the positioning of products.

The process of exploration and visualization can help us **turn the unknown into the known**.

> Based on fMRI images of the brain of insomnia patients, explore whether there is any difference between them and the images of ordinary people.
>
> Explore whether physical pain and social pain behave differently in the brain.
>
> -- Catie Chang (Assistant Professor of Computer Science, Vanderbilt University)

> Visualizing personal stories that are closer to real life enables viewers to have a more immersive experience.
>
> -- Yorgos Askilidis (Senior Data Scientist, Instagram)

# 02 Inference
Due to collection costs, storage costs, or historical reasons, we cannot have a data set that contains everything that may be needed. In actual data analysis, we may need to display information that is not included in the data set directly. **Visualization can only show information directly represented** in the data, but for the data that is not directly displayed, we need to use inference related theory to make inferences based on the existing information.

> For product data example, we can only see the values of variables of each product in the past, but the values do not directly tell us what products are successful. We need to infer and judge the success of a product based on sales volume, cost, profit margin, capital turnover cycle and the stability of the production process of the product itself.

The significance of inference is to get new information from what is already known. In other words, the inference can help **find something new from the old**.

> Use billing codes, drug names, and more to mark Parkinson's patients.
>
> Use pathological data to distinguish normal samples from abnormal samples in order to extract control groups for analysis.
>
> -- Paul Harris (Professor of Biomedical Informatics, Vanderbilt University | REDCap)

> Find out the most accurate and efficient indicators that can determine whether a patient has hypertension among a large number of indicators such as genetic data.
>
> -- Josh Denny (Professor of Biomedical Informatics and Medicine, Vanderbilt University)

# 03 Prediction

The information obtained by the visualization and inference process is based on the existing data, and the existing data must be a description of what happened before.

In actual work, it is not enough to focus on the past. We often need to **make decisions about the future**. At this point, data-based forecasting will become a vital part.

> In the example of the product launch, we may need to predict the possible sales and profitability of the planned product before the actual product launch. According to the forecast results, we can change the resource allocation methods such as product line and pre-production volume to reduce risks and obtain higher returns.

The value of prediction lies in reducing the cost of trial and error and **making better decisions**.

> Prediction finds target markets that are "likely to buy" and "definitely buy", and launches products when the predicted value exceeds a certain threshold.
>
> -- Kelly Goldsmith (Associate Professor of Marketing, Vanderbilt University)

> Predict the number of viewers to help determine the number of ad views that can be sold, and adjust the number of ads sale based on the forecast to complete the expected playback with minimal cost.
>
> -- Minchun Zhou (Senior Data Scientist, Comcast)

> For Wal-Mart in-home delivery, predict what and how often specific consumers might buy, and related products that they might want to try.
>
> -- Betsy Barton (Director of Data Science, Walmart In-Home Delivery)

# Epicycle

Of course, **this process may be performed more than once**. We may need to perform multiple processing on the same data set, and re-reflect and summarize after each processing, considering what can be implemented next.

>For example, after visualization, think about whether there are still questions that not clear enough and need to be explored. After using inference to investigate, consider again how to visualize the results. And based on the results obtained in previous steps, we can also think about whether we can use them to make predictions and what are the suitable prediction methods.

In a broad sense, this process also belongs to some kind of epicycle. These parts do not appear in a purely linear sequence, but exist in a **repeatable and mutually affecting relationship**. They constantly promote each other and ultimately form a successful project.

# Conclusions

In order to achieve the goal more efficiently and successfully, in the actual operation process, we should first **determine what type of things we need to do**. Do we want to understand the data, or dig deeper based on the existing information, or predict what has not happened based on the existing data.

After confirming the purpose, it is clear from the definition whether what we need to do is exploration, inference or prediction.

Finally, the best solution will be found according to the category.

At the same time, we need to carry out this process **multiple times** in the same project, and constantly improve and expand until a satisfactory result is achieved.

# Slides
<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTr02Z5Zn7lGTvEo2Jz5P0ADkz76YFfvNOnQUXeQiHwZ5CrpOJhR2fL8avHvWIIcQtWGTb6wOTmLNRS/embed?start=false&loop=true&delayms=15000" frameborder="0" width="700" height="423" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
