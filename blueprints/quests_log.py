from flask import Blueprint, Response, current_app, request, render_template, abort, redirect
from flask_login import current_user, login_required

from temod.base.condition import Equals, Or, In 
from temod.base.attribute import UUID4Attribute

from datetime import datetime
from pathlib import Path

import traceback
import shutil
import json
import os


def setup(configuration):
	default = {
		"templates_folder": "quests"
	}
	quests_log_blueprint.configuration = {
		key: configuration.get(key, value) for key,value in default.items()
	}
	return quests_log_blueprint


def get_configuration(config):
	try:
		return quests_log_blueprint.configuration.get(config)
	except:
		if not hasattr(quests_log_blueprint,"configuration"):
			setup({})
			return get_configuration(config)
		raise


quests_log_blueprint = Blueprint('quests_log', __name__)
quests_log_blueprint.setup = setup


@quests_log_blueprint.route("/quests",methods=["GET"])
@login_required
def getQuests():
	keys = list(ResourceKey.storage.list(
		Or(Equals(UUID4Attribute("user",value=current_user['idU'])),Equals(UUID4Attribute("user",value=None))),
		resource_type="quest"
	))

	incomplete_quests = []; complete_quests = []
	if len(keys) > 0:
		incomplete_quests = list(Quest.storage.list(
			In("id",*[UUID4Attribute("id",value=key['resource']) for key in keys]),
			complete=False,
			archived=False
		))
		complete_quests = list(Quest.storage.list(
			In("id",*[UUID4Attribute("id",value=key['resource']) for key in keys]),
			complete=True,
			archived=False
		))

	active_quest = ActiveQuest.storage.get(user=current_user['id'])
	selected_quest_id = None; default_quest = None
	if active_quest is not None:
		default_quest = active_quest['quest']
	selected_quest_id = request.args.get("quest",default_quest)

	selected_quest = None; selected_quest_tasks = []; selected_quest_key = None
	if selected_quest_id is not None:
		selected_quest = Quest.storage.get(id=selected_quest_id)
		selected_quest_tasks = sorted(Task.storage.list(quest=selected_quest_id),key=lambda t:t['task_order'])
		selected_quest_key = [key for key in keys if key['resource'] == selected_quest_id][0]

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('list.html')),
		active_quest=active_quest,
		quests_templates=templates_folder,
		selected_quest=selected_quest,
		selected_quest_tasks=selected_quest_tasks,
		selected_quest_key=selected_quest_key,
		incomplete_quests=incomplete_quests,
		complete_quests=complete_quests,
		is_archive=False
	)


@quests_log_blueprint.route("/quests/archived",methods=["GET"])
@login_required
def getArchivedQuests():
	keys = list(ResourceKey.storage.list(
		Or(Equals(UUID4Attribute("user",value=current_user['idU'])),Equals(UUID4Attribute("user",value=None))),
		resource_type="quest"
	))

	archived_quests = list(Quest.storage.list(
		In("id",*[UUID4Attribute("id",value=key['resource']) for key in keys]),
		archived=True
	))

	selected_quest = None; selected_quest_tasks = []; selected_quest_key = None
	if len(archived_quests) > 0:
		selected_quest = archived_quests[0]
		selected_quest_tasks = sorted(Task.storage.list(quest=selected_quest['id']),key=lambda t:t['task_order'])
		selected_quest_key = [key for key in keys if key['resource'] == selected_quest['id']][0]

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('list.html')),
		active_quest=None,
		quests_templates=templates_folder,
		selected_quest=selected_quest,
		selected_quest_tasks=selected_quest_tasks,
		selected_quest_key=selected_quest_key,
		incomplete_quests=[],
		complete_quests=archived_quests,
		is_archive=True
	)


@quests_log_blueprint.route("/quest/<string:quest_id>",methods=["GET"])
@login_required
def getQuest(quest_id):

	quest = Quest.storage.get(id=quest_id)
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'r' in key['resource_key'] ):
		return abort(403)

	active_quest = ActiveQuest.storage.get(user=current_user['id'])
	tasks = sorted(Task.storage.list(quest=quest['id']),key=lambda x:x['task_order'])
	events = {event['task']:event for event in Event.storage.list(quest=quest['id'])}
	locations = list(Location.storage.list())
	saved_locations = {
		label: [location for location in locations if location['label'] == label]
		for label in set([l['label'] for l in locations])
	}
	locations = {location['id']: location for location in locations}

	tasks_list = {task['id']:task for task in tasks}
	for taskId, event in events.items():
		if(event['location'] in locations):
			event.setInfo('elocation',locations[event['location']])
		else:
			event.setInfo('elocation',event['location'])
		tasks_list[taskId].setInfo('event',event)
		
	quest.setInfo('tasks',sorted(tasks_list.values(),key=lambda x:x['task_order']))
	quest.setInfo('active',active_quest is not None and quest['id'] == active_quest['quest'])
	quest.setInfo('key',key)

	if request.args.get("format") == "json":
		return {"data":{"quest":quest.to_dict(complements=True)}}

	if key is None or not( 'w' in key['resource_key'] ):
		return abort(403)

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	events = [events.get(task['id'],None) for task in tasks]
	return render_template(
		str(Path(templates_folder).joinpath('view.html')),
		quest=quest,
		saved_locations=saved_locations,
		quests_templates=templates_folder
	)


