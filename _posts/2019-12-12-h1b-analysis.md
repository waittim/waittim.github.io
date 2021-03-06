---
layout:     post
title:      Think and Get Jobs - H1B Visa Analysis
subtitle:   Helping the international data science students strategize job search
date:       2019-12-12
author:     Zekun, Yasi, Yilin, Ali
header-img: img/h1b/post-h1b.jpeg
catalog: true
tags:
    - H1B
    - EDA
    - Project
    - R
---

![title](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/0.png)


# H1B
The H1B visa is a non-immigrant visa that allows companies in the US to hire graduate-level workers in specialty occupations that require theoretical or technical expertise in specialized fields.

#### Requirements
1. A bachelor's degree.
2. Job offer from a company within the United States for a specialty position that matches your degree.

#### Why is H1B Popular?
1. For a company in the US, applying for H1B is generally quicker than applying for a US Green Card, so it is popular when they want to bring in an employee for a longer period.
2. H1B is open to nationals and citizens of any country, as opposed to other visa types that are only open to people with certain countries of citizenship.
3. H1B allows holders to stay for three years initially and can be easily extended to three more years after the first term.
4. H1B allows holders to move their status from one company to another and also allows its holders to work part-time and work for multiple employers at the same time.
5. The main benefit of H1B that attracts a large volume of applicants is the fact that it is a dual intent visa. This means that it allows its holders to seek permanent residency while under the H1B nonimmigrant status.

#### Caveats
Despite having a lot of advantages, applying for the H1B comes with its own set of caveats or disadvantages.

1. The biggest drawback of H1B is the fact that there is a limit on the number of petitions that are approved each year. Because of the large number of petitions each year, the USCIS has chosen to have all petitions entered into a lottery. Through this an annual general cap of 65,000 in first, and then run the remaining in the master’s-and-above 20,000 categories.
This means there is a strong likelihood that for any given year, your petition will not be selected. Once rejected, you will have to wait another year to submit another petition.
2. Because of its lottery, the deadlines for the H1B applications are very inflexible.
3. It is difficult to find an employer that would be willing to sponsor an employee for H1B, as the process can get expensive and is unreliable.

#### H1B Historic Timeline
![Timeline](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/1.png)
The timeline of relevant events is listed above. Sources for this information are from the New York times, government official documents from USCIS (U.S. Citizenship and Immigration Services).   


# Exploration

#### Purpose
The main purpose of our exploration was to examine and recognize the trends in H1B Visa and see how data-related jobs in the United States have changed over the past 5 years.

#### Dataset
To perform this analysis, we combined data sets of 5 different years from 2014 to 2018.
![df1](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/2.png)
![df2](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/3.png)

Column Name | Column Description
--- | ---
job_title	Job | title of the particular H1B application.
case_status |	Certified-withdrawn; Certified; Denied; Withdrawn; Rejected; Invalidated- we filter this data by certified as we only wish to keep the applications that were approved to be submitted.
employer_name	| Employer through which the H1B application was submitted.
prevailing_wage |	The annual salary of the job in a particular observation.
year | Year the particular H1B application was submitted.
worksite | Location of the worksite.
lon	| Longitudinal location of the worksite.
lat	| Latitudinal location of the worksite.
data_relation	| If the job title is data-related, then this will have “data-related” else “undefined.
data_job_title | This will be used to classify the data-related job titles into 4 different categories of business analysts, data analysts, data engineers, and data scientists.
stem | This is supposed to classify the h1b application into STEM or non-STEM based on another dataset to recognize its classification.
soc_code | SOC is a federal statistical standard used by federal agencies to classify workers into occupational categories to collect, calculate, or disseminate data.

#### Number of Applications Per State

We wanted to look at how the number of applications differed per state over the course of the last 5 years.
Here we can see that the states of California, Texas, New York, Michigan, Georgia, Pennsylvania, Florida, and Illinois are the states with the highest number of applications. The number of applicants is seen to increase over time (from 2015 to 2017) for Washington, Virginia and North Carolina. States that have the lowest number of applicants are Montana, Wyoming and South Dakota.


<iframe src="https://waittim.github.io/gallery/h1b-map.html" frameborder="0" width="700" height="435" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

# STEM

Instead of doing an overview of the actual data, we thought it to be better to first filter by STEM (Science, Technology, Engineering, and Management) related jobs. It was expected that the majority of the applications would be coming from STEM, but a confirmation was needed.

