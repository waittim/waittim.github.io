---
layout:     post
title:      What makes a trending video?
subtitle:   An analysis of trending YouTube videos
date:       2019-10-29
author:     Zekun Wang, Ali, Mingli
authors:
    - name: Zekun Wang
      url: /about/
    - name: Ali
    - name: Mingli
header-img: img/headers/2019-10-29-trending-video.jpg
catalog: true
dark_chart_images: invert
tags:
    - YouTube
    - EDA
    - Project
    - R
    - Python
---


## Slides
<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTN6OHLfZ70A3x6X97oe68aBpaGtQUUmvcnJ-n9QSCdz99m_S4hYXZYY__sMhHhwB0hapDY1y2HuHuo/embed?start=false&loop=true&delayms=30000" frameborder="0" width="700" height="423" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>



## Introduction

YouTube is one of the biggest media platforms of the 21st century.

**5 Billion** videos are watched daily.

**500 Hours** of videos are uploaded every minute.

**51%** of users say that they visit the website daily.

This makes YouTube a powerful tool for advertising, business, research, and content creators.

#### Motivation

Being able to predict if a YouTube video is likely to be trending or not is highly useful if you are:
- **A content creator** who wants to make trending videos.
- **An advertiser** who wants to know the best videos to put advertisements on before they become trending videos.
- **A researcher** trying to derive insight about behavior from YouTube trends.

To do this, you will need to know:
1. **When** to upload or look for a potentially trending YouTube video
2. **How** to upload or look for a potentially trending YouTube video
3. **What** to upload or look for in a potentially trending YouTube video

#### A look at the trending videos

A trending video can be identified by three major measures:
1. Number of **Likes**
2. Number of **Views**
3. Number of **Comments**

Likes | Views | Comments
--- | --- | ---
![]({{ "/img/posts/2019-10-29-trending-video/1.png" | relative_url }} "dislikes & likes") | ![]({{ "/img/posts/2019-10-29-trending-video/2.png" | relative_url }} "views") | ![]({{ "/img/posts/2019-10-29-trending-video/3.png" | relative_url }} "comments")

Upon looking at the distribution of likes, dislikes, views, and comments of the trending YouTube videos, we can see that most trending YouTube videos have a total of:
1. **1,000,000** views
2. About **1,000** dislikes or **10,000** likes
3. About **2,000** comments

We will be looking at the number of videos being posted and the number of views being received.

## When to post a trending video

#### Best month

![]({{ "/img/posts/2019-10-29-trending-video/4.png" | relative_url }} "best month")

The **lowest** number of trending videos is posted in the months of **June** to **October**.

It also shows that the **highest** number of trending videos is posted in **May**, which also has the highest number of views.

The best time to post a video would be **April** and **May**, as they show the **highest** number of views compared with the number of videos posted. December, March, and February also see a high number of trending videos, but not as many views.

#### Best day of the week

![]({{ "/img/posts/2019-10-29-trending-video/5.png" | relative_url }} "Best day of the week")

Most trending videos are posted from **Tuesday** through **Friday**. Thursday and Friday see the highest number of trending videos, with Friday showing the highest number of views.

Interestingly, **Saturday** and **Sunday** are the worst days to post videos, as fewer videos are posted on these days and they see **the lowest number of views** compared with other days.

However, there might be an extremely small chance that a video that you post on Sunday reaches **200 million views**!

#### Best time of day

![]({{ "/img/posts/2019-10-29-trending-video/6.png" | relative_url }} "Best time of day 1")
![]({{ "/img/posts/2019-10-29-trending-video/7.png" | relative_url }} "Best time of day 2")

We see the highest number of trending videos being posted around **8AM to 5PM** with the peak time from **9AM to 1PM**. (CST)

Surprisingly, around **11PM**, when very few videos are being posted, we see the **highest variation** in the number of views!

The best time to post a video would be around **8AM to 11AM**. However, there is a small chance that if you post at **11PM**, your video will get the highest number of views, though it might be risky because this is also a low-volume time.


## How to post a trending video

#### Rows of description

“Rows of description” are defined by the number of rows it takes to give the description of the video.

![]({{ "/img/posts/2019-10-29-trending-video/8.png" | relative_url }} "Rows of description")

Most trending YouTube videos have **1 - 3 rows** of description only and videos with **1 row of description** see the highest number of views. Keeping a simple description of the video may be what attracts or loses a viewer.

However, we see a spike in the number of views at around 20 rows of description. These might be videos that require further explanation.

#### Number of tags

![]({{ "/img/posts/2019-10-29-trending-video/9.png" | relative_url }} "Number of tags")

There are a large number of trending videos with no tags, but they see a lower number of views. Videos with **3 to 20** tags see a higher number of views. Most people uploading videos choose to add tags within this range.

We can also see that adding more tags outside of this range resulted in a decline in the number of views. Furthermore, the number of people choosing to add tags greater than this range also declined.  