@quests_log_blueprint.route("/quest",methods=["GET"])
@login_required
def newQuest():

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	locations = list(Location.storage.list())
	saved_locations = {
		label: [location for location in locations if location['label'] == label]
		for label in set([l['label'] for l in locations])
	}
	return render_template(
		str(Path(templates_folder).joinpath('new.html')),
		quests_templates=templates_folder,
		saved_locations=saved_locations
	)


@quests_log_blueprint.route("/quest",methods=["POST"])
@login_required
def createQuest():

	data = dict(request.json)

	quest = Quest(
		id=Quest.storage.generate_value('id'),
		owner=current_user['id'],
		title=data['title'],
		description=data['description'],
		complete=False,
		archived=False,
		reccurence=Quest.RECCURENCES[data['periodicity']['type']],
		reccurence_config=data['periodicity'].get('configs',None)
	)

	tasks = []
	for i,task in enumerate(data['tasks']):
		tasks.append(Task(id=Task.storage.generate_value('id'),quest=quest['id'],task_order=i,content=task['content'],complete=False))

	key = ResourceKey(
		id=ResourceKey.storage.generate_value('id'),resource=quest['id'],resource_type="quest",user=current_user['id'],resource_key="drwx"
	)

	Quest.storage.create(quest)
	ResourceKey.storage.create(key)
	for i, task in enumerate(tasks):
		Task.storage.create(task)
		if data['tasks'][i].get('event',None) is not None:
			event = data['tasks'][i]['event']
			Event.storage.create(Event(
				id=Event.storage.generate_value('id'),task=task['id'], quest=quest['id'],
				start_date=datetime.fromisoformat(event['start_date']),
				end_date=datetime.fromisoformat(event['end_date']),
				location=event['location'],
				reminder=event['reminder'],
				synced=False
			))

	quest = quest.to_dict()
	quest.update({"tasks":[task.to_dict() for task in tasks]})
	return {"data":{"quest":quest}}


@quests_log_blueprint.route("/quest/<string:quest_id>",methods=["PUT"])
@login_required
def editQuest(quest_id):

	quest = Quest.storage.get(id=quest_id).takeSnapshot()
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'w' in key['resource_key'] ):
		return abort(403)

	data = dict(request.json)

	tasks = {task['id']:task for task in sorted(Task.storage.list(quest=quest['id']),key=lambda t:t['task_order'])}
	new_tasks_ids = [task['id'] for task in data['tasks'] if 'id' in task and task['id'] != None]
	# Remove deleted tasks
	for task_id in tasks:
		if not task_id in new_tasks_ids:
			Event.storage.update({"quest":None,"task":None, "synced": False},task=task_id)
			Task.storage.delete(id=task_id)

	# Update other tasks
	new_tasks = []
	for i,task in enumerate(data['tasks']):
		if 'id' in task and task['id'] != None:
			tasks[task['id']].takeSnapshot().setAttributes(content=task['content'], task_order=i)
			Task.storage.updateOnSnapshot(tasks[task['id']])
			new_tasks.append(tasks[task['id']])
			event = Event.storage.get(task=task['id'])
			if task.get('event',None) is not None and event is None:
				Event.storage.create(Event(
					id=Event.storage.generate_value('id'),task=task['id'], quest=quest['id'],
					start_date=datetime.fromisoformat(task['event']['start_date']),
					end_date=datetime.fromisoformat(task['event']['end_date']),
					location=task['event']['location'],
					reminder=task['event']['reminder'],
					synced=False
				))
			elif task.get('event',None) is None and event is not None:
				event.takeSnapshot().setAttributes(synced=False, task=None, quest=None)
				Event.storage.updateOnSnapshot(event)
			elif task.get('event',None) is not None and event is not None:
				event.takeSnapshot().setAttributes(
					start_date=datetime.fromisoformat(task['event']['start_date']),
					end_date=datetime.fromisoformat(task['event']['end_date']),
					location=task['event']['location'],
					reminder=task['event']['reminder'],
					synced=False
				)
				Event.storage.updateOnSnapshot(event)
		else:
			new_task = Task(id=Task.storage.generate_value('id'),quest=quest['id'],task_order=i,content=task['content'],complete=False)
			Task.storage.create(new_task)
			new_tasks.append(new_task)
			if task.get('event',None) is not None:
				Event.storage.create(Event(
					id=Event.storage.generate_value('id'), task=new_task['id'], quest=quest['id'],
					start_date=datetime.fromisoformat(task['event']['start_date']),
					end_date=datetime.fromisoformat(task['event']['end_date']),
					location=task['event']['location'],
					reminder=task['event']['reminder'],
					synced=False
				))

	quest.setAttributes(
		title=data['title'],description=data['description'],reccurence=Quest.RECCURENCES[data['periodicity']['type']],
		reccurence_config=data['periodicity'].get("configs",None)
	)
	Quest.storage.updateOnSnapshot(quest)

	quest = quest.to_dict()
	quest['tasks'] = [task.to_dict() for task in new_tasks]
	return {"data":{"quest":quest}}


