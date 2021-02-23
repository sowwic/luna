# Control creation


- Full creation
    ```python
    import pymel.core as pm
    from Luna import Logger
    from Luna_rig.core.control import Control

    pm.newFile(f=1)
    # Fully create new control
    ctl1 = Control.create(name="arm_ik",
                            side="r",
                            guide=None,
                            joint=True,
                            shape="cube",
                            tag="ik")

    # Common methods and properties
    ctl1.write_bind_pose()
    #Set color and shape as properties
    ctl1.color = 17
    ctl1.shape = "circle"
    ctl1.orient_shape(direction="x")
    
    
    ```

- Instancing existing control as Python object
    ```python
    instance_from_name = Control("r_arm_ik_00_ctl")
    # -----------------------------------------------
    instance_from_name.insert_offset()
    Logger.info(instance_from_name.shape)
    Logger.info(instance_from_name.bind_pose)
    ```
---

Both objects represent identical control:

```
[Luna][DEBUG] ========Control instance========
              tree:
              -group: r_arm_ik_00_grp
              -offset_list: [nt.Transform(u'r_arm_ik_00_ofs')]
              -offset: r_arm_ik_00_ofs
              -transform: r_arm_ik_00_ctl
              -joint: r_arm_ik_00_cjnt
              -tag_node: r_arm_ik_00_ctl_tag

              data:
              -side: r
              -name: arm_ik
```