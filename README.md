# DigiQuests
A quest log flask app to manage your to do list in a fun way with an auto-check system able to examine automatically if a quest is complete or not. It was built upon the skyrim theme and was inspired by the app **Quest Log** published by **PZED** that can be found on play store [here](https://play.google.com/store/apps/details?id=com.app.stodo)


## What has been done 
The app allows for now for a single user to add, edit & delete quests to the quest log.

- Enable users to sync quests/tasks with other calendars (Google Calendar)

## install

### Fresh installation

- Create the mysql database that will be used by the app. If you use another name than 'digiq' then you'll have to update accordingly the files [config.toml](https://github.com/TuburboMajus/DigiQuests/blob/main/config.toml#L20) and [install/install.py](https://github.com/TuburboMajus/DigiQuests/blob/main/install/install.py#L10)
- Update the file [config.toml](https://github.com/TuburboMajus/DigiQuests/blob/main/config.toml#L18-L19) by writing the mysql user & password with write privileges on all tables on the database created 

```console
git clone https://github.com/TuburboMajus/DigiQuests
cd DigiQuests
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python install/setup.py # Enter your mysql database credentials

systemctl enable digiq.service
systemctl enable digiq.timer
systemctl start digiq.timer

./run.sh
```

The command **python install/setup.py** may fail if the executing user does not have enough permissions. In this case, execute
```console
sudo venv/bin/python install/setup.py
```

### update

To update your current version of DigiQuests, stop the server (you may need to backup your digiq databse in case of an error), then go to your DigiQuests directory and do the following:

```console
git pull
cd DigiQuests
pip install --upgrade -r requirements.txt
python install/update.py # Enter your mysql database credentials

./run.sh
```

The command **python install/update.py** may fail if the executing user does not have enough permissions. In this case, execute
```console
sudo venv/bin/python install/update.py
```

Check if digiq service is enabled and running:
```console
systemctl is-enabled digiq.service # should show enabled
systemctl is-enabled digiq.timer # should show enabled
systemctl is-active digiq.timer # should show active
```

if any of digiq.service or digiq.timer is not enabled execute
```console
systemctl enable digiq.service 
systemctl enable digiq.timer
```

if digiq.timer is not active execute
```console
systemctl start digiq.timer
```

### Run through https

#### Https to http nginx forwarding

The first option to run the server securily is to run it behind a nginx reverse proxy with a ssl context that can be provided by certbot per example.
You can accomplish this by:

- Setup nginx to [redirect subdomain](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) to your http app running on localhost (with ssl configuration set to **false** in your config.toml file). Per example, lets say we've added this configuration:
```
server {
    listen 80;
    server_name digiq.example.com;
    location / {
        proxy_pass http://localhost:1234;
    }
}
```

- Install certbot and run the cmd:
```console
sudo certbot --nginx -d digiq.example.com
```
Certbot will generate your ssl context and will automatically update your nginx configuration accordingly.

#### Serve https directly

To serve https directely you'll need to generate the ssl context (again can be done using certbot) then provide the file paths, key & certificate, to the config.toml file by updating the parameters **ssl_key** and **ssl_cert** and setting **ssl** to true.

### Synchronization with external apps

#### Google Calendar

To allow the app to synchronize the tasks you create with Google calendar, automatically creating, updating and deleting events, you will need first to setup your app to run in an ssl context as shown above. Then, you'll need to create a google app from you [google dev console](https://console.cloud.google.com/).

* Create a new app.
* Go to your [apis dashboard](https://console.cloud.google.com/apis/dashboard) and activate the Google Calendar API
* Setup your [app's consent screen](https://console.cloud.google.com/apis/credentials/consent) according to the nature of your google dev account:
  * If it is an entreprise account you can't setup your app to be internal and thus all users linked to the account can consent and use the app.
  * Otherwise, you can setup the app to be in dev and add the emails of your users manually to the testers list or they wont be able to allow the app to access their calendars.
* Create an OAuth credential of type "Web Application" where you'll need to add the following urls to the *authorized url redirection* section:
  * https://[app domain name]/gservices/calendar/auth
  * https://[app domain name]/gservices/calendar
  * https://[app domain name]
* Download the generated crendentials on to your server and update your config.toml file to set the parameter **credentials_file** under the section *app.blueprints.google_services* to point to the correct location.
* Run your server

***NB*** : If you picked the first option (Https to http nginx forwarding) to serve the app through https, you'll need also to update, or add, the parameter **ssl_encapsulation** under the *app* section and set it to true, or the OAuth authentication process will fail. 

## What's to be done

- Users management
- Sharing quests with other users and rights management
- Create auto-trackers to observe tasks & quests completion
- Mobile app (for this one I'm waiting a bit If by any chance **PZED** will find this git and contact me to see if we can join efforts to build upon his app as I didn't succeed in finding his contact.)

## Author
[PyAxolotl](https://github.com/PyAxolotl): abdellatifzied.saada@gmail.com


