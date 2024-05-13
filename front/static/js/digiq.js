var NEW_TASKS_ITERATOR = 0

function on_task_checkbox_click(){
	set_task_complete(this.dataset.task, this.dataset.complete!="true")
}

function on_storyline_selected(storyline){
	let curl = new URL(window.location.href)
	if (curl.searchParams.get('line') == undefined || curl.searchParams.get('line') == null){
		curl.searchParams.append("line",storyline)
	}else{
		curl.searchParams.set("line",storyline)
	}
	window.location.href = curl.toString()
}

function on_sidebar_quest_click(questid){
	select_quest(questid)
	event.stopPropagation()
}

function select_quest(questid){
	let req = new XMLHttpRequest();
	req.onload = function(){
		let data = JSON.parse(this.response)['data']
		set_selected_quest(data['quest'])
		reset_quest_ui(data['quest'], data['active'])
	}

	req.open('GET',`/quest/${questid}?format=json`)
	req.send()
}

function set_active_quest(btn){
	let form = document.createElement('form');
	form.method="post"
	form.action=`/quest/${btn.dataset.quest}/active`
	document.body.appendChild(form)
	form.submit()
}

function archive_quest(btn){
	let form = document.createElement('form');
	form.method="post"
	form.action=`/quest/${btn.dataset.quest}/archive`
	document.body.appendChild(form)
	form.submit()
}

function dearchive_quest(btn){
	let form = document.createElement('form');
	form.method="post"
	form.action=`/quest/${btn.dataset.quest}/dearchive`
	document.body.appendChild(form)
	form.submit()
}

function set_task_complete(task, complete){
	let req = new XMLHttpRequest();
	req.onload = function(){
		update_task_ui(JSON.parse(this.response)['data']['task'])
		update_quest_ui(JSON.parse(this.response)['data']['quest'])
	}

	req.open('PUT',`/task/${task}`)
	req.setRequestHeader('Content-Type','application/json')
	req.send(JSON.stringify(
		{"complete":complete}
	))
}

function set_selected_quest(quest){
	let sidebar = document.getElementById('sidebar')
	let selected = Object.values(sidebar.getElementsByClassName('selected')).filter(x => x.classList.contains('quest_sidebar_item'))
	if (selected.length == 0) selected = null; else selected = selected[0];
	let new_selection = Object.values(sidebar.getElementsByClassName('unselected')).filter(x => x.dataset.quest == quest['id'])[0]

	if(new_selection == null) return;
	if(selected != null && selected.dataset.quest == new_selection.dataset.quest) return;

	if(selected != null)  {
		selected.classList.remove('selected')
		selected.classList.add('unselected')
	}
	new_selection.classList.remove('unselected')
	new_selection.classList.add('selected')

}

function update_task_ui(task){

	let task_li = null;
	let tasks_li = Object.values(document.getElementsByClassName('tasks_list')[0].getElementsByTagName('li'));
	for(var i = 0; i < tasks_li.length; i++){
		if(tasks_li[i].dataset.task == task['id']) 
			task_li = tasks_li[i];
	}

	if(task_li == null) return;

	img = task_li.getElementsByTagName('img')[0]
	new_img = document.createElement('img')
	new_img.classList.add('skr-img-40')
	new_img.classList.add('task_checkbox')
	new_img.dataset.complete = task['complete']
	new_img.dataset.task = task['id']

	new_img.onclick = on_task_checkbox_click

	let audio = null;

	if(task['complete']){
		new_img.src = "/static/images/task_complete_icon.png"
		audio = document.getElementById('quest_upgrade')
	}
	else{
		new_img.src = "/static/images/task_incomplete_icon.png"
		audio = document.getElementById('quest_downgrade')
	}

	audio.play()
	img.replaceWith(new_img)

}

function update_quest_ui(quest){

	let content_section = document.getElementById('quest_content_section')
	let complete_section = document.getElementById('quest_complete_section')

	if(quest['complete']){
		document.getElementById('level_up').play()
		content_section.style.display = "none";
		complete_section.style.display = "flex";
		complete_section.classList.add("skr-apparition")
	}else{
		let quest_item = Object.values(document.getElementById('incomplete_quests_list').getElementsByClassName('quest_sidebar_item')).filter(
			x => x.dataset.quest == quest['id']
		)[0]
		if(quest_item == undefined) window.location.reload()
	}

	setTimeout(function(){reset_quest_ui(quest)},6000)
}