The following analysis was done to see the proportion of applicants for H1B that were in STEM fields vs non-STEM fields. This was done using the SOC (Standard Occupational Classification)  code associated with educational background. This was then cross-referenced (left-join) with a list of SOC codes that were considered to be STEM . We combined this with our analysis of the number of applicants per year as a sum just to see if some trends had changed.

![stem-nonstem](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/4.png "Figure 2: Number of applications per year. Proportion of STEM and non-STEM H1B Applicants.")

We observed (from Figure. 2) that the number of applications stays high as compared to the yearly cap of 85,000 applications that get approved. The number of applications also keeps increasing each year with only a slight dip in 2017. The changes in the total number of applications don’t seem to affect the proportion of STEM to non-STEM applications each year. This is also very interesting to note as the number of non-STEM jobs available in the United States is much higher than the number of STEM jobs.

This disproportionately high number might be attributed to the fact that foreign students with STEM degrees are more likely to pursue STEM fields. The reason for this is that USCIS allows foreign students who pursue a STEM degree during their academic career to stay within the United States for up to three years after they have graduated as opposed to a single year for those of non-STEM backgrounds. This means that during those 3 years, you will have three chances to apply for an H1B and would potentially be eligible to apply for permanent residency.  

Another reason why international students might want to pursue STEM would be the prevailing wages for STEM and non-STEM jobs.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/5.png "Figure 3: Modified box plot to show only the spread and the median of the
wage distribution between STEM and non-STEM.")

The medians of the prevailing wages of the STEM and non-STEM jobs have gotten wider apart but the median for the STEM is always higher than the non-STEM (Figure. 3). In 2018, we see the gap between the two to appear to be the widest.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/6.png "Figure 4: Density plot for the prevailing wages for STEM vs non-STEM jobs.")

It is visible from the density plot of the wage distribution of the year 2018 that the wages of the STEM jobs in 2018 are not only higher but the distribution is also tighter as compared to the distribution for the non-STEM jobs.

#### Top Jobs In STEM in 2018

What naturally followed after this was an analysis of what these STEM jobs were, to gain an understanding of why so many foreign students were attracted to them (Figure 5). Software developer and software engineer positions seem to be the top two jobs with the highest number of applications. This might be attributed to the tech boom of the last 5 years, which has greatly increased the demand for software developers.

Following right after are business analyst and programmer analyst positions. It is important to note that approximately 10 out of these 20 jobs could be associated with data-related jobs. Even if they were not explicitly mentioned as a data-related job, they have, in their job description, data-related roles.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/7.png "Figure 5: Top 20 jobs in STEM with the highest number of applications in 2018. All jobs are colored blue, data-related jobs are colored red.")

After recognizing the number of data-related jobs within the top 20 job titles in the last year, the next step was to break down what these data-related roles were and if we could combine them and/or break them down based on how complex we wanted our analysis to be.

# Data Related Jobs Trends

We created four categories of data-related jobs for this analysis. This categorization was based on the keywords in the job titles.

Data Job Title | Associated Keywords
--- | ---
Business Analyst |  “Business Intelligence”
Data Analyst | “EDA”, “Visualization”,  “Data aggregation”
Data Scientist | “Machine learning”, “Model”, “Algorithm”, “A/B testing”
Data Engineer | “Pipeline”, “Data lake”, “ETL”, “Database”, “Warehouse”

We combined machine learning and deep learning jobs into data science jobs, as they are highly correlated and it also made the following visualizations easier to look at. Since these data points were essentially just combined with another category, we need to note that the number of machine learning/deep learning jobs (with those explicit keywords as titles) have remained very few.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/8.png "Figure 6: Data related jobs and their four categories. Business Analysts having the highest number of applications and only going down after 2016.")

Two important things to notice here (Figure 6). Firstly, the total number of jobs for business analysts is much higher than the total number of jobs for other roles. There also seems to be a downward trend in the number of jobs for business analysts after 2016; however, the number of jobs within business analytics remains much higher than the number of jobs in any of the other categories in any of the years. Secondly, the number of jobs for data scientists, analysts and engineers are all showing an upward trend. There appears to be a higher number of jobs for data analysts as compared to data scientists and data engineers. A reason for this is that the role of data scientists only emerged recently and the number of jobs available in the industry has just recently, in the past couple of years, started growing.

