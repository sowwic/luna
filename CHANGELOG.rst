luna
=========================

v 0.2.14
-------
* Fix issues with loading plugin in Maya2023 (#36)

v 0.2.13
-------
* History widget hotfix

v 0.2.12
-------
* Allow model to be not specified.
* Fixes to support MetaHuman based character.
* FKIKSpine orientation fixes.
* Character: add option to specify up axis for root motion.
* BipedLeg: add option to specify class used for foot creation.
* Hand: add option to specify end joints for five finger setup.
* Add AbstractReverseFootComponent.
* AnimComponent: improve skeleton detachment logic.
* Add new inputs to FKIK spine node.
* FKIKComponent node: add new axis attributes.

v 0.2.11
-------
* Decoupled duplicated rig control joints from input skeleton joint names.

v 0.2.10
-------
* Add BipedLeg class and node.

v 0.2.9
-------
* Added scene history widget.

v 0.2.8
-------
* Added implementation for script node.

v 0.2.7
-------
* Store control name parts on tag node attributes. Rename top character node to "rig" #16

v 0.2.6
-------
* Add drag in installer for maya.

v 0.2.5
-------
* HandComponent: five finger setup fix wrong argument for end joint and ctl.
* FKIKComponent: add helper method to add orient switch for fk control.
* Add common_setup module to reduce build code duplication.