function reset_quest_ui(quest){
	let content_section = document.getElementById('quest_content_section')
	let complete_section = document.getElementById('quest_complete_section')

	let active_quest_btn = document.getElementById('set_active_btn')
	let archive_quest_btn = document.getElementById('archive_btn')
	let dearchive_quest_btn = document.getElementById('dearchive_btn')
	if(quest['complete'] === true){
		active_quest_btn.style.display = "none"
		active_quest_btn.dataset.quest = ""
		if(quest['archived'] === true){
			archive_quest_btn.style.display = "none"
			archive_quest_btn.dataset.quest = ""
			dearchive_quest_btn.style.display = "block"
			dearchive_quest_btn.dataset.quest = quest['id']
		}else{
			archive_quest_btn.style.display = "block"
			archive_quest_btn.dataset.quest = quest['id']
			dearchive_quest_btn.style.display = "none"
			dearchive_quest_btn.dataset.quest = ""
		}
	}else{
		archive_quest_btn.style.display = "none"
		archive_quest_btn.dataset.quest = ""
		dearchive_quest_btn.style.display = "none"
		dearchive_quest_btn.dataset.quest = ""
		if(quest['active'] === true){
			active_quest_btn.style.display = "none"
			active_quest_btn.dataset.quest = ""
		}else if(quest['active'] === false){
			active_quest_btn.style.display = "block"
			active_quest_btn.dataset.quest = quest['id']
		}
	}

	if(quest['key']['resource_key'].includes('w')){
		edit_quest_btn.style.display = "block"
		edit_quest_btn.onclick = function(){ window.location.href = `/quest/${quest['id']}` }
	}else{
		edit_quest_btn.style.display = "none"
		edit_quest_btn.onclick = function(){}
	}

	if(quest['key']['resource_key'].includes('d')){
		delete_quest_btn.style.display = "block"
		delete_quest_btn.onclick = function(){ delete_quest(quest['id']) }
	}else{
		delete_quest_btn.style.display = "none"
		delete_quest_btn.onclick = function(){}
	}

	if(quest['title'] != undefined) document.getElementById('selected_quest_title').innerHTML = quest['title']
	if(quest['description'] != undefined) document.getElementById('selected_quest_description').innerHTML = quest['description']

	if(quest['tasks'] != undefined){
		let tasks_list = document.getElementById('selected_quest_tasks')
		tasks_list.innerHTML = ""
		Object.values(quest['tasks']).forEach(task => {
			let li = document.createElement('li')
			li.classList.add('skr-button-img')
			li.dataset.task = task['id']

			if(task['complete']){
				li.innerHTML = `<img src="/static/images/task_complete_icon.png" class="skr-img-40 task_checkbox" data-complete="true" data-task="${task['id']}">`
			}else{
				li.innerHTML = `<img src="/static/images/task_incomplete_icon.png" class="skr-img-40 task_checkbox" data-complete="false" data-task="${task['id']}">`
			}

			li.innerHTML += task['content']
			tasks_list.appendChild(li)

			if(quest['archived'] !== true){
				li.getElementsByTagName('img')[0].onclick = on_task_checkbox_click
			}
		})
	}

	content_section.style.display = "flex";
	complete_section.style.display = "none";
}

