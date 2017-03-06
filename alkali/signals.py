from blinker import signal

model_creation   = signal('model_creation' , doc = 'called when a new Model class is created (not an instance)')
creation         = signal('creation'       , doc = 'called when a new Model instance is created')

field_update = signal('field_update', doc = 'called when a model field is set')

pre_save    = signal('pre_save'   , doc = 'called before an Model object is saved')
post_save   = signal('post_save'  , doc = 'called after an Model object is saved')

pre_delete  = signal('pre_delete' , doc = 'called before an Model object is deleted')
post_delete = signal('post_delete', doc = 'called after an Model object is deleted')

pre_load    = signal('pre_load'   , doc = 'called before all Model objects are loaded from disk')
post_load   = signal('post_load'  , doc = 'called after all Model objects are loaded from disk')

pre_store   = signal('pre_store'  , doc = 'called before all Model objects are stored to disk')
post_store  = signal('post_store' , doc = 'called after all Model objects are stored to disk')

# def callback(sender, instance, **kw):
#     print str(sender)
#
# blinker.signal('pre_save').connect(callback)
