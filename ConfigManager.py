# -*- coding: utf-8 -*-
#ConfigManager
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import os
import configparser
import logging
from logging import getLogger

class ConfigManager(configparser.ConfigParser):


	def __init__(self):
		super().__init__()
		self.identifier="ConfigManager"
		self.log=getLogger("Soc.%s" % (self.identifier))
		self.log.debug("Create config instance")

	def read(self,fileName):
		self.fileName=fileName
		if os.path.exists(fileName):
			self.log.info("read configFile:"+fileName)
			try:
				with open(self.fileName,"r",encoding="utf-8") as f: return super().read(f)
			except configparser.ParsingError:
				self.log.warning("configFile parse failed.")
				return []
		else:
			self.log.warning("configFile not found.")
			return []

	def write(self):
		self.log.info("write configFile:"+self.fileName)
		with open(self.fileName,"w",encoding="utf-8") as f: return super().write(f)

	def __getitem__(self,key):
		try:
			return ConfigSection(super().__getitem__(key))
		except KeyError as e:
			self.log.debug("created new section:"+key)
			self.add_section(key)
			return self.__getitem__(key)

	def getstring(self,section,key,default="",selection=None,*, raw=False, vars=None,fallback=None):
		if type(selection) not in (set,tuple,list):
			raise TypeError("selection must be set, list or tuple")
		ret=self.__getitem__(section)[key]
		if ret=="":
			if default=="":
				self[section][key]=""
				return ""
			else:
				self.log.debug("add default value.  at section "+section+", key "+key)
				self[section][key]=default
				ret=default
				if selection==None:return ret

		if ret not in selection:
			self.log.debug("value "+ret+" not in selection.  at section "+section+", key "+key)
			self[section][key]=default
			ret=default
		return ret

	def getint(self,section,key,default=0,min=None,max=None):
		if type(default)!=int:
			raise ValueError("default value must be int")
		try:
			ret = super().getint(section,key)
			if (min!=None and ret<min) or (max!=None and ret>max):
				self.log.debug("intvalue "+str(ret)+" out of range.  at section "+section+", key "+key)
				self[section][key]=str(default)
				return int(default)
			return ret
		except (configparser.NoOptionError,ValueError) as e:
			self.log.debug("add new intval "+str(default)+" at section "+section+", key "+key)
			self[section][key]=str(default)
			return int(default)
		except configparser.NoSectionError as e:
			self.log.debug("add new section and intval "+str(default)+" at section "+section+", key "+key)
			self.add_section(section)
			self.__getitem__(section).__setitem__(key,str(default))
			return int(default)

	def add_section(self,name):
		if not self.has_section(name):
			return super().add_section(name)

class ConfigSection(configparser.SectionProxy):
	def __init__(self,proxy):
		super().__init__(proxy._parser, proxy._name)

	def __getitem__(self,key):
		try:
			return super().__getitem__(key)
		except KeyError:
			self._parser[self._name][key]=""
			return ""

	def __setitem__(self,key,value):
		return super().__setitem__(key,str(value))
