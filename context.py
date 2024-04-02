from temod.ext.holders import clusters, joins, entities
from temod_flask.ext import _readers_holder as _FormReaders
from temod.storage.directory import DirectoryStorage


def init_context(config):
	
	for category, name, entity in entities.tuples():
		_FormReaders.addEntity(entity)
		if name in __builtins__:
			print(f'Warning: cannot register entity {name} in the global context as {name} is already used');continue
		__builtins__[name] = entity

	for category, name, join in joins.tuples():
		_FormReaders.addJoin(join)
		if name in __builtins__:
			print(f'Warning: cannot register join {name} in the global context as {name} is already used');continue
		__builtins__[name] = join

	for category, name, cluster in clusters.tuples():
		_FormReaders.addCluster(cluster)
		if name in __builtins__:
			print(f'Warning: cannot register cluster {name} in the global context as {name} is already used');continue
		__builtins__[name] = cluster