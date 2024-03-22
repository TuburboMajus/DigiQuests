from temod.base.constraint import *
from .entity import *


class CSTR_USER_USER_ACCOUNT(EqualityConstraint):
	ATTRIBUTES = [
		{"name":"id","entity":User},
		{"name":"idU","entity":UserAccount},
	]


class CSTR_ACCOUNT_PRIVILEGE_USER_ACCOUNT(EqualityConstraint):
	ATTRIBUTES = [
		{"name":"id","entity":AccountPrivilege},
		{"name":"idP","entity":UserAccount},
	]


class CSTR_TASK_MONITOR_TASK(EqualityConstraint):
	ATTRIBUTES = [
		{"name":"id","entity":Task},
		{"name":"task","entity":TaskMonitor},
	]


class CSTR_TASK_QUEST(EqualityConstraint):
	ATTRIBUTES = [
		{"name":"quest","entity":Task},
		{"name":"id","entity":Quest}
	]