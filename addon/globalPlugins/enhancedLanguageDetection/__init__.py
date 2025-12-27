# coding: utf-8
# Copyright 2025 Emil-18
# An add-on that detects languages based on the spoken text itself
# This add-on is licensed under the same license as NVDA. See the copying.txt file for more information

import addonHandler
addonHandler.initTranslation()
import config
import globalPluginHandler
import gui
import languageHandler
import os
import speech
import sys
import wx
from scriptHandler import script
from speech.commands import LangChangeCommand
from speech.extensions import filter_speechSequence
from . import langdetect
# Lingua can't be imported with relative import, because it requires submodules that I had to include manualy in the lingua folder
# so add both the add-on folder as well as the underlying lingua folder, to os.path, import lingua, and remove them again
addonPath = os.path.dirname(__file__)
linguaPath = os.path.join(os.path.dirname(__file__), "lingua")
sys.path.append(addonPath)
sys.path.append(linguaPath)
import lingua
sys.path.remove(linguaPath)
sys.path.remove(addonPath)
profilePath = os.path.join(os.path.dirname(__file__), "langdetect", "profiles")
languages = os.listdir(profilePath)
detector = None

confspec = {
	"languageDetection": "integer(default=1)",
	"model": "integer(default=0)",
	"detectMultipleLanguages": "boolean(default=True)"
}

for i in languages:
	confspec.update({i: "boolean(default=False)"})
for i in lingua.Language:
	confspec.update({"lingua_"+i.iso_code_639_1.name: "boolean(default=False)"})
config.conf.spec["enhancedLanguageDetection"] = confspec
def updateDetector():
	global detector
	languages = []
	for i in lingua.Language:
		if not config.conf["enhancedLanguageDetection"]["lingua_"+i.iso_code_639_1.name]:
			continue
		languages.append(i)
	if languages:
		detector = lingua.LanguageDetectorBuilder(languages).build()
	return detector if languages else None

class EnhancedLanguageDetectionSettingsPanel(gui.SettingsPanel):
	# Translators: The title for the settings panel
	title = _("Enhanced Language Detection")
	def handleModelChange(self, evt):
		self.linguaLanguages.Enable(evt.GetSelection() == 0)
		self.languages.Enable(evt.GetSelection())
		self.multiple.Enable(evt.GetSelection() == 0)
	def makeSettings(self, settingsSizer):
		settings = gui.guiHelper.BoxSizerHelper(self, sizer = settingsSizer)
		modelComboBoxValues = [
			# Translators: An option in a combo box
			_("lingua (recommended)"),
			"langdetect"
		]
		# Translators: the label for a combo box
		label = _("language detection library")
		self.modelComboBox = settings.addLabeledControl(label, wx.Choice, choices = modelComboBoxValues)
		self.modelComboBox.SetSelection(config.conf["enhancedLanguageDetection"]["model"])
		self.modelComboBox.Bind(wx.EVT_CHOICE, self.handleModelChange)
		comboBoxValues = [
			# Translators: An option in a combo box
			_("always interpret"),
			# Translators: An option in a combo box
			_("only interpret if the text doesn't instruct NVDA to change language"),
			# Translators: An option in a combo box
			_("never interpret (NVDA's default behavior)")
		]
		# Translators: The label for a combo box
		label = _("Language interpretation:")
		self.languageDetection = settings.addLabeledControl(label, wx.Choice, choices = comboBoxValues)
		self.languageDetection.SetSelection(config.conf["enhancedLanguageDetection"]["languageDetection"])
		# Translators: The label for a c check box
		label = _("Detect multiple languages in the same text")
		self.multiple = settings.addItem(wx.CheckBox(self, label = label))
		self.multiple.SetValue(config.conf["enhancedLanguageDetection"]["detectMultipleLanguages"])
		self.multiple.Enable(config.conf["enhancedLanguageDetection"]["model"] == 0)
		# Translators: The label for a checkable list box
		label = _("Languages to interpret")
		choices = []
		for i in languages:
			description = languageHandler.getLanguageDescription(i)
			if description:
				choices.append(description)
			else:
				choices.append(i)
		self.languages = settings.addLabeledControl(label, gui.nvdaControls.CustomCheckListBox, choices = choices)
		self.languages.SetSelection(0)
		choices = []
		checked = []
		for i in range(len(languages)):
			if config.conf["enhancedLanguageDetection"][languages[i]]:
				checked.append(i)
		self.languages.SetCheckedItems(checked)
		for i in lingua.Language:
			description = languageHandler.getLanguageDescription(i.iso_code_639_1.name)
			if description:
				choices.append(description)
			else:
				choices.append(i.iso_code_639_1.name)
		self.linguaLanguages = settings.addLabeledControl(label, gui.nvdaControls.CustomCheckListBox, choices = choices)
		self.languages.SetSelection(0)
		checked = []
		for i in enumerate(lingua.Language):
			if config.conf["enhancedLanguageDetection"]["lingua_"+i[1].iso_code_639_1.name]:
				checked.append(i[0])
		self.linguaLanguages.SetCheckedItems(checked)
		self.languages.Enable(config.conf["enhancedLanguageDetection"]["model"])
		self.linguaLanguages.Enable(config.conf["enhancedLanguageDetection"]["model"] == 0)
	def onSave(self):
		config.conf["enhancedLanguageDetection"]["languageDetection"] = self.languageDetection.GetSelection()
		config.conf["enhancedLanguageDetection"]["model"] = self.modelComboBox.GetSelection()
		config.conf["enhancedLanguageDetection"]["detectMultipleLanguages"] = self.multiple.GetValue()
		checked = self.languages.GetCheckedItems()
		for i in range(len(languages)):
			config.conf["enhancedLanguageDetection"][languages[i]] = i in checked
		checked = self.linguaLanguages.GetCheckedItems()
		for i in enumerate(lingua.Language):
			config.conf["enhancedLanguageDetection"]["lingua_"+i[1].iso_code_639_1.name] = i[0] in checked
		updateDetector()