function add_new_task(task){
	let tasks_list = document.getElementById('new_tasks_list')
	let task_item = document.createElement('li')
	let task_name = document.createElement('strong')
	let task_startDate = document.createElement('input')
	let task_startTime = document.createElement('input')
	let task_endDate = document.createElement('input')
	let task_endTime = document.createElement('input')
	let task_location = document.createElement('input')
	let task_reminder = document.createElement('input')

	let edit_button = document.createElement('button')
	let edit_button_img = document.createElement('img')
	let delete_button = document.createElement('button')
	let delete_button_img = document.createElement('img')
	let up_button = document.createElement('button')
	let up_button_img = document.createElement('img')
	let down_button = document.createElement('button')
	let down_button_img = document.createElement('img')
	let dir_buttons_div = document.createElement('div')

	let has_event = task['event'] != undefined && task['event'] != null

	task_item.classList.add('editable_task_item')
	if(task['id'] != undefined) task_item.dataset.task = task['id']

	if(has_event){
		task_startDate.type = "hidden"; task_startDate.classList.add('task_startDate'); task_startDate.value = task['event']['start']['date']
		task_startTime.type = "hidden"; task_startTime.classList.add('task_startTime'); task_startTime.value = task['event']['start']['time']
		task_endDate.type = "hidden"; task_endDate.classList.add('task_endDate'); task_endDate.value = task['event']['end']['date']
		task_endTime.type = "hidden"; task_endTime.classList.add('task_endTime'); task_endTime.value = task['event']['end']['time']
		task_location.type = "hidden"; task_location.classList.add('task_location');
		task_reminder.type = "hidden"; task_reminder.classList.add('task_reminder');
		let elocation = task['event']['location']
		task_location.value = ""
		if(elocation != null && elocation != undefined){
			if(typeof(elocation) == "string"){
				task_location.value = elocation
			}else{
				task_location.value = elocation['id']
			}
		}
		let reminder = task['event']['reminder']
		task_reminder.value = ""
		if(reminder != null && reminder != undefined){
			task_reminder.value = reminder
		}
	}

	task_name.innerHTML = task['content']
	task_name.classList.add('task_name')

	edit_button_img.src = "/static/images/cog.png"
	edit_button.classList.add("skr-button-img")
	edit_button.classList.add("editable_task_full_button")

	delete_button_img.src = "/static/images/trash.png"
	delete_button.classList.add("skr-button-img")
	delete_button.classList.add("editable_task_full_button")

	up_button_img.src = "/static/images/up_arrow.png"
	up_button_img.classList.add("editable_task_half_button")
	up_button_img.classList.add("clickable_image")

	down_button_img.src = "/static/images/down_arrow.png"
	down_button_img.classList.add("editable_task_half_button")
	down_button_img.classList.add("clickable_image")

	delete_button.onclick = delete_new_task
	edit_button.onclick = edit_new_task_from_list
	up_button_img.onclick = move_task_up
	down_button_img.onclick = move_task_down

	delete_button.appendChild(delete_button_img)
	edit_button.appendChild(edit_button_img)

	dir_buttons_div.style.alignSelf = "flex-start"
	dir_buttons_div.appendChild(up_button_img);
	dir_buttons_div.appendChild(down_button_img);

	task_item.id = "new_task_item_"+NEW_TASKS_ITERATOR
	NEW_TASKS_ITERATOR += 1
 
	task_item.appendChild(task_name)
	task_item.appendChild(edit_button)
	task_item.appendChild(delete_button)
	task_item.appendChild(dir_buttons_div)

	if(has_event){
		task_item.appendChild(task_startDate); task_item.appendChild(task_startTime);
		task_item.appendChild(task_endDate); task_item.appendChild(task_endTime);	
		task_item.appendChild(task_location); task_item.appendChild(task_reminder);	
	}
	tasks_list.insertBefore(task_item, new_task_li)
}

function update_new_task(task, task_element_id){
	let task_dom = document.getElementById(task_element_id)
	if(task_dom == null) return;

	task_dom.getElementsByClassName('task_name')[0].innerHTML = task['content']
	if(task['event'] == undefined || task['event'] == null){
		try{task_dom.getElementsByClassName('task_startDate')[0].remove()}catch{}
		try{task_dom.getElementsByClassName('task_startTime')[0].remove()}catch{}
		try{task_dom.getElementsByClassName('task_endDate')[0].remove()}catch{}
		try{task_dom.getElementsByClassName('task_endTime')[0].remove()}catch{}
		try{task_dom.getElementsByClassName('task_location')[0].remove()}catch{}
		try{task_dom.getElementsByClassName('task_reminder')[0].remove()}catch{}
	}else{
		try{task_dom.getElementsByClassName('task_startDate')[0].value = task['event']['start']['date']}
		catch{
			let task_startDate = document.createElement('input')
			task_startDate.type = "hidden"; task_startDate.classList.add('task_startDate'); task_startDate.value = task['event']['start']['date']
			task_dom.appendChild(task_startDate)
		}
		try{task_dom.getElementsByClassName('task_startTime')[0].value = task['event']['start']['time']}
		catch{
			let task_startTime = document.createElement('input')
			task_startTime.type = "hidden"; task_startTime.classList.add('task_startTime'); task_startTime.value = task['event']['start']['time']
			task_dom.appendChild(task_startTime)
		}
		try{task_dom.getElementsByClassName('task_endDate')[0].value = task['event']['end']['date']}
		catch{
			let task_endDate = document.createElement('input')
			task_endDate.type = "hidden"; task_endDate.classList.add('task_endDate'); task_endDate.value = task['event']['end']['date']
			task_dom.appendChild(task_endDate)
		}
		try{task_dom.getElementsByClassName('task_endTime')[0].value = task['event']['end']['time']}
		catch{
			let task_endTime = document.createElement('input')
			task_endTime.type = "hidden"; task_endTime.classList.add('task_endTime'); task_endTime.value = task['event']['end']['time']
			task_dom.appendChild(task_endTime)
		}
		let elocation = task['event']['location']
		try{
			if(elocation == null){
				try{task_dom.getElementsByClassName('task_location')[0].remove()}catch{}
			}else{
				task_dom.getElementsByClassName('task_location')[0].value = elocation
			}
		}
		catch{
			let task_location = document.createElement('input')
			task_location.type = "hidden"; task_location.classList.add('task_location'); task_location.value = elocation
			task_dom.appendChild(task_location)
		}
		let reminder = task['event']['reminder']
		try{
			if(reminder == null){
				try{task_dom.getElementsByClassName('task_reminder')[0].remove()}catch{}
			}else{
				task_dom.getElementsByClassName('task_reminder')[0].value = reminder
			}
		}
		catch{
			let task_reminder = document.createElement('input')
			task_reminder.type = "hidden"; task_reminder.classList.add('task_reminder'); task_reminder.value = reminder
			task_dom.appendChild(task_reminder)
		}
	}
}


