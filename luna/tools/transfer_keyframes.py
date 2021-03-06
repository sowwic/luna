import pymel.core as pm
from PySide2 import QtWidgets
import luna.utils.pysideFn as pysideFn
import luna.interface.shared_widgets as shared_widgets


class TransferKeyframesDialog(QtWidgets.QDialog):

    INSTANCE = None  # type: TransferKeyframesDialog
    GEOMETRY = None

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(TransferKeyframesDialog, self).__init__(parent)
        self.setWindowTitle("Transfer keyframes")
        self.setProperty("saveWindowPref", True)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(TransferKeyframesDialog.GEOMETRY)

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()
        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    def create_widgets(self):
        self.time_range_wgt = shared_widgets.TimeRangeWidget()
        self.time_offset_dspinbox = QtWidgets.QDoubleSpinBox()
        self.time_offset_dspinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        self.source_group = QtWidgets.QGroupBox("Source component")
        self.source_component_wgt = shared_widgets.ComponentsListing()
        self.source_component_wgt.list.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.target_group = QtWidgets.QGroupBox("Target component")
        self.target_component_wgt = shared_widgets.ComponentsListing()

        self.vertical_splitter = QtWidgets.QSplitter()
        self.vertical_splitter.addWidget(self.source_group)
        self.vertical_splitter.addWidget(self.target_group)
        self.transfer_button = QtWidgets.QPushButton("Transfer")

        self.problems_log = QtWidgets.QTextEdit()
        self.problems_log.setReadOnly(True)
        self.status_bar = QtWidgets.QStatusBar()

    def create_layouts(self):
        source_layout = QtWidgets.QVBoxLayout()
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.addWidget(self.source_component_wgt)
        self.source_group.setLayout(source_layout)

        time_offset_layout = QtWidgets.QHBoxLayout()
        time_offset_layout.addWidget(QtWidgets.QLabel("Offset:"))
        time_offset_layout.addWidget(self.time_offset_dspinbox)
        time_offset_layout.addStretch()
        self.time_range_wgt.main_layout.addLayout(time_offset_layout)

        target_layout = QtWidgets.QVBoxLayout()
        target_layout.setContentsMargins(0, 0, 0, 0)
        target_layout.addWidget(self.target_component_wgt)
        self.target_group.setLayout(target_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(5, 10, 5, 0)
        self.main_layout.addWidget(self.time_range_wgt)
        self.main_layout.addWidget(self.vertical_splitter)
        self.main_layout.addWidget(self.problems_log)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.transfer_button)
        self.main_layout.addWidget(self.status_bar)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.transfer_button.clicked.connect(self.make_transfer)
        self.source_component_wgt.list.itemSelectionChanged.connect(self.update_problems)
        self.source_component_wgt.list.itemSelectionChanged.connect(self.update_transfer_button)
        self.target_component_wgt.list.itemSelectionChanged.connect(self.update_problems)
        self.target_component_wgt.list.itemSelectionChanged.connect(self.update_transfer_button)
        self.source_component_wgt.update_started.connect(lambda: self.status_bar.showMessage("Updating source components..."))
        self.source_component_wgt.update_finished.connect(self.status_bar.clearMessage)
        self.target_component_wgt.update_started.connect(lambda: self.status_bar.showMessage("Updating target component..."))
        self.target_component_wgt.update_finished.connect(self.status_bar.clearMessage)

    def make_transfer(self):
        self.status_bar.showMessage("Transfering keys...")
        if not self.source_component_wgt.list.currentItem():
            pm.warning("Selected component to copy keyframes from")
            return
        if not self.target_component_wgt.list.selectedItems():
            pm.warning("Select at least 1 target component")
            return
        source_component = self.source_component_wgt.list.currentItem().data(1)
        time_offset = self.time_offset_dspinbox.value()
        for selected_target in self.target_component_wgt.list.selectedItems():
            target_component = selected_target.data(1)
            source_component.copy_keyframes(self.time_range_wgt.get_range(), target_component, time_offset=time_offset)
        self.status_bar.showMessage("Transfer complete...", 5)

    def update_problems(self):
        self.problems_log.clear()
        if not self.source_component_wgt.list.currentItem() or not self.target_component_wgt.list.selectedItems():
            return
        source_component = self.source_component_wgt.list.currentItem().data(1)
        if not pm.objExists(source_component.pynode):
            self.problems_log.append("Node {0} no longer exists. Update components list.".format(source_component.pynode))
            self.transfer_button.setEnabled(False)
            return
        if not source_component.is_animatable():
            self.problems_log.append("Not animatable source component selected {0}".format(source_component))
            return

        source_controls_names = [ctl.transform.stripNamespace() for ctl in source_component.controls]
        target_controls_names = []
        for selected_target in self.target_component_wgt.list.selectedItems():
            target_component = selected_target.data(1)
            if not target_component.is_animatable():
                self.problems_log.append("Not animatable target component selected {0}".format(source_component))
                return
            target_controls_names += [ctl.transform.stripNamespace() for ctl in target_component.controls]

        for source_name in source_controls_names:
            if source_name not in target_controls_names:
                self.problems_log.append("{0}: Missing control {1}".format(target_component, source_name))

    def update_transfer_button(self):
        source_item = self.source_component_wgt.list.currentItem()
        target_item = self.target_component_wgt.list.currentItem()
        if source_item and target_item and all([source_item.data(1).is_animatable(), target_item.data(1).is_animatable()]):
            self.transfer_button.setEnabled(True)
        else:
            self.transfer_button.setEnabled(False)


if __name__ == "__main__":
    TransferKeyframesDialog.display()
