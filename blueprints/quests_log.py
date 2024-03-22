from flask import Blueprint, Response, current_app, request, render_template, abort, redirect
from flask_login import current_user, login_required

from temod.base.condition import Equals, Or, In 
from temod.base.attribute import UUID4Attribute

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
	if active_quest is not None:
		selected_quest = request.args.get("quest",active_quest['quest'])
		if selected_quest != active_quest['quest'] and selected_quest in [key['resource'] for key in keys]:
			selected_quest = Quest.storage.get(id=selected_quest)
		else:
			selected_quest = Quest.storage.get(id=active_quest['quest'])

	selected_quest_tasks = []
	if selected_quest is not None:
		selected_quest_tasks = sorted(Task.storage.list(quest=selected_quest['id']),key=lambda t:t['task_order'])

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('list.html')),
		active_quest=active_quest,
		quests_templates=templates_folder,
		selected_quest=selected_quest,
		selected_quest_tasks=selected_quest_tasks,
		selected_quest_key=[key for key in keys if key['resource'] == selected_quest['id']][0],
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

	complete_quests = list(Quest.storage.list(
		In("id",*[UUID4Attribute("id",value=key['resource']) for key in keys]),
		archived=True
	))

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('list.html')),
		active_quest=None,
		quests_templates=templates_folder,
		active_quest_tasks=[],
		incomplete_quests=[],
		complete_quests=complete_quests,
		is_archive=True
	)



@quests_log_blueprint.route("/quest",methods=["GET"])
@login_required
def newQuest():

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('new.html')),
		quests_templates=templates_folder
	)

@quests_log_blueprint.route("/quest",methods=["POST"])
@login_required
def createQuest():

	data = dict(request.json)

	quest = Quest(
		id=Quest.storage.generate_value('id'),
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

	key = ResourceKey(id=ResourceKey.storage.generate_value('id'),resource=quest['id'],resource_type="quest",user=current_user['id'],resource_key="rwx")

	Quest.storage.create(quest)
	ResourceKey.storage.create(key)
	for task in tasks:
		Task.storage.create(task)

	quest = quest.to_dict()
	quest.update({"tasks":[task.to_dict() for task in tasks]})
	return {"data":{"quest":quest}}


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

	if request.args.get("format") == "json":
		quest = quest.to_dict()
		quest.update({
			"active":active_quest is not None and quest['id'] == active_quest['quest'],
			"tasks":[task.to_dict() for task in sorted(tasks,key=lambda x:x['task_order'])],
			"key":key.to_dict()
		})
		return {"data":{"quest":quest}}

	if key is None or not( 'w' in key['resource_key'] ):
		return abort(403)

	templates_folder = quests_log_blueprint.configuration["templates_folder"]
	return render_template(
		str(Path(templates_folder).joinpath('view.html')),
		quest=quest,
		tasks=tasks,
		quests_templates=templates_folder
	)


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
			Task.storage.delete(id=task_id)

	# Update other tasks
	new_tasks = []
	for i,task in enumerate(data['tasks']):
		if 'id' in task and task['id'] != None:
			tasks[task['id']].takeSnapshot().setAttributes(content=task['content'], task_order=i)
			Task.storage.updateOnSnapshot(tasks[task['id']])
			new_tasks.append(tasks[task['id']])
		else:
			new_task = Task(id=Task.storage.generate_value('id'),quest=quest['id'],task_order=i,content=task['content'],complete=False)
			Task.storage.create(new_task)
			new_tasks.append(new_task)

	quest.setAttributes(
		title=data['title'],description=data['description'],reccurence=Quest.RECCURENCES[data['periodicity']['type']],
		reccurence_config=data['periodicity'].get("configs",None)
	)
	Quest.storage.updateOnSnapshot(quest)

	quest = quest.to_dict()
	quest['tasks'] = [task.to_dict() for task in new_tasks]
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

	active_quest = ActiveQuest.storage.get(user=current_user['id']).takeSnapshot()

	if active_quest is not None:
		active_quest['quest'] = quest_id
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
	task.takeSnapshot().setAttributes(**js)

	task.storage.updateOnSnapshot(task)

	tasks = list(Task.storage.list(quest=quest['id']))
	if all([t['complete'] for t in tasks]):
		quest.setAttribute("complete",True)
		Quest.storage.updateOnSnapshot(quest)
	else:
		if quest['complete']:
			quest.setAttribute("complete",False)
			Quest.storage.updateOnSnapshot(quest)

	return {"data":{"task":task.to_dict(), "quest": quest.to_dict()}}