allowedLanguages = ["no", "en"]
def detectLanguage(text):
	try:
		languages = langdetect.detect_langs(text)
	except:
		return
	if not languages:
		return
	lang = None
	for language in languages:
		if config.conf["enhancedLanguageDetection"][language.lang]:
			lang = language.lang
			return(lang)
def detectLanguageWithLingua(text):
	lang = None
	try:
		lang = detector.detect_language_of(text)
	except:
		return
	if not lang:
		return
	return(lang.iso_code_639_1.name)

def detectMultipleLanguages(text):
	sequence = []
	if not detector:
		return([text])
	detected = detector.detect_multiple_languages_of(text)
	if not detected:
		return([text])
	for i in detected:
		newString = ""
		for j in range(i.start_index, i.end_index):
			newString += text[j]
		command = LangChangeCommand(i.language.iso_code_639_1.name.lower())
		sequence.append(command)
		sequence.append(newString)
	return(sequence)

def speechSequenceFilter(speechSequence, *args, **kwargs):
	if config.conf["enhancedLanguageDetection"]["languageDetection"] == 2 or not config.conf["speech"]["autoLanguageSwitching"]:
		return(speechSequence)
	newSequence = []
	shouldInterpret = True
	for i in speechSequence:
		if  isinstance(i, LangChangeCommand) and config.conf["enhancedLanguageDetection"]["languageDetection"] == 0:
			continue
		if isinstance(i, LangChangeCommand):
			shouldInterpret = not i.lang
		if isinstance(i, str):
			if shouldInterpret:
				if config.conf["enhancedLanguageDetection"]["model"] == 0 and config.conf["enhancedLanguageDetection"]["detectMultipleLanguages"]:
					tempSequence = detectMultipleLanguages(i)
					newSequence.extend(tempSequence)
					continue
				else:
					language = detectLanguage(i) if config.conf["enhancedLanguageDetection"]["model"] != 0 else detectLanguageWithLingua(i)
					if isinstance(language, str):
						language = language.lower()
					languageCommand = LangChangeCommand(language)
					newSequence.append(languageCommand)
			else:
				newSequence.append(i)
				continue

		newSequence.append(i)
	return(newSequence)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(EnhancedLanguageDetectionSettingsPanel)
		updateDetector()
		filter_speechSequence.register(speechSequenceFilter)
		config.post_configProfileSwitch.register(updateDetector)
	def terminate(self, *args, **kwargs):
		config.post_configProfileSwitch.unregister(updateDetector)
		filter_speechSequence.unregister(speechSequenceFilter)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove