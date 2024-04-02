# DigiQuests
A quest log flask app to manage your to do list in a fun way with an auto-check system able to examine automatically if a quest is complete or not. It was built upon the skyrim theme and was inspired by the app **Quest Log** published by **PZED** that can be found on play store [here](https://play.google.com/store/apps/details?id=com.app.stodo)


## What has been done 
The app allows for now for a single user to add, edit & delete quests to the quest log.

- Enable users to sync quests/tasks with other calendars (Google Calendar)

## install

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

python run.py
```

The command **python install/setup.py** may fail if the executing user does not have enough permissions. In this case, execute
```console
sudo venv/bin/python install/setup.py
```

## update

To update your current version of DigiQuests, stop the server, then go to your DigiQuests directory and do the following:

```console
git pull
cd DigiQuests
pip install --upgrade -r requirements.txt
python install/update.py # Enter your mysql database credentials

python run.py
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

## What's to be done

- Users management
- Sharing quests with other users and rights management
- Create auto-trackers to observe tasks & quests completion
- Mobile app (for this one I'm waiting a bit If by any chance **PZED** will find this git and contact me to see if we can join efforts to build upon his app as I didn't succeed in finding his contact.)

## Author
[PyAxolotl](https://github.com/PyAxolotl): abdellatifzied.saada@gmail.com


