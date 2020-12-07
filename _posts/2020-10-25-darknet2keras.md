---
layout:     post
title:      Darknet to Keras Transformation
subtitle:   New version based on TensorFlow 2.0
date:       2020-10-25
author:     Zekun
header-img: img/post-deep-brain.jpg
catalog: true
tags:
    - Object Detection
    - Deep Learning
    - Python
    - Keras
---

In the process of completing the mask detection project recently, I tried to convert Darknet into a Keras model. In other words, to convert the `.cfg` file and the `.weights` file into a `.h5` file. 

There are actually some ready-made codes online to complete this process, such as [YAD2K](https://github.com/allanzelener/YAD2K) and [keras-yolo3](https://github.com/qqwweee/keras-yolo3). However, the most recent update of these repository was at least three years ago. The Keras used is an older version. The new version of Keras has been embedded in TensorFlow 2.0. 

Secondly, during the converting, I met a issue called `buffer is too small for requested array`. After check the transformation process, I found it cannot handle group convolutional layers. 

Therefore, after referring to the relevant information on the Internet, I modified the `convert.py` to be based on TensorFlow 2.0 and able to deal with group in convolutional layers.

Regarding the modification of the grouped convolutional layer, the main part of the code is as follows:

```python
        groups = int(block['groups']) if 'groups' in block else 1
        # Other content...

        weights_shape = (size, size, int(prev_layer_shape[-1]/groups), filters)
        # Other content...
        
        conv_layer = (Conv2D(
                filters, (size, size),
                strides=(stride, stride),
                kernel_regularizer=l2(self.weight_decay),
                use_bias=not batch_normalize,
                weights=conv_weights,
                activation=act_fn,
                groups=groups,
                padding=padding))(self.prev_layer)

```

The entire code of the `convert.py` is as follows:

```python
import os
import io
import argparse
import configparser


import numpy as np
from tensorflow.keras import backend as K
from tensorflow.keras.layers import (Conv2D, Input, ZeroPadding2D, Add, UpSampling2D, MaxPooling2D, Concatenate, Dropout, LeakyReLU, BatchNormalization)
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2



def parser():
    parser = argparse.ArgumentParser(description="Darknet\'s yolov3.cfg and yolov3.weights \
                                      converted into Keras\'s yolov3.h5!")
    parser.add_argument('-cfg_path', help='yolov3.cfg')
    parser.add_argument('-weights_path', help='yolov3.weights')
    parser.add_argument('-output_path', help='yolov3.h5')
    parser.add_argument('-weights_only', action='store_true',help='only save weights in yolov3.h5')
    return parser.parse_args()


class WeightLoader(object):

    def __init__(self,weight_path):
        self.fhandle = open(weight_path,'rb')
        self.read_bytes = 0

    def parser_buffer(self,shape,dtype='int32',buffer_size=None):
        self.read_bytes += buffer_size
        return np.ndarray(shape=shape,
                          dtype=dtype,
                          buffer=self.fhandle.read(buffer_size) )

    def head(self):

        major, minor, revision = self.parser_buffer(
                                   shape=(3,),
                                   dtype='int32',
                                   buffer_size=12)

        if major*10+minor >= 2 and major < 1000 and minor < 1000:
            seen = self.parser_buffer(
                             shape=(1,),
                             dtype='int64',
                             buffer_size=8)
        else:
            seen = self.parser_buffer(
                             shape=(1,),
                             dtype='int32',
                             buffer_size=4)

        return major, minor, revision, seen

    def close(self):
        self.fhandle.close()

class DarkNetParser(object):
    def __init__(self, cfg_path, weights_path):

        self.block_gen = self._get_block(cfg_path)
        self.weight_loader = WeightLoader(weights_path)
        
        major, minor, revision, seen = self.weight_loader.head()
        print('weights header: ',major, minor, revision, seen)

        self.input_layer = Input(shape=(None, None, 3))
        self.out_index = []
        self.prev_layer = self.input_layer
        self.all_layers = []
        self.count = [0,0]

    
    def _get_block(self,cfg_path):

        block = {}
        with open(cfg_path,'r', encoding='utf-8') as fr:
            for line in fr:
                line = line.strip()
                if '[' in line and ']' in line:        
                    if block:
                        yield block
                    block = {}
                    block['type'] = line.strip(' []')
                elif not line or '#' in line:
                    continue
                else:
                    key,val = line.strip().replace(' ','').split('=')
                    key,val = key.strip(), val.strip()
                    block[key] = val

            yield block


    def conv(self, block):
        '''When reading darknet's yolov3.weights file, the order is
          1 - bias；
          2 - If there is a bn, read scale，mean，var 
          3 - Get the weights
        '''
        # Darknet serializes convolutional weights as:

        # [bias/beta, [gamma, mean, variance], conv_weights]

        self.count[0] += 1
        # read conv block

        filters = int(block['filters'])
        size = int(block['size'])
        stride = int(block['stride'])
        pad = int(block['pad'])
        activation = block['activation']
        groups = int(block['groups']) if 'groups' in block else 1
        
        padding = 'same' if pad == 1 and stride == 1 else 'valid'
        batch_normalize = 'batch_normalize' in block
        
        prev_layer_shape = K.int_shape(self.prev_layer)
        weights_shape = (size, size, int(prev_layer_shape[-1]/groups), filters)
        darknet_w_shape = (filters, weights_shape[2], size, size)
        weights_size = np.product(weights_shape)

        print('+',self.count[0],'conv2d', 
              'bn' if batch_normalize else ' ',
              activation,
              weights_shape)

        # Read the bias

        conv_bias = self.weight_loader.parser_buffer(
                                 shape=(filters,),
                                 dtype='float32',
                                 buffer_size=filters*4)
 
        # If there is a bn, read scale，mean，var 

        if batch_normalize:
            bn_weight_list = self.bn(filters, conv_bias)

        # Read the weights

        conv_weights = self.weight_loader.parser_buffer(
                              shape=darknet_w_shape,
                              dtype='float32',
                              buffer_size=weights_size*4)

        # DarkNet conv_weights are serialized Caffe-style:

        # (out_dim, in_dim, height, width)

        # We would like to set these to Tensorflow order:

        # (height, width, in_dim, out_dim)

        conv_weights = np.transpose(conv_weights, [2, 3, 1, 0])
        conv_weights = [conv_weights] if batch_normalize else \
                              [conv_weights, conv_bias]

        act_fn = None
        if activation == 'leaky':
            pass
        elif activation != 'linear':
            raise

        if stride > 1:
            self.prev_layer = ZeroPadding2D(((1,0),(1,0)))(self.prev_layer)

        conv_layer = (Conv2D(
                filters, (size, size),
                strides=(stride, stride),
                kernel_regularizer=l2(self.weight_decay),
                use_bias=not batch_normalize,
                weights=conv_weights,
                activation=act_fn,
                groups=groups,
                padding=padding))(self.prev_layer)

        if batch_normalize:
             conv_layer = BatchNormalization(weights=bn_weight_list)(conv_layer)
        self.prev_layer = conv_layer

        if activation == 'linear':
            self.all_layers.append(self.prev_layer)
        elif activation == 'leaky':
            act_layer = LeakyReLU(alpha=0.1)(self.prev_layer)
            self.prev_layer = act_layer
            self.all_layers.append(act_layer)


    def bn(self,filters,conv_bias):
        '''bn has 4 parameters. they're bias, scale, mean, var,
           The bias has been read, and the remaining three are read here, scale, mean, var '''
           
        bn_weights = self.weight_loader.parser_buffer(
                              shape=(3,filters),
                              dtype='float32',
                              buffer_size=(filters*3)*4)
        # scale, bias, mean,var
        bn_weight_list = [bn_weights[0],
                          conv_bias,
                          bn_weights[1],
                          bn_weights[2] ]
        return bn_weight_list
       
    def maxpool(self,block):
        size = int(block['size'])
        stride = int(block['stride'])
        maxpool_layer = MaxPooling2D(pool_size=(size,size),
                        strides=(stride,stride),
                        padding='same')(self.prev_layer)
        self.all_layers.append(maxpool_layer)
        self.prev_layer = maxpool_layer

    def shortcut(self,block):
        index = int(block['from'])
        activation = block['activation']
        assert activation == 'linear', 'Only linear activation supported.'
        shortcut_layer = Add()([self.all_layers[index],self.prev_layer])
        self.all_layers.append(shortcut_layer)
        self.prev_layer = shortcut_layer

    def route(self,block):
        layers_ids = block['layers']
        ids = [int(i) for i in layers_ids.split(',')]
        layers = [self.all_layers[i] for i in ids]
        if len(layers) > 1:
            print('Concatenating route layers:', layers)
            concatenate_layer = Concatenate()(layers)
            self.all_layers.append(concatenate_layer)
            self.prev_layer = concatenate_layer
        else:
            skip_layer = layers[0]
            self.all_layers.append(skip_layer)
            self.prev_layer = skip_layer

    def upsample(self,block):
        stride = int(block['stride'])
        assert stride == 2, 'Only stride=2 supported.'
        upsample_layer = UpSampling2D(stride)(self.prev_layer)
        self.all_layers.append(upsample_layer)
        self.prev_layer = self.all_layers[-1]
    
    def yolo(self,block):
        self.out_index.append(len(self.all_layers)-1)
        self.all_layers.append(None)
        self.prev_layer = self.all_layers[-1]

    def dropout(self,block):
        prob = float(block['probability'])
        dropout_layer = Dropout(prob)(self.prev_layer)
        self.all_layers.append(dropout_layer)
        self.prev_layer = dropout_layer

    def net(self, block):
        self.weight_decay = float(block['decay'])


    def create_and_save(self,weights_only,output_path):
        if len(self.out_index) == 0:
            self.out_index.append( len(self.all_layers)-1 )

        output_layers = [self.all_layers[i] for i in self.out_index]
        model = Model(inputs=self.input_layer,
                      outputs=output_layers)
        print(model.summary())

        if weights_only:
            model.save_weights(output_path)
            print('Saved Keras weights to {}'.format(output_path))
        else:
            model.save(output_path)
            print('Saved Keras model to {}'.format(output_path))

    def close(self):
        self.weight_loader.close()
        

def main():

    args = parser()
    print('loading weights...')

    cfg_parser = DarkNetParser(args.cfg_path,args.weights_path)

    print('creating keras model...')

    layers_fun = {'convolutional':cfg_parser.conv,
                 'net':cfg_parser.net,
                 'yolo':cfg_parser.yolo,
                 'route':cfg_parser.route,
                 'upsample':cfg_parser.upsample,
                 'maxpool':cfg_parser.maxpool,
                 'shortcut':cfg_parser.shortcut,
                 'dropout':cfg_parser.dropout
                 }

    print('Parsing Darknet config.')
    for index,block in enumerate(cfg_parser.block_gen):
        type = block['type']
        layers_fun[type](block)

    cfg_parser.create_and_save(args.weights_only, args.output_path)
    cfg_parser.close()
        

if __name__ == '__main__':
    main()

```

Please save the code and rename it to `convert.py`. Usage is the same as in keras-yolo3:

```
python convert.py -w yolov3.cfg yolov3.weights model_data/yolov3.h5
```

This time, no buffer issue.



--- 
*Note: Thanks to the articles "[模型转换[yolov3模型在keras与darknet之间转换]](https://www.cnblogs.com/shouhuxianjian/p/10567201.html)" for the help in the compilation process.*
