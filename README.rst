simpleflow
==========

通用工作流数库

主要代码基于Openstack Mitaka中的taskflow 2.14

python2.7以上networkx使用>1.10的官方版即可

python2.6需要修改networkx 1.9.1部分代码以支持有序字典,否则linear flow中的任务会应为添加顺序不正确报错

可以直接使用已经修改好的版本https://github.com/lolizeppelin/networkx