#### Title of a trending video

Number of Uppercase Letters | Length of Title  
--- | ---
![]({{ "/img/posts/2019-10-29-trending-video/10.png" | relative_url }} "Number of Uppercase Letters") | ![]({{ "/img/posts/2019-10-29-trending-video/11.png" | relative_url }} "Length of Title")

The greatest number of views appeared on videos where the title had between **1 and 15** uppercase letters. Most uploaders chose to stay within this range.

The highest number of views appeared on videos where the title was less than **50** characters long. Uploaders mostly chose titles between **25-50** characters long.

## What is in a trending video

#### Categorical analysis

![]({{ "/img/posts/2019-10-29-trending-video/12.png" | relative_url }} "Categorical analysis")
Categories of **Entertainment** and **Music** have the highest number of trending videos. However, Music has a higher number of views as compared to Entertainment.

Film and animation has a lower number of trending videos compared with Entertainment but has comparable views.

If you are a **musician** or an **entertainer**, your videos are more likely to be trending as compared to any other type of video.

#### Likes/Dislikes ratio

If the L/D ratio is less than 1, more people disliked the video. If greater than 1, more people liked the video. If equal to 1, an equal number of people liked and disliked the video. A video is **controversial** when the L/D ratio is less than 1 or equal to 1.   

![]({{ "/img/posts/2019-10-29-trending-video/13.png" | relative_url }} "Likes/Dislikes ratio")

If L/D = **10-100** we see **the highest views**.

If the L/D ratio is **less than 10**, the number of views **declines**. **The more controversial** a video is, **the fewer** views it has.

However, videos with higher **L/D ratios (>100)** coincided with **fewer views**. It seems that videos which are slightly controversial may be viewed more than videos which are not controversial at all.

#### Sentiment Analysis

Understanding how sentiment plays a role in making a trending YouTube video is an interesting area to explore.

To do this sort of analysis, we look at the channel title, tags, and description to see how positive or negative a typical trending video is.

**Classification**
For this problem we can classify our videos into four distinct categories:
1. **Popular :** views < 10,000  
2. **Very Popular :** 10,000 < views < 100,000
3. **Highly Popular :** 100,000 < views < 1 Million
4. **Hyper Popular :** views > 1 Million

![]({{ "/img/posts/2019-10-29-trending-video/14.png" | relative_url }} "Sentiment Analysis 1")

From this, we can see that very popular to hyper popular trending videos have positive sentiments in their descriptions, tags, and channel titles at around **70%**.

The **least** popular videos of these four categories had a positive sentiment of about **57%**.

This is consistent with our analysis of Likes/Dislikes ratio. It shows that a video needs to be **controversial**; however **the more negative** it tends to be, **the less likely** it is to be the most trending video.

## Conclusions

![]({{ "/img/posts/2019-10-29-trending-video/15.png" | relative_url }} "breakdown")

Knowing the components of a trending YouTube video can provide insight into what a trending video looks like and how to recognize it, but **human behavior is unpredictable** and there will always be outliers.

In general, your video is much more likely to be trending if you are a **musician** or an **entertainer**. This might have to do with the demographic and the reasons why people visit YouTube.

While creating video content, it’s important to keep the idea of **controversy** in mind. This is based on human psychology: people are attracted to anything that grabs attention, and controversy does just that.

However, it’s important to **strike a balance**. You will see the most views and have the highest likelihood of a trending video when you hit the sweet spot between challenging a thought and inciting emotion.
As a content creator, you will have to make sure to keep that in mind while trying to enter an online media market that is highly saturated.

## Appendix

Motivated by the results from this research, we built a **classification model** using **naive Bayes**.

The input features are title, channel_title, tags, and description.

We labeled our dataset into four categories as before:
1. Popular : 10,000 > views
2. Very Popular : 10,000 < views < 100,000
3. Highly Popular : 100,000 < views < 1 Million
4. Hyper Popular : views > 1 Million

 . | precision | recall | f1-score | support
 ---|---|---|---|---
 1 | 0.14 | 0.89 | 0.25 | 162
 2 | 0.20 | 0.68 | 0.31 | 878
 3 | 0.80 | 0.39 | 0.53 | 3873
 4 | 0.81 | 0.58 | 0.68 | 3277
 accuracy |  |  | 0.51 | 8190
 macro avg | 0.49 | 0.64 | 0.44 | 8190
 weighted avg | 0.73 | 0.51 | 0.56 | 8190

The model has 0.73 weighted average precision, which is a solid result. It further supports the importance of the four features: **title, channel_title, tags, description**.


*Hint 1: Project GitHub page: [Youtube-trending-videos-analysis](https://github.com/waittim/Youtube-trending-videos-analysis)*

*Hint 2: Data source: [Trending YouTube Video Statistics](https://www.kaggle.com/datasnaek/youtube-new)*
