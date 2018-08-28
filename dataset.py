# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 22:18
# @Author  : zhoujun
import pathlib
import numpy as np
from mxnet import image, nd
import cv2
from mxnet.gluon.data import Dataset


class Gluon_OCRDataset(Dataset):
    def __init__(self, data_txt: str, data_shape: tuple, img_channel: int, num_label: int,
                 alphabet: str):
        """
        数据集初始化
        :param data_txt: 存储着图片路径和对于label的文件
        :param data_shape: 图片的大小(w,h)
        :param img_channel: 图片通道数
        :param num_label: 最大字符个数,应该和网络最终输出的序列宽度一样
        :param alphabet: 字母表
        """
        super(Gluon_OCRDataset, self).__init__()
        self.data_list = []
        with open(data_txt, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n').replace('.jpg ', '.jpg\t').split('\t')
                img_path = pathlib.Path(line[0])
                if img_path.exists() and img_path.stat().st_size > 0 and line[1]:
                    self.data_list.append((line[0], line[1]))
        self.data_shape = data_shape
        self.img_channel = img_channel
        self.num_label = num_label
        self.alphabet = alphabet
        self.label_dict = {}
        for i, char in enumerate(self.alphabet):
            self.label_dict[char] = i

    def __getitem__(self, idx):
        img_path, label = self.data_list[idx]
        label = label.replace(' ','')
        try:
            label = self.label_enocder(label)
        except Exception as e:
            print(img_path, label)
        img = self.pre_processing(img_path)
        return img, label

    def __len__(self):
        return len(self.data_list)

    def label_enocder(self, label):
        """
        对label进行处理，将输入的label字符串转换成在字母表中的索引
        :param label: label字符串
        :return: 索引列表
        """
        tmp_label = nd.zeros(self.num_label, dtype=np.float32) - 1
        for i, ch in enumerate(label):
            tmp_label[i] = self.label_dict[ch]
        return tmp_label

    def pre_processing(self, img_path):
        """
        对图片进行处理，先按照高度进行resize，resize之后如果宽度不足指定宽度，就补黑色像素，否则就强行缩放到指定宽度
        :param img_path: 图片地址
        :return:
        """
        img = image.imdecode(open(img_path, 'rb').read(), 1 if self.img_channel == 3 else 0)
        h, w = img.shape[:2]
        ratio_h = float(self.data_shape[0]) / h
        new_w = int(w * ratio_h)
        if new_w < self.data_shape[1]:
            img = image.imresize(img, w=new_w, h=self.data_shape[0])
            step = nd.zeros((self.data_shape[0], self.data_shape[1] - new_w, self.img_channel), dtype=img.dtype)
            img = nd.concat(img, step, dim=1)
        else:
            img = image.imresize(img, w=self.data_shape[1], h=self.data_shape[0])
        return img


if __name__ == '__main__':
    import keys
    import time
    from mxnet.gluon.data import DataLoader
    from matplotlib import pyplot as plt
    from mxnet.gluon.data.vision.transforms import ToTensor
    from predict import decode

    alphabet = keys.zyqd_alphabet
    dataset = Gluon_OCRDataset('/data1/fxw/crnn_train/test_new.txt', (32, 320), 3, 81, alphabet)

    data_loader = DataLoader(dataset.transform_first(ToTensor()), 128, shuffle=True,num_workers=6)
    start = time.time()
    s = dataset.__len__()//128
    for i, (img, label) in enumerate(data_loader):
        print(i,s)
        # print(i, all, time.time() - start)
        # start = time.time()
        # # label = label[0].asnumpy()
        # result = decode(label.asnumpy(), alphabet)
        # img1 = img[0].asnumpy().transpose(1, 2, 0)
        # print(result[0])
        # plt.title(result[0])
        # plt.imshow(img1)
        # plt.show()
        # break