@quests_log_blueprint.route("/quest/<string:quest_id>",methods=["DELETE"])
@login_required
def deleteQuest(quest_id):

	quest = Quest.storage.get(id=quest_id).takeSnapshot()
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'd' in key['resource_key'] ):
		return abort(403)

	ResourceKey.storage.delete(resource=quest['id'], resource_type="quest", many=True)
	Event.storage.update({"quest":None,"task":None, "synced": False},quest=quest['id'])
	Task.storage.delete(quest=quest['id'],many=True)
	Quest.storage.delete(quest=quest['id'])

	quest = quest.to_dict()
	return {"data":{"quest":quest}}


@quests_log_blueprint.route("/quest/<string:quest_id>/active",methods=["POST"])
@login_required
def setActiveQuest(quest_id):

	quest = Quest.storage.get(id=quest_id)
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'r' in key['resource_key'] ):
		return abort(403)

	active_quest = ActiveQuest.storage.get(user=current_user['id'])

	if active_quest is not None:
		active_quest.takeSnapshot()['quest'] = quest_id
		ActiveQuest.storage.updateOnSnapshot(active_quest)
	else:
		ActiveQuest.storage.create(ActiveQuest(user=current_user['id'],quest=quest_id))

	return redirect("/quests")


@quests_log_blueprint.route("/quest/<string:quest_id>/archive",methods=["POST"])
@login_required
def setQuestArchived(quest_id):

	quest = Quest.storage.get(id=quest_id)
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'w' in key['resource_key'] ):
		return abort(403)

	if quest['complete'] == False:
		return abort(401)

	quest.takeSnapshot().setAttribute("archived",True)
	Quest.storage.updateOnSnapshot(quest)

	return redirect("/quests")


@quests_log_blueprint.route("/quest/<string:quest_id>/dearchive",methods=["POST"])
@login_required
def setQuestDearchived(quest_id):

	quest = Quest.storage.get(id=quest_id)
	if quest is None:
		return abort(404)
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'w' in key['resource_key'] ):
		return abort(403)

	quest.takeSnapshot().setAttribute("archived",False)
	Quest.storage.updateOnSnapshot(quest)

	return redirect("/quests")


@quests_log_blueprint.route("/task/<string:task_id>",methods=["PUT"])
@login_required
def editTask(task_id):
	task = Task.storage.get(id=task_id)
	if task is None:
		return abort(404)

	quest = Quest.storage.get(id=task['quest']).takeSnapshot()
	key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=current_user['idU'])
	if key is None:
		key = ResourceKey.storage.get(resource=quest['id'], resource_type="quest", user=None)

	if key is None or not( 'x' in key['resource_key'] ):
		return abort(403)

	js = dict(request.json)
	eventjs = js.pop('event',None)
	task.takeSnapshot().setAttributes(**js)
	task.storage.updateOnSnapshot(task)

	event = Event.storage.get(task=task['id'])
	if event is None and eventjs is not None:
		Event.storage.create(Event(
			id=Event.storage.generate_value('id'), task=task['id'], quest=quest['id'],
			start_date=datetime.fromisoformat(eventjs['start_date']),
			end_date=datetime.fromisoformat(eventjs['end_date']),
			location=eventjs['location'],
			reminder=eventjs['reminder'],
			synced=False
		))
	elif event is not None and eventjs is not None:
		event.takeSnapshot().setAttributes(
			start_date=datetime.fromisoformat(eventjs['start_date']),
			end_date=datetime.fromisoformat(eventjs['end_date']),
			location=eventjs['location'],
			reminder=eventjs['reminder'],
			synced=False
		)
		Event.storage.updateOnSnapshot(event)
	elif event is not None and eventjs is None:
		event.takeSnapshot().setAttributes(task=None,quest=None, synced=False)
		Event.storage.updateOnSnapshot(event)

	active_quest = ActiveQuest.storage.get(user=current_user['id'])
	is_active = active_quest is not None and quest['id'] == active_quest['quest']
	tasks = list(Task.storage.list(quest=quest['id']))
	if all([t['complete'] for t in tasks]):
		quest.setAttribute("complete",True)
		Quest.storage.updateOnSnapshot(quest)
		if is_active:
			ActiveQuest.storage.delete(user=current_user['id'])
			is_active = False
	else:
		if quest['complete']:
			quest.setAttribute("complete",False)
			Quest.storage.updateOnSnapshot(quest)

	quest = quest.to_dict()
	quest.update({
		"active":is_active,
		"tasks":[task.to_dict() for task in sorted(tasks,key=lambda x:x['task_order'])],
		"key":key.to_dict()
	})

	return {"data":{"task":task.to_dict(), "quest": quest}}
