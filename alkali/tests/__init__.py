from alkali.model import Model
from alkali import fields

class EmptyModel(Model):
    pass

class MyModel( Model ):
    class Meta:
        ordering = ['int_type','str_type','dt_type']

    int_type = fields.IntField(primary_key=True)
    str_type = fields.StringField()
    dt_type  = fields.DateTimeField()

    @property
    def iter_type(self):
        return [self.int_type]

class MyMulti(Model):
    pk1 = fields.IntField(primary_key=True)
    pk2 = fields.IntField(primary_key=True)
    other = fields.StringField()
