function on_confirm_updates(){
	getPasswordDialog_setCallback(changes_confirmed)
	$('#getPasswordDialog').modal('show')
}

function changes_confirmed(password){
	let data = {
		"updater_password":password,
		"user":{
			"password":document.getElementById('password').value,
			"cpassword":document.getElementById('cpassword').value
		}
	}

	let req = new XMLHttpRequest()
	req.onload = function(){ 
		if(this.status != 200){
			show_toast({
				"title":"error",
				"info":"",
				"image":"/static/images/error.png",
				"messages":[this.response]
			})
		}else{
			window.location.reload(); 
		}
	}

	req.open('POST',`/account/${document.getElementById('accountid').value}`)
	req.setRequestHeader('Content-Type',"application/json")
	req.send(JSON.stringify(data))
}