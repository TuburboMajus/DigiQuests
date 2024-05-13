# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_Storyline
class Storyline(Entity):
	ENTITY_NAME = "storyline"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"title","type":StringAttribute,"required":True,"non_empty":True,"max_length":100,"is_nullable":False}
	]
# ** EndSection ** Entity_Storyline


# ** Section ** Entity_Quest
class Quest(Entity):
	ENTITY_NAME = "quest"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"storyline","type":UUID4Attribute},
		{"name":"owner","type":UUID4Attribute,"required":True,"is_nullable":False},
		{"name":"title","type":StringAttribute,"required":True,"non_empty":True,"max_length":100,"is_nullable":False},
		{"name":"description","type":StringAttribute,"max_length":500},
		{"name":"complete","type":BooleanAttribute, "is_nullable": False, "default_value": False},
		{"name":"archived","type":BooleanAttribute, "is_nullable": False, "default_value": False},
		{"name":"reccurence","type":IntegerAttribute, "is_nullable": False, "default_value": 0},
		{"name":"reccurence_config","type":StringAttribute,"max_length":250, "is_nullable": True}
	]

	RECCURENCES = {
		"complete_once":0
	}
# ** EndSection ** Entity_Quest


# ** Section ** Entity_Task
class Task(Entity):
	ENTITY_NAME = "task"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"quest","type":UUID4Attribute,"required":True,"is_nullable":False},
		{"name":"task_order","type":IntegerAttribute,"required":True,"is_nullable":False},
		{"name":"content","type":StringAttribute,"required":True,"non_empty":True,"max_length":200,"is_nullable":False},
		{"name":"complete","type":BooleanAttribute, "is_nullable": False, "default_value": False}
	]
# ** EndSection ** Entity_Task


# ** Section ** Entity_TaskMonitor
class TaskMonitor(Entity):
	ENTITY_NAME = "task"
	ATTRIBUTES = [
		{"name":"id","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"task","type":UUID4Attribute,"required":True,"is_nullable":False},
		{"name":"type","type":StringAttribute,"required":True,"is_nullable":False},
		{"name":"params","type":StringAttribute,"max_length":2000}
	]
# ** EndSection ** Entity_TaskMonitor


# ** Section ** Entity_ActiveQuest
class ActiveQuest(Entity):
	ENTITY_NAME = "activeQuest"
	ATTRIBUTES = [
		{"name":"user","type":UUID4Attribute,"required":True,"is_id":True,"is_nullable":False},
		{"name":"quest","type":UUID4Attribute,"required":True,"is_nullable":False}
	]
# ** EndSection ** Entity_ActiveQuest