#### Prevailing Wages Per Data Related Job Category

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/9.png "Figure 7: Prevailing wages for data-related jobs in 2018")

From the prevailing wages for the different categories that we have established, we see that the median salary (from Figure 7) for a data scientist is a lot higher for the median salary for the business analyst. This coincides with our earlier analysis when we saw that the number of applications for H1B is a lot higher than the number of job applications from a data scientist or analyst role. The higher number of jobs and lower salaries make it a good option for someone within data science to use that as an opportunity to get into the industry.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/10.png "Figure 8: Top 5 companies with the highest number of applications for data-related roles")

To get a general trend of what was going on in the industry for data-related roles, we look at five companies with the highest number of applications in the years 2014 to 2017 (Fig. 8). We notice here that despite expecting the highest number of applications to come from tech companies, it comes from 3 consulting firms and two tech companies.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/11.png "Figure 9: Infosys and the downward trend in job applications")

The company Infosys showed a very steep downward trend and also had the highest number of H1B applications in the year 2014 which was on a completely different scale as compared to other similar companies (Fig. 9). This drew the attention of our analysis because it was a highly abnormal trend, but upon deeper examination, it revealed a precautionary tale for foreign students trying to get jobs in the United States.

#### Story Behind Infosys

In 2013, Infosys agreed to pay $34 million to settle a lawsuit against them which claimed they were involved in fraud and abuse of the immigration process in the United States . Infosys brought foreign nationals into the country on visa types that are not authorized for employment in the United States. This means that the company was involved in fraudulent activity. The USCIS has been stricter on companies like Infosys (Wipro, Tata) because they have a history of trying to go around the system and abusing it to employ cheap labor. The denial rate  for these companies has been extremely high and can be seen to effectively reduce the total number of applications submitted through them over the course of the last 5 years.

#### Top Tech Companies

A natural assumption for someone entering the market as a data scientist would be that the top tech companies have the highest number of jobs for data-related roles. We examine the top tech giants that are
![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/12.png "Figure 10: Data related job trends in the top tech companies in the past 5 years")

There is a general upward trend to the number of data-related jobs for all tech companies, with Google hiring the least number of people within data-related capacities and Amazon hiring the most. While most companies are showing an upward trend, IBM shows a decreasing trend from 2015 to 2017.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/13.png "Microsoft") | ![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/14.png "Google")
a\) Microsoft | b\) Google
![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/15.png "Facebook") | ![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/16.png "Amazon ")
c\) Facebook | d\) Amazon

*Figure 11: Trends in data some of the top tech companies*

All of the tech companies show an increasing trend in the data-related. However, there are two companies that draw our attention. Google (Fig 11 (b)) has a much lower number of data-related jobs as compared to the other companies. This might be attributed to the fact that some jobs might have data-related roles even if they don’t have data-related titles. But overall, Google has very few explicit data roles and thus fewer opportunities for international students.

Another trend of interest is that of Amazon (Fig 11 (d)) which sees a decrease in the number of applications for data-related roles after the year 2017. This might be attributed to stricter H1B regulations implemented under Trump’s administration and also could be attributed to data scientist jobs doing jobs of data scientists.

#### IBM

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/17.png "Figure 12: IBM trends for data-related roles - (a)IBM Spaghetti plot for all jobs")

IBM H1B petitions see an overall decrease after the year 2017 (Fig 12 (a)). This is because of how Trump’s administration has affected the H1B denial rates. We can see that  IBM has an increasing denial rate that is not like those of tech firms. This can be attributed to the fact that IBM is not a traditional tech firm; it provides a lot of consulting services. Due to a stricter review, the H1B application process involves providing more information about the type of exact work a company is involved in, the projects and the subcontractors. This hinders non-tech companies from hiring more international students as it will be both expensive and cumbersome. These companies would rather hire US citizens with the same skills if they can avoid it and most of the time, a foreign employee can be replaced with a US citizen.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/18.png "Figure 12: IBM trends for data-related roles - (b)Data-related roles for IBM")

This downward trend is probably linked to IBM’s consulting sector combined with stricter government regulations . Despite this trend, the number of applications for specific data-related roles in IBM (Fig 12 (b)) seems to be unaffected by this downward trend.

#### Other Consulting Companies

