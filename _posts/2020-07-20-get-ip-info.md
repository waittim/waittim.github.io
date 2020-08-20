---
layout:     post
title:      Note - How to get information from IP?
subtitle:   geoip2 module introduction
date:       2020-07-20
author:     Zekun
header-img: img/post-python.jpg
catalog: true
tags:
    - Feature Engineering
    - Python
    - IP
---


The process of getting IP information is done based on [GeoIP2 Databases](https://www.maxmind.com/en/geoip2-databases). I Used the [MaxMind GeoIP2 Python API](https://geoip2.readthedocs.io/en/latest/) for IP information queries. The Github page for the API is [GeoIP2-python](https://github.com/maxmind/GeoIP2-python).

You need to download [GeoLite2-City.mmdb](https://github.com/waittim/waittim.github.io/raw/master/gallery/GeoLite2-City.mmdb) as data source and install **geoip2** module before you can use it.

For complete information, see [MaxMind - GeoIP2 Downloadable Databases](https://dev.maxmind.com/geoip/geoip2/downloadable/).

### Installation


```python
!pip install geoip2

# For Chinese user, you can choose tsinghua mirrors

#!pip install -i https://pypi.tuna.tsinghua.edu.cn/simple geoip2
```

### Usage

First, we should import the geoip2 module.
We are using the free downloaded data, therefore, please import *geoip2.database* .


```python
import geoip2.database
```


```python
ip = '129.59.93.0' # The IP of Vanderbilt Univeristy

reader = geoip2.database.Reader('GeoLite2-City.mmdb')
response = reader.city(ip)
reader.close()
```

all of the results were reserved in the *response*.


```python
response
```




    geoip2.models.City({'city': {'geoname_id': 4644585, 'names': {'de': 'Nashville', 'en': 'Nashville', 'es': 'Nashville', 'fr': 'Nashville', 'ja': 'ナッシュビル', 'pt-BR': 'Nashville', 'ru': 'Нашвилл', 'zh-CN': '纳什维尔'}}, 'continent': {'code': 'NA', 'geoname_id': 6255149, 'names': {'de': 'Nordamerika', 'en': 'North America', 'es': 'Norteamérica', 'fr': 'Amérique du Nord', 'ja': '北アメリカ', 'pt-BR': 'América do Norte', 'ru': 'Северная Америка', 'zh-CN': '北美洲'}}, 'country': {'geoname_id': 6252001, 'iso_code': 'US', 'names': {'de': 'USA', 'en': 'United States', 'es': 'Estados Unidos', 'fr': 'États-Unis', 'ja': 'アメリカ合衆国', 'pt-BR': 'Estados Unidos', 'ru': 'США', 'zh-CN': '美国'}}, 'location': {'accuracy_radius': 20, 'latitude': 36.066, 'longitude': -86.9659, 'metro_code': 659, 'time_zone': 'America/Chicago'}, 'postal': {'code': '37221'}, 'registered_country': {'geoname_id': 6252001, 'iso_code': 'US', 'names': {'de': 'USA', 'en': 'United States', 'es': 'Estados Unidos', 'fr': 'États-Unis', 'ja': 'アメリカ合衆国', 'pt-BR': 'Estados Unidos', 'ru': 'США', 'zh-CN': '美国'}}, 'subdivisions': [{'geoname_id': 4662168, 'iso_code': 'TN', 'names': {'en': 'Tennessee', 'es': 'Tennessee', 'fr': 'Tennessee', 'ja': 'テネシー州', 'pt-BR': 'Tenessi', 'ru': 'Теннесси', 'zh-CN': '田纳西州'}}], 'traits': {'ip_address': '129.59.93.0', 'prefix_len': 20}}, ['en'])



Let me re-format it to make it understandable.

{'city': 
    {'geoname_id': 4644585, 
     'names': {'de': 'Nashville', 'en': 'Nashville', 'es': 'Nashville', 'fr': 'Nashville', 'ja': 'ナッシュビル', 'pt-BR': 'Nashville', 'ru': 'Нашвилл', 'zh-CN': '纳什维尔'}
     }, 
 'continent': 
    {'code': 'NA', 
     'geoname_id': 6255149, 
     'names': {'de': 'Nordamerika', 'en': 'North America', 'es': 'Norteamérica', 'fr': 'Amérique du Nord', 'ja': '北アメリカ', 'pt-BR': 'América do Norte', 'ru': 'Северная Америка', 'zh-CN': '北美洲'}
     }, 
 'country': 
    {'geoname_id': 6252001, 
     'iso_code': 'US', 
     'names': {'de': 'USA', 'en': 'United States', 'es': 'Estados Unidos', 'fr': 'États-Unis', 'ja': 'アメリカ合衆国', 'pt-BR': 'Estados Unidos', 'ru': 'США', 'zh-CN': '美国'}
     }, 
 'location': 
    {'accuracy_radius': 20, 
     'latitude': 36.066, 
     'longitude': -86.9659, 
     'metro_code': 659, 
     'time_zone': 'America/Chicago'
     }, 
 'postal': 
    {'code': '37221'}, 
 'registered_country': 
    {'geoname_id': 6252001, 
     'iso_code': 'US', 
     'names': {'de': 'USA', 'en': 'United States', 'es': 'Estados Unidos', 'fr': 'États-Unis', 'ja': 'アメリカ合衆国', 'pt-BR': 'Estados Unidos', 'ru': 'США', 'zh-CN': '美国'}
     }, 
 'subdivisions': 
    [{'geoname_id': 4662168, 
      'iso_code': 'TN', 
      'names': {'en': 'Tennessee', 'es': 'Tennessee', 'fr': 'Tennessee', 'ja': 'テネシー州', 'pt-BR': 'Tenessi', 'ru': 'Теннесси', 'zh-CN': '田纳西州'}
      }],
 'traits': {'ip_address': '129.59.93.0', 'prefix_len': 20}
}, 
['en']

There are some example to use the *response*:


```python
response.country.iso_code

#'US'
```



```python
response.country.name

#'United States'
```



```python
response.country.names['zh-CN']

#'美国'
```



```python
response.subdivisions.most_specific.name

#'Tennessee'
```



```python
response.subdivisions.most_specific.iso_code

#'TN'
```



```python
response.city.name

#'Nashville'
```



```python
response.postal.code

#'37221'
```



```python
response.location.latitude

#36.066
```



```python
response.location.longitude

#-86.9659
```



```python
response.traits.network

#IPv4Network('129.59.80.0/20')
```


