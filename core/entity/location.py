# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_Location
class Location(Entity):
	ENTITY_NAME = "location"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"name","type":StringAttribute,"max_length":100, "required":True,"is_nullable":False},
		{"name":"address","type":StringAttribute,"max_length":250,"required":True,"non_empty":True,"is_nullable":False},
		{"name":"label","type":StringAttribute,"max_length":50}
	]
# ** EndSection ** Entity_Location