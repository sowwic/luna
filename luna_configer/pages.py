from PySide2 import QtWidgets
from PySide2 import QtCore
import luna
import luna.interface.shared_widgets as shared_widgets
import luna.interface.hud as hud
import luna.interface.marking_menu as marking_menu
import luna.utils.devFn as devFn


class PageWidget(QtWidgets.QWidget):

    CATEGORY_NAME = 'Category'

    def __repr__(self):
        return self.__class__.CATEGORY_NAME

    def __init__(self, parent=None):
        super(PageWidget, self).__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        pass

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        pass

    def load_config(self):
        raise NotImplementedError("load_config method must be implemented")

    def save_config(self):
        raise NotImplementedError("save_config method must be implemented")


class DeveloperPage(PageWidget):
    CATEGORY_NAME = "Developer"

    def create_widgets(self):
        self.logging_grp = QtWidgets.QGroupBox("Logging")
        self.logging_level_field = QtWidgets.QComboBox()
        self.logging_level_field.addItems(["NOT SET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

        self.testing_grp = QtWidgets.QGroupBox("Testing")
        self.testing_temp_dir = shared_widgets.PathWidget(dialog_label="Set temp dir for luna tests", label_text="Temp dir: ")
        self.testing_buffer_output_cb = QtWidgets.QCheckBox("Buffer output")
        self.testing_new_file_cb = QtWidgets.QCheckBox("New scene per test")
        self.testing_delete_files_cb = QtWidgets.QCheckBox("Delete test files")
        self.testing_delete_dirs_cb = QtWidgets.QCheckBox("Delete test dirs")

        self.misc_grp = QtWidgets.QGroupBox("Misc")
        self.misc_pyport_field = shared_widgets.NumericFieldWidget("Python port:", default_value=-1, min_value=-1, max_value=49151,)

    def create_layouts(self):
        super(DeveloperPage, self).create_layouts()
        logging_layout = QtWidgets.QFormLayout()
        self.logging_grp.setLayout(logging_layout)
        logging_layout.addRow("Level: ", self.logging_level_field)

        testing_layout = QtWidgets.QVBoxLayout()
        self.testing_grp.setLayout(testing_layout)
        testing_layout.addWidget(self.testing_temp_dir)
        testing_layout.addWidget(self.testing_buffer_output_cb)
        testing_layout.addWidget(self.testing_new_file_cb)
        testing_layout.addWidget(self.testing_delete_files_cb)
        testing_layout.addWidget(self.testing_delete_dirs_cb)

        misc_layout = QtWidgets.QFormLayout()
        self.misc_grp.setLayout(misc_layout)
        misc_layout.addRow(self.misc_pyport_field)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.logging_grp)
        self.main_layout.addWidget(self.testing_grp)
        self.main_layout.addWidget(self.misc_grp)
        self.main_layout.addStretch()

    def create_connections(self):
        pass

    def load_config(self):
        luna.Logger.debug("Developer page - loading config...")
        config_dict = luna.Config.load()

        # Logging
        luna.Logger.set_level(config_dict.get(luna.LunaVars.logging_level))
        self.logging_level_field.setCurrentText(luna.Logger.get_level(name=1))

        # Testing
        self.testing_temp_dir.line_edit.setText(config_dict.get(luna.TestVars.temp_dir, ""))
        self.testing_buffer_output_cb.setChecked(config_dict.get(luna.TestVars.buffer_output, True))
        self.testing_new_file_cb.setChecked(config_dict.get(luna.TestVars.new_file, True))
        self.testing_delete_files_cb.setChecked(config_dict.get(luna.TestVars.delete_files, True))
        self.testing_delete_dirs_cb.setChecked(config_dict.get(luna.TestVars.delete_dirs, True))

        # Misc
        self.misc_pyport_field.set_value(config_dict.get(luna.LunaVars.command_port, -1))

    def save_config(self):
        luna.Logger.debug("Developer page - saving config...")
        new_config = {}
        # Logging
        luna.Logger.set_level(self.logging_level_field.currentText())
        new_config[luna.LunaVars.logging_level] = luna.Logger.get_level()

        # Testing
        new_config[luna.TestVars.temp_dir] = self.testing_temp_dir.line_edit.text()
        new_config[luna.TestVars.buffer_output] = self.testing_buffer_output_cb.isChecked()
        new_config[luna.TestVars.new_file] = self.testing_new_file_cb.isChecked()
        new_config[luna.TestVars.delete_files] = self.testing_delete_files_cb.isChecked()
        new_config[luna.TestVars.delete_dirs] = self.testing_delete_dirs_cb.isChecked()

        # Misc
        new_config[luna.LunaVars.command_port] = self.misc_pyport_field.value()

        # Open command port
        devFn.open_port(self.misc_pyport_field.value())

        # Update config
        luna.Config.update(new_config)
        luna.Logger.debug("Developer page - saved config: {0}".format(new_config))


class GeneralPage(PageWidget):

    CATEGORY_NAME = "General"

    def create_widgets(self):
        # HUD
        self.interface_grp = QtWidgets.QGroupBox("Interface")
        self.hud_section_field = shared_widgets.NumericFieldWidget("HUD Section:", data_type="int", min_value=0, max_value=9)
        self.hud_block_field = shared_widgets.NumericFieldWidget("HUD Block:", data_type="int", min_value=0)
        # Marking menu
        self.marking_mode_combobox = QtWidgets.QComboBox()
        self.marking_mode_combobox.addItems(["Animator", "Rigger"])
        # Misc
        self.misc_grp = QtWidgets.QGroupBox("Miscellaneous")
        self.misc_licence_cb = QtWidgets.QCheckBox("Student pop up block:")
        self.misc_project_max_recent = shared_widgets.NumericFieldWidget("Recent projects limit:", default_value=3, min_value=2, max_value=10)
        # Unreal
        self.unreal_grp = QtWidgets.QGroupBox("Unreal Engine")
        self.unreal_project = shared_widgets.PathWidget(label_text="Project path:", dialog_label="Set Unreal project")

    def create_layouts(self):
        super(GeneralPage, self).create_layouts()
        interface_layout = QtWidgets.QFormLayout()
        interface_layout.addRow("Marking menu mode:", self.marking_mode_combobox)
        interface_layout.addRow(self.hud_block_field)
        interface_layout.addRow(self.hud_section_field)
        self.interface_grp.setLayout(interface_layout)

        unreal_layout = QtWidgets.QVBoxLayout()
        unreal_layout.addWidget(self.unreal_project)
        self.unreal_grp.setLayout(unreal_layout)

        self.main_layout.addWidget(self.interface_grp)
        self.main_layout.addWidget(self.unreal_grp)
        self.main_layout.addStretch()

    def create_connections(self):
        pass

    def load_config(self):
        luna.Logger.debug("General page - loading config...")
        config_dict = luna.Config.load()
        # HUD
        self.hud_section_field.set_value(config_dict.get(luna.HudVars.section, 7))
        self.hud_block_field.set_value(config_dict.get(luna.HudVars.block, 5))
        self.marking_mode_combobox.setCurrentIndex(config_dict.get(luna.LunaVars.marking_menu_mode, 1))
        self.unreal_project.line_edit.setText(config_dict.get(luna.UnrealVars.project, ""))

    def save_config(self):
        luna.Logger.debug("General page - saving config...")
        new_config = {}

        # HUD
        new_config[luna.HudVars.section] = self.hud_section_field.value()
        new_config[luna.HudVars.block] = self.hud_block_field.value()
        new_config[luna.UnrealVars.project] = self.unreal_project.line_edit.text()
        new_config[luna.LunaVars.marking_menu_mode] = self.marking_mode_combobox.currentIndex()

        luna.Config.update(new_config)
        luna.Logger.debug("General page - saved config: {0}".format(new_config))
        # Hud recreate
        luna.Logger.info("Updating HUD...")
        hud.LunaHUD.create()
        # Apply marking menu mode
        marking_menu.MarkingMenu.MODE = self.marking_mode_combobox.currentIndex()


class RigPage(PageWidget):

    CATEGORY_NAME = "Rig"

    def create_widgets(self):
        # Naming
        self.naming_grp = QtWidgets.QGroupBox("Naming")
        self.naming_current_template = shared_widgets.StringFieldWidget("Current template:", button_text="Set")
        self.naming_current_template.line_edit.setReadOnly(True)
        self.naming_templates_table = QtWidgets.QTableWidget()
        self.naming_templates_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.naming_templates_table.setColumnCount(2)
        self.naming_templates_table.setHorizontalHeaderLabels(["Name", "Rule"])
        self.naming_templates_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.naming_start_index = shared_widgets.NumericFieldWidget("Start index:", default_value=0, min_value=0)
        self.naming_index_padding = shared_widgets.NumericFieldWidget("Index padding:", default_value=2, min_value=1)

        # File formats
        self.file_formats_grp = QtWidgets.QGroupBox("File formats")
        self.file_formats_skin_combobox = QtWidgets.QComboBox()
        self.file_formats_skin_combobox.addItems(["pickle", "json"])
        self.file_formats_nglayers_combobox = QtWidgets.QComboBox()
        self.file_formats_nglayers_combobox.addItems(["pickle", "json"])

        # Misc
        self.misc_grp = QtWidgets.QGroupBox("Miscellaneous")
        self.misc_line_width = shared_widgets.NumericFieldWidget("Line width", data_type="double", default_value=2.0, min_value=-1.0)

    def create_layouts(self):
        super(RigPage, self).create_layouts()
        naming_layout = QtWidgets.QFormLayout()
        naming_layout.addRow(self.naming_current_template)
        naming_layout.addRow(self.naming_templates_table)
        naming_layout.addRow(self.naming_start_index)
        naming_layout.addRow(self.naming_index_padding)
        self.naming_grp.setLayout(naming_layout)

        file_formats_layout = QtWidgets.QFormLayout()
        file_formats_layout.addRow("Skin files:", self.file_formats_skin_combobox)
        file_formats_layout.addRow("ngLayers files:", self.file_formats_nglayers_combobox)
        self.file_formats_grp.setLayout(file_formats_layout)

        misc_layout = QtWidgets.QFormLayout()
        misc_layout.addRow(self.misc_line_width)
        self.misc_grp.setLayout(misc_layout)

        self.main_layout.addWidget(self.naming_grp)
        self.main_layout.addWidget(self.file_formats_grp)
        self.main_layout.addWidget(self.misc_grp)
        self.main_layout.addStretch()

    def create_connections(self):
        self.naming_current_template.button.clicked.connect(self.set_current_naming_template)
        self.naming_templates_table.customContextMenuRequested.connect(self.naming_table_context_menu)

    def load_config(self):
        luna.Logger.debug("General page - loading config...")
        config_dict = luna.Config.load()
        # Naming
        default_template_dict = {"default": "{side}_{name}_{suffix}"}
        self.update_templates_table(config_dict.get(luna.NamingVars.templates_dict, default_template_dict))
        self.naming_current_template.line_edit.setText(config_dict.get(luna.NamingVars.current_template, "Error"))
        self.naming_start_index.set_value(config_dict.get(luna.NamingVars.start_index, 0))
        self.naming_index_padding.set_value(config_dict.get(luna.NamingVars.index_padding, 2))
        # File formats
        self.file_formats_skin_combobox.setCurrentText(config_dict.get(luna.RigVars.skin_export_format, "pickle"))
        self.file_formats_nglayers_combobox.setCurrentText(config_dict.get(luna.RigVars.nglayers_export_format, "pickle"))
        # Misc
        self.misc_line_width.set_value(config_dict.get(luna.RigVars.line_width, 2.0))

    def save_config(self):
        luna.Logger.debug("Rig page - saving config...")
        new_config = {}
        new_config[luna.NamingVars.current_template] = self.naming_current_template.line_edit.text()
        new_config[luna.NamingVars.templates_dict] = self.get_naming_templates_dict()
        new_config[luna.NamingVars.start_index] = self.naming_start_index.spin_box.value()
        new_config[luna.NamingVars.index_padding] = self.naming_index_padding.spin_box.value()
        new_config[luna.RigVars.skin_export_format] = self.file_formats_skin_combobox.currentText()
        new_config[luna.RigVars.nglayers_export_format] = self.file_formats_nglayers_combobox.currentText()
        new_config[luna.RigVars.line_width] = self.misc_line_width.value()

        luna.Config.update(new_config)
        luna.Logger.debug("Rig page - saved config: {0}".format(new_config))

    def update_templates_table(self, templates_dict):
        self.naming_templates_table.setRowCount(0)
        for row_index, template_name in enumerate(templates_dict.keys()):
            name_item = QtWidgets.QTableWidgetItem(template_name)
            rult_item = QtWidgets.QTableWidgetItem(templates_dict.get(template_name))
            self.naming_templates_table.insertRow(row_index)
            self.naming_templates_table.setItem(row_index, 0, name_item)
            self.naming_templates_table.setItem(row_index, 1, rult_item)

    def set_current_naming_template(self):
        table_selection = self.naming_templates_table.selectedItems()
        if not table_selection:
            return
        if table_selection[-1].column == 0:
            template_name = table_selection[-1].text()
        else:
            template_name = self.naming_templates_table.item(table_selection[-1].row(), 0).text()
        self.naming_current_template.line_edit.setText(template_name)

    def get_naming_templates_dict(self):
        template_dict = {}
        for row_index in range(self.naming_templates_table.rowCount()):
            template_name = self.naming_templates_table.item(row_index, 0).text()
            template_rule = self.naming_templates_table.item(row_index, 1).text()
            template_dict[template_name] = template_rule
        return template_dict

    def naming_table_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        add_template_action = QtWidgets.QAction("Add template", self)
        remove_template_action = QtWidgets.QAction("Remove template", self)
        add_template_action.triggered.connect(lambda *args: self.naming_templates_table.insertRow(self.naming_templates_table.rowCount()))
        remove_template_action.triggered.connect(lambda *args: [self.naming_templates_table.removeRow(item.row()) for item in self.naming_templates_table.selectedItems()])
        context_menu.addAction(add_template_action)
        context_menu.addAction(remove_template_action)
        context_menu.exec_(self.naming_templates_table.mapToGlobal(point))
