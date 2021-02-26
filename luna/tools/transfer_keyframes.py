import pymel.core as pm
from PySide2 import QtWidgets

import luna.utils.pysideFn as pysideFn
import luna.interface.shared_widgets as shared_widgets
import luna_rig
reload(shared_widgets)


class TransferDialog(QtWidgets.QDialog):

    INSTANCE = None  # type: TransferDialog
    GEOMETRY = None

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(TransferDialog, self).__init__(parent)
        self.setWindowTitle("Transfer keyframes")
        self.setProperty("saveWindowPref", True)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(TransferDialog.GEOMETRY)

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

    def create_layouts(self):
        source_layout = QtWidgets.QVBoxLayout()
        source_layout.addWidget(self.source_component_wgt)
        self.source_group.setLayout(source_layout)

        time_offset_layout = QtWidgets.QHBoxLayout()
        time_offset_layout.addWidget(QtWidgets.QLabel("Offset:"))
        time_offset_layout.addWidget(self.time_offset_dspinbox)
        time_offset_layout.addStretch()
        self.time_range_wgt.main_layout.addLayout(time_offset_layout)

        target_layout = QtWidgets.QVBoxLayout()
        target_layout.addWidget(self.target_component_wgt)
        self.target_group.setLayout(target_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.time_range_wgt)
        self.main_layout.addWidget(self.vertical_splitter)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.transfer_button)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.transfer_button.clicked.connect(self.make_transfer)

    def make_transfer(self):
        if not self.source_component_wgt.list.currentItem():
            pm.warning("Selected component to copy keyframes from")
            return
        if not self.target_component_wgt.list.selectedItems():
            pm.warning("Select at least 1 target component")
            return
        source_component = self.source_component_wgt.list.currentItem().data(1)  # type: luna_rig.Component
        time_offset = self.time_offset_dspinbox.value()
        for selected_target in self.target_component_wgt.list.selectedItems():
            target_component = selected_target.data(1)
            source_component.copy_keyframes(self.time_range_wgt.get_range(), target_component, time_offset=time_offset)


if __name__ == "__main__":
    TransferDialog.display()
