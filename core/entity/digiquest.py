# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_DigiQuest
class DigiQuest(Entity):
	ENTITY_NAME = "digiQuest"
	ATTRIBUTES = [
		{"name":"version","type":StringAttribute,"required":True,"is_id":True,"non_empty":True,"is_nullable":False}
	]
# ** EndSection ** Entity_DigiQuest