function edit_new_task_from_list(btn){
	let task = {}
	if( btn == undefined || btn.tagName == undefined) btn = this;
	edit_new_task(task_from_dom(btn.parentNode), btn.parentNode.id)
}

function create_new_task(){
	ntd_resetDialog()
	ntd_setConfirmCallback(add_new_task)
	ntd_setConfirmText('Add')
	$('#newTaskDialog').modal('show')
}

function edit_new_task(task, task_element_id){
	ntd_setupDialog(task)
	ntd_setConfirmCallback(function(x){update_new_task(x,task_element_id)})
	ntd_setConfirmText('Edit')
	$('#newTaskDialog').modal('show')
}

function delete_new_task(btn){
	if( btn == undefined || btn.tagName == undefined) btn = this;
	btn.parentNode.remove()
}

function move_task_up(btn){
	if( btn == undefined || btn.tagName == undefined) btn = this;
	let task_item = this.parentNode.parentNode
	let tasks_list = document.getElementById("new_tasks_list")
	let task_order = null;
	let tasks = Object.values(tasks_list.getElementsByTagName('li')).filter( x => x.id != "new_task_li" )
	for(var i = 0; i < tasks.length; i++){
		if(tasks[i].id == task_item.id) task_order = i;
	}

	if(task_order == null || task_order == 0) return;
	tasks_list.removeChild(task_item)
	tasks_list.insertBefore(task_item,tasks[task_order-1])
}

function move_task_down(btn){
	if( btn == undefined || btn.tagName == undefined) btn = this;
	let task_item = this.parentNode.parentNode
	let tasks_list = document.getElementById("new_tasks_list")
	let task_order = null;
	let tasks = Object.values(tasks_list.getElementsByTagName('li')).filter( x => x.id != "new_task_li" )
	for(var i = 0; i < tasks.length; i++){
		if(tasks[i].id == task_item.id) task_order = i;
	}

	if(task_order == null || task_order == tasks.length-1) return;
	tasks_list.removeChild(task_item)
	if(task_order == tasks.length-2) tasks_list.insertBefore(task_item,document.getElementById('new_task_li'))
	else tasks_list.insertBefore(task_item,tasks[task_order+2])
}

function task_from_dom(task_dom){

	let task = {
		"content":task_dom.getElementsByClassName('task_name')[0].innerHTML,
		"event":null
	}

	if(task_dom.dataset.task != undefined) task['id'] = task_dom.dataset.task

	let task_startDate = task_dom.getElementsByClassName('task_startDate')[0]
	if(task_startDate != undefined){
		let elocation = null
		try{elocation = task_dom.getElementsByClassName('task_location')[0].value}catch{}
		let reminder = null
		try{
			reminder = parseInt(task_dom.getElementsByClassName('task_reminder')[0].value)
			if(isNaN(reminder)) reminder = null;
		}catch{}
		task['event'] = {
			"start":{
				"date":task_startDate.value,
				"time":task_dom.getElementsByClassName('task_startTime')[0].value
			},"end":{
				"date":task_dom.getElementsByClassName('task_endDate')[0].value,
				"time":task_dom.getElementsByClassName('task_endTime')[0].value
			},"location":elocation,
			"reminder": reminder
		}
	}

	return task
}


