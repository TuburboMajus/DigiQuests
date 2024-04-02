# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_Event
class Event(Entity):
	ENTITY_NAME = "event"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"task","type":UUID4Attribute,"required":True},
		{"name":"quest","type":UUID4Attribute,"required":True},
		{"name":"start_date","type":DateTimeAttribute,"required":True},
		{"name":"end_date","type":DateTimeAttribute,"required":True},
		{"name":"synced","type":BooleanAttribute,"required":False, "default_value": False},
	]
# ** EndSection ** Entity_Event


# ** Section ** Entity_GEvent
class GEvent(Entity):
	ENTITY_NAME = "gevent"
	ATTRIBUTES = [
		{"name":"event","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"owner","type":UUID4Attribute,"required":True, "is_nullable":False},
		{"name":"gcalendar_id","type":StringAttribute,"required":True, "max_length":200, "is_nullable":False},
		{"name":"gevent_id","type":StringAttribute,"required":True, "max_length":200, "is_nullable":False}
	]
# ** EndSection ** Entity_GEvent