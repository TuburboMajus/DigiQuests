
function show_toast(options){
	console.log(options)
	
	if(options['title'] != undefined) document.getElementById('base_toast_title').innerHTML = options['title'];
	else document.getElementById('base_toast_title').innerHTML = "";

	if(options['info'] != undefined) document.getElementById('base_toast_info').innerHTML = options['info'];
	else document.getElementById('base_toast_info').innerHTML = "";

	if(options['image'] != undefined) document.getElementById('base_toast_image').src = options['image'];
	else document.getElementById('base_toast_image').src = "/static/images/info.png";

	if(options['messages'] == undefined) document.getElementById('base_toast_body').innerHTML = "";
	else{
		let toast_body = document.getElementById('base_toast_body')
		if(options['messages'].length  == 1) toast_body.innerHTML = options['messages'][0]
		else{
			toast_body.innerHTML = ""
			Object.values(options['messages']).forEach( message => {
				let div = document.createElement('div')
				div.innerHTML = message
				toast_body.appendChild(div)
			})
		}
	}

	var toast = bootstrap.Toast.getOrCreateInstance(document.getElementById('base_toast'))
	toast.show()
}