It would make sense that other consulting or non-tech companies should show trends similar to that of IBM with a decreasing number of applications. And this can be seen in both Deloitte and Accenture (Fig. 13 (a) and (b). Even though Deloitte has been a major employer for data-related roles in the past 5 years, it has shown a sharp decrease in these roles after 2016 (Fig 13 (a)). This decline started before President Trump’s election around 2015, when stricter regulations were implemented on working offsite on H1B.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/19.png "Deloitte") | ![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/20.png "Accenture")
a\) Deloitte Consulting | b\) Accenture Consulting

*Figure 13: Consulting companies and the trends in data-related roles*

The worksite regulations implemented in 2015 can cause problems for consulting companies as a lot of consulting work may be off-site in another city and not in the official workplace. Also, consulting companies that deal with U.S. Federal Government might not hire international students as the work might require the workers to be U.S. citizens.

# Locations for Data-Related Jobs

#### Nationwide Overview

<iframe src="https://waittim.github.io/gallery/h1b-map-data.html" frameborder="0" width="700" height="435" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

This is an incomplete but interesting cartographic analysis (Fig. 14). The first thing we can see from here, however, is that the most number of applications in data-related roles are coming from (starting from the west coast to east) Washington, California, Texas, Illinois, Atlanta, Florida, New York, New Jersey, and Massachusetts.

Just because the colors seem similar for certain states in this diagram, does not mean that the numbers of data-related H1B applications are the same. They belong to the same interval or above a certain threshold. The numbers for the major states are as follows:
1.	California - 7,417 applications
2.	New York - 2516 applications
3.	Washington - 1428 applications
4.	Texas - 2499 applications
5.	New Jersey - 2007 applications
6.	Massachusetts - 1570 applications

Wyoming and Montana have 2 and 5 H1B applications, respectively,  in 2018. This indicates that these would be the worst states to apply for data-related jobs.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/21.png "Figure 15: Alluvial diagram showing the distribution of the number of applications from each role ")

Upon taking a deeper look at the different jobs and the top states for those jobs, we can see how the number of applications for the data-related roles is being distributed among the top states. What is interesting to note here is that the Business Analyst role is higher for almost all states except for the state of Michigan where the Data Analyst applications are higher than the Business Analyst applications. We can see the majority of Data Scientist applications are coming from California while Washington and New York follow right after.

#### Regions of the United States

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/22.png "Figure 16: 1 Point = 1 City. Color = Data position with the highest number of jobs in that city")
*Figure 16: 1 Point = 1 City. Color = Data position with the highest number of jobs in that city*

To find where would be best to apply based on the type of data role, a deeper analysis is needed into what cities would be best to apply to, based on the number of proportions of jobs available for each of the data roles. In Figure 16, each point is a city and the color of the city is given by what data-position provided the majority of the application in 2017 and 2018. Using two years for the analysis instead of one is better as it provides a better picture of the data-related jobs.  We can see lots of blue clusters forming on the east coast, while some black clusters forming in Michigan and more of a variety of colors in California in the Bay Area and Washington.

#### The Western United States

The Western United States has two main states of interest for data-related roles, Washington and California.
![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/23.png "Figure 17: State of Washington and data-related roles in that state ")

Washington has a significant amount of data-related roles with Seattle having a majority of Business Analyst applications and Redmond (red circle) has a higher number of data scientists. This may be because of the Amazon and Microsoft headquarters being located in Seattle and Redmond.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/24.png "Figure 18: The state of California and data-related roles in that state")

If pursuing a data scientist role or job title, state of California seems to have the most variety and also the highest number of applications for H1B applications for that role (668 H1B applications). The big red circles show that a large number of data scientists applied for H1B from the bay area (San Jose, San Francisco, and Oakland). This makes complete sense because of the presence of Silicon Valley, where most of the headquarters for tech companies are located, and the recent boom in data science jobs in the tech industry (cite).

#### The Northeastern United States

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/25.png "Figure 19: The Northeastern States and data-related roles in those states")

We see four main clusters on this map. Boston, New York, Philadelphia, and Washington DC. The majority of these clusters are blue as northeast has a relatively large number of finance and insurance companies (+ 22.7% relative as compared to other places in the United States) , and these companies have a large number of business analyst or data analytics positions as compared to other roles. The existence of some black clusters is an indication of this industry requiring data analysts.

