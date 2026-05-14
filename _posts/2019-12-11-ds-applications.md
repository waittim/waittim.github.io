---
layout:     post
title:      As data scientists, what should we do?
subtitle:   Data science application analysis, using product launch processes as an example
date:       2019-12-11
author:     Zekun
header-img: img/headers/post-ds-application.jpg
catalog: true
tags:
    - Career
    - Talk
---
# Slides
<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTr02Z5Zn7lGTvEo2Jz5P0ADkz76YFfvNOnQUXeQiHwZ5CrpOJhR2fL8avHvWIIcQtWGTb6wOTmLNRS/embed?start=false&loop=true&delayms=15000" frameborder="0" width="700" height="423" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>


# Summary

Three major parts of data science work:
- Use **EXPLORATION** to turn the unknown into the known.
- Use **INFERENCE** to help find something new from the old.
- Use **PREDICTION** to make better decisions.

# Scene Setting

> Imagine a scenario in which our manager asks us to make suggestions for the launch of a new product, and all we have is a dataset containing historical information about this type of product.
>
> What can we do now? What should we do?

This is a common scenario in industry. The backgrounds and fields may differ, but the purpose is the same: we need to start with raw data and move toward a decision or product that can be implemented.

**So what are the key steps in this process?**
Overall, we can divide it into three parts:
01. EXPLORATION
02. INFERENCE
03. PREDICTION

# Concepts & Connections

#### 01 Exploration

This is often done through **visualization**. Use visual exploration to understand what is in a dataset and what characteristics the data has.

Identify potential relationships or insights hidden in the data that can support **inference** and **prediction**.

#### 02 Inference

Use data analysis to infer the properties of a dataset. These properties give the analyst a more accurate understanding of the data and provide a theoretical basis for **prediction**.

#### 03 Prediction

Based on **exploration** and **inference** results, prediction encompasses a variety of techniques from data mining, predictive modeling, and machine learning that analyze current and historical facts to make predictions about unknown events.

# 01 Exploration (Visualization)

It is difficult for humans to process large numbers quickly, especially if the numbers are not ordered. It is even harder to quickly calculate proportional relationships among numbers or understand information within groups under certain conditions.

But the **human eye can quickly process image information** and extract key content from it. Therefore, facing a new data set, visualizing the data is one of the best ways to understand it.

> For product data, we can explore sales under different channels, delivery costs, and changes over time. We can also compare the differences between sub-categories within this larger product category to help differentiate product positioning.

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
Due to collection costs, storage costs, or historical reasons, we cannot always have a dataset that contains everything we may need. In actual data analysis, we may need to discuss information that is not directly included in the dataset. **Visualization can only show information directly represented** in the data, but for information that is not directly displayed, we need to use inference-related theory to make inferences based on existing information.

> For the product data example, we can only see the historical values of each product's variables, but those values do not directly tell us which products are successful. We need to infer and judge the success of a product based on sales volume, cost, profit margin, capital turnover cycle, and the stability of the production process itself.

The significance of inference is that it extracts new information from what is already known. In other words, inference can help **find something new from the old**.

> Use billing codes, drug names, and more to mark Parkinson's patients.
>
> Use pathological data to distinguish normal samples from abnormal samples in order to extract control groups for analysis.
>
> -- Paul Harris (Professor of Biomedical Informatics, Vanderbilt University REDCap)

> Find out the most accurate and efficient indicators that can determine whether a patient has hypertension among a large number of indicators such as genetic data.
>
> -- Josh Denny (Professor of Biomedical Informatics and Medicine, Vanderbilt University)

# 03 Prediction

The information obtained through visualization and inference is based on existing data, and existing data is usually a description of what happened before.

In actual work, it is not enough to focus on the past. We often need to **make decisions about the future**. At this point, data-based forecasting will become a vital part.

> In the product launch example, we may need to predict the possible sales and profitability of the planned product before the actual launch. According to the forecast results, we can change resource allocation decisions such as product lines and pre-production volume to reduce risks and obtain higher returns.

The value of prediction lies in reducing the cost of trial and error and **making better decisions**.

> Prediction finds target markets that are "likely to buy" and "definitely buy", and launches products when the predicted value exceeds a certain threshold.
>
> -- Kelly Goldsmith (Associate Professor of Marketing, Vanderbilt University)

> Predict the number of viewers to help determine the number of ad views that can be sold, and adjust the amount of ad inventory sold based on the forecast to achieve the expected playback with minimal cost.
>
> -- Minchun Zhou (Senior Data Scientist, Comcast)

> For Wal-Mart in-home delivery, predict what and how often specific consumers might buy, and related products that they might want to try.
>
> -- Betsy Barton (Director of Data Science, Walmart In-Home Delivery)

# Epicycle

Of course, **this process may be performed more than once**. We may need to process the same dataset multiple times, then reflect and summarize after each round while considering what can be implemented next.

>For example, after visualization, think about whether there are still questions that are not clear enough and need further exploration. After using inference to investigate, consider again how to visualize the results. Based on the results obtained in previous steps, we can also think about whether we can use them to make predictions and which prediction methods are suitable.

In a broad sense, this process also belongs to some kind of epicycle. These parts do not appear in a purely linear sequence, but exist in a **repeatable and mutually affecting relationship**. They constantly promote each other and ultimately form a successful project.

# Conclusions

To achieve the goal more efficiently and successfully, we should first **determine what type of work we need to do**. Do we want to understand the data, dig deeper based on existing information, or predict what has not happened based on existing data?

After confirming the purpose, we can decide whether the work we need to do is exploration, inference, or prediction.

Finally, we can find the best solution according to that category.

At the same time, we need to carry out this process **multiple times** in the same project, and constantly improve and expand until a satisfactory result is achieved.