function format_task_for_server(task){
	if(task['event'] != undefined && task['event'] != null){
		task['event'] = {
			"start_date":new Date(task['event']['start']['date']+" "+task['event']['start']['time']).toISOString().split('Z')[0],
			"end_date":new Date(task['event']['end']['date']+" "+task['event']['end']['time']).toISOString().split('Z')[0],
			"location":task['event']['location'],
			"reminder":task['event']['reminder']
		}
		delete task['event']['start']
		delete task['event']['end']
	}
	return task
}

function format_event_from_server(task){
	if(task['event'] != undefined && task['event'] != null){
		let event = task['event']
		let sDate = new Date(event['start_date']+"Z")
		let eDate = new Date(event['end_date']+"Z")
		let sMDate = sDate.getMonth()+1;
		let sDDate = sDate.getDate();
		let eMDate = eDate.getMonth()+1;
		let eDDate = eDate.getDate();
		let sHTime = sDate.getHours();
		let sMTime = sDate.getMinutes();
		let eHTime = eDate.getHours();
		let eMTime = eDate.getMinutes();
		task['event'] = {
			"start":{
				"date":`${sDate.getFullYear()}-${(sMDate < 10)?'0':''}${sMDate}-${(sDDate < 10)?'0':''}${sDDate}`,
				"time":`${(sHTime < 10)?'0':''}${sHTime}:${(sMTime < 10)?'0':''}${sMTime}`
			},
			"end":{
				"date":`${eDate.getFullYear()}-${(eMDate < 10)?'0':''}${eMDate}-${(eDDate < 10)?'0':''}${eDDate}`,
				"time":`${(eHTime < 10)?'0':''}${eHTime}:${(eMTime < 10)?'0':''}${eMTime}`
			},
			"location":event['elocation'],
			"reminder":event['reminder']
		}
	}else{
		task['event'] = null
	}
	return task
}


function validate_quest(quest){

	if(quest['title'].length == 0) return ["Quest title can't be left empty"];

	return [];
}


function create_new_quest(){
	let quest = {}
	quest['title'] = document.getElementById('new_quest_title').value
	quest['description'] = document.getElementById('new_quest_description').value
	quest['periodicity'] = {"type": document.getElementById('new_quest_period').dataset.periodicity}
	quest['tasks'] = Object.values(
		document.getElementById("new_tasks_list").getElementsByTagName('li')
	).filter( 
		x => x.id != "new_task_li"
	).map( 
		y => format_task_for_server(task_from_dom(y))
	)
	quest['storyline'] = document.getElementById('new_quest_storyline').value
	if(quest['storyline'] == ""){
		quest['storyline'] = null
	}

	errors = validate_quest(quest)
	if(errors.length == 0){
		var req = new XMLHttpRequest()
		req.onload = function(){
			js = JSON.parse(this.response)
			window.location.href = `/quests?quest=${js['data']['quest']['id']}`
		}

		req.open('POST',"/quest")
		req.setRequestHeader('Content-Type',"application/json")
		req.send(JSON.stringify(quest))
	}else{
		show_toast({
			"messages":errors,
			"title": "Error",
			"info": "",
			"image": "/static/images/error.png",
		})
	}
}

function edit_quest(questid){

	let quest = {}
	quest['title'] = document.getElementById('new_quest_title').value
	quest['description'] = document.getElementById('new_quest_description').value
	quest['periodicity'] = {"type": document.getElementById('new_quest_period').dataset.periodicity}
	quest['tasks'] = Object.values(
		document.getElementById("new_tasks_list").getElementsByTagName('li')
	).filter( 
		x => x.id != "new_task_li"
	).map( 
		y => format_task_for_server(task_from_dom(y))
	)
	quest['storyline'] = document.getElementById('new_quest_storyline').value
	if(quest['storyline'] == ""){
		quest['storyline'] = null
	}

	errors = validate_quest(quest)
	if(errors.length == 0){
		var req = new XMLHttpRequest()
		req.onload = function(){
			js = JSON.parse(this.response)
			window.location.href = `/quests?quest=${js['data']['quest']['id']}`
		}

		req.open('PUT',`/quest/${questid}`)
		req.setRequestHeader('Content-Type',"application/json")
		req.send(JSON.stringify(quest))
	}else{
		show_toast({
			"messages":errors,
			"title": "Error",
			"info": "",
			"image": "/static/images/error.png",
		})
	}
}

function delete_quest(questid){
	if(confirm("Deleting the quest will permanently erase it from your database. Continue ?")){
		var req = new XMLHttpRequest()
		req.onload = function(){
			window.location.href = `/quests`
		}

		req.open('DELETE',`/quest/${questid}`)
		req.send()
	}
}

$('.task_checkbox').on('click',on_task_checkbox_click)