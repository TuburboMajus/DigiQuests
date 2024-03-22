# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_ResourceKey
class ResourceKey(Entity):
	ENTITY_NAME = "resourceKey"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"resource","type":UUID4Attribute,"required":True,"is_nullable":False},
		{"name":"resource_type","type":StringAttribute,"required":True,"non_empty":True,"is_nullable":False},
		{"name":"user","type":UUID4Attribute,"required":True},
		{"name":"resource_key","type":StringAttribute,"required":True,"is_nullable":False}
	]
# ** EndSection ** Entity_ResourceKey