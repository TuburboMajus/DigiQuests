# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_UserGCalendar
class UserGCalendar(Entity):
	ENTITY_NAME = "userGCalendar"
	ATTRIBUTES = [
		{"name":"user","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"calendar","type":StringAttribute,"required":True,"non_empty":True,"is_nullable":False},
		{"name":"sync","type":BooleanAttribute,"is_nullable":False, "default_value": True}
	]
# ** EndSection ** Entity_UserGCalendar