#### The Midwestern United States

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/26.png "Figure 20: Midwestern states and data-related roles in those states")

The midwest shows relatively more black clusters as compared to any other region. There is a large black cluster in the state of Michigan indicating a significant number of data analyst positions, in Detroit. And a large blue cluster in Chicago indicating a large number of business analyst positions.

#### State of Tennessee

The final and most important analysis, relevant to the authors of this paper and the potential individuals reading it, is an analysis of the data-related job market for international students, using H1B, in the state of Tennessee.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/27.png "Figure 21: Data related jobs in the state of Tennessee ")

There are two major cities where you find the biggest clusters for data-related roles: Nashville and Memphis. Both these cities have applications mainly for business analytics. We can see some sprinkles of data analyst roles in other parts of the state, with one small dot representing data science applications around the Oak Ridge area. This is from an employer named Oak Ridge National Laboratory and they hire data scientists for the work and research that they perform.  

This does not make Tennessee the best state for foreign students who are pursuing data science; however, growth in data science jobs is projected over the next few years, due to tech companies moving to Tennessee.

![](https://github.com/waittim/waittim.github.io/raw/master/img/h1b/28.png "Figure 13: Proportion of data-related jobs as compared to other jobs")

Figure 13 shows that there has been a growth in data-related roles in the past 5 years, with 2018 showing the highest number of applications for data-related roles in the year 2018. This is promising, as it will mean a higher number of data-related roles that will hire and sponsor international students in the years to come.

# Conclusions

To reiterate, the purpose of this data exploration was to examine and recognize the trends in H1B visa applications and see how data-related jobs in the United States have changed over the past 5 years. This analysis can be used to assist international students in pursuing a data-related degree in determining what type of jobs they should apply for and where they should be considering moving to in the future if they wanted to stay within the United States.

We can gather from our analysis that among the four data-related job titles that we divided our dataset into (business analyst, data analyst, data engineers and data scientists), the highest number of jobs are available for the business analyst job title or job classifications. We also note that the salary for this job role is much lower as compared to the other data-related jobs. The barrier to entry for data scientists, for this specific role, might be a lot lower as compared to other roles. This is because there are a lot of jobs for data scientists, and potential employers would be more open to hiring data scientists from business backgrounds, as they would be able to perform well in roles associated with business analytics.

In terms of what type of company data scientists should apply for, we find that some big companies such as Google and Apple (shown in the final-report.Rmd), have fewer data-related jobs for international students despite being major tech companies. However, there does seem to be an upward trend in data-related jobs in the tech industry.

We can also see those consulting companies are harder to get jobs in for data-related roles, as they are more affected by governmental regulations and policies. These positions may be limited to U.S. citizens or permanent residents. It is also cheaper for these companies to hire non-foreign workers, as consulting roles are not as profitable as purely technical roles and therefore may not need extremely specialized foreign talent (for those companies).

The location analysis will help international students pursuing a data-related degree, to find the most probable location they should move to based on the type of data-related role they want to pursue. The best location to find a job in business analytics is in the northeastern states as they have a large number of finance and insurance companies. However, there is no shortage of business analytics roles, since these are very commonly found in almost every company. So almost every state has a large number of these roles. Nevertheless, it is still important to note that the total number of applications for H1B in business analytics is showing a generally downward trend.

The best location to find a job as a data analyst or in data analytics in the Northeast or the Midwest, as seen from the clusters in the maps that we explored. However, since a large number of job applications come from California, almost all of these roles are plentiful in the state of California. California is also where a large number of specific data scientists and data engineering roles are available, specifically in the bay area where a large number of tech companies are located. The state of Washington (Seattle and Redmond area) is good to find data engineering and data science jobs as well because of the existence of Microsoft and Amazon.

Finally, although Tennessee is not the best for international students pursuing data-related roles, there does seem to be a potential for growth since tech giants such as Amazon and Microsoft are creating more opportunities for jobs in the Nashville area in the future.


# Slides
<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vQR_hrMRbhVNpoudmrkJRcPi3lTcSG0g1lYYnMOElPjTcrC_y1Bxk16DdwxUCLruMuoQEPX0n04Zc8k/embed?start=false&loop=false&delayms=3000" frameborder="0" width="700" height="423" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

*Hint: Project GitHub page: [H1B-visas-analysis](https://github.com/waittim/H1B-visas-analysis)*
