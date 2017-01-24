# -*- coding: utf-8 -*-
# from: https://github.com/ytyng/python-memoized-property

"""
property デコレータの代わりに使う。
関数の実行を1度だけ行い、計算結果をインスタンス変数として格納しておく。
再度呼び出しが行われた場合、関数をコールせず、インスタンス変数から結果を返す。

slots が定義されているとうまくいかないかもしれない。

class Hoge(object):

    @memoized_property
    def calc(self):
        some cord....

一応、セッターなんかも設定できるようにしたが未テスト
セッター、デリーターのコールでキャッシングしてるクラス変数を削除するので、
その後にゲッターがコールされると再計算を行う…はず。
"""

class memoized_property(object):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        if doc is None and fget is not None and hasattr(fget, "__doc__"):
            doc = fget.__doc__
        self.__get = fget
        self.__set = fset
        self.__del = fdel
        self.__doc__ = doc
        if fget is not None:
            self._attr_name = '___'+fget.func_name

    def __get__(self, inst, type=None):
        if inst is None:
            return self

        try:
            return getattr(inst, self._attr_name)
        except AttributeError:
            if self.__get is None:
                raise AttributeError, "unreadable attribute"

            result = self.__get(inst)
            setattr(inst, self._attr_name, result)

        return result


    def __set__(self, inst, value):
        if self.__set is None:
            raise AttributeError, "can't set attribute"
        delattr(inst, self._attr_name)
        return self.__set(inst, value)

    def __delete__(self, inst):
        if self.__del is None:
            raise AttributeError, "can't delete attribute"
        delattr(inst, self._attr_name)
        return self.__del(inst)


def memoized_property_set(inst, func_name, value):
    """
    memoized_property用の属性に値をセット。
    次に memoized_property デコレータがついたプロパティから値を読み出す時、
    ここで保存している値が使われる
    """
    if isinstance(func_name, basestring):
        property_name = '___' + func_name
    elif hasattr(func_name, 'func_name'):
        property_name = '___' + func_name.func_name
    else:
        raise
    setattr(inst, property_name, value)
