# # import pybullet as p
# # import pybullet_data
# # import time
# # import os

# # # Start simulation
# # physicsClient = p.connect(p.GUI)

# # # Load default assets
# # p.setAdditionalSearchPath(pybullet_data.getDataPath())

# # plane = p.loadURDF("plane.urdf")
# # # robot = p.loadURDF("r2d2.urdf")

# # # Gravity
# # p.setGravity(0,0,-9.8)


# # ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# # pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")
# # # cup_obj = os.path.join(ASSET_ROOT, "dinnerware", "plastic_coffee_cup.obj")
# # # cup_vhacd = os.path.join(ASSET_ROOT, "dinnerware", "plastic_coffee_cup_vhacd.obj")
# # wheelchair_urdf = os.path.join(ASSET_ROOT, "wheelchair", "wheelchair.urdf")

# # # === Load Wheelchair ===
# # # wheelchair_start_pos = [0, -0.2, 0.1]
# # # wheelchair_id = p.loadURDF(wheelchair_urdf, basePosition=wheelchair_start_pos, useFixedBase=True)

# # # # === Load PR2 ===
# # pr2_start_pos = [-0.8, -0.4, 0]
# # pr2_id = p.loadURDF(pr2_urdf, basePosition=pr2_start_pos, useFixedBase=True)

# # for i in range(10000):
# #     p.stepSimulation()
# #     time.sleep(1./240.)

# # p.disconnect()



# import pybullet as p
# import pybullet_data
# import time
# import os

# physicsClient = p.connect(p.GUI)

# p.setAdditionalSearchPath(pybullet_data.getDataPath())

# plane = p.loadURDF("plane.urdf")

# p.setGravity(0,0,-9.8)

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# pr2_start_pos = [-0.8, -0.4, 0]
# pr2_id = p.loadURDF(pr2_urdf, basePosition=pr2_start_pos, useFixedBase=True)

# end_effector_index = 61


# def move_arm_to(target_pos):

#     joint_angles = p.calculateInverseKinematics(
#         pr2_id,
#         end_effector_index,
#         target_pos
#     )

#     for joint_index in range(len(joint_angles)):
#         p.setJointMotorControl2(
#             pr2_id,
#             joint_index,
#             p.POSITION_CONTROL,
#             targetPosition=joint_angles[joint_index],
#             force=500
#         )


# def agent():

#     # Agent decides goal position
#     return [0.3, -0.2, 0.9]


# target = agent()

# print("Agent target:", target)

# for i in range(500):

#     move_arm_to(target)

#     p.stepSimulation()
#     time.sleep(1./240.)

# p.disconnect()


import pybullet as p
import pybullet_data
import time
import os
import numpy as np

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

p.loadURDF("plane.urdf")
p.setGravity(0,0,-9.8)

ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
pr2_urdf = os.path.join(ASSET_ROOT,"PR2","pr2_no_torso_lift_tall.urdf")

pr2 = p.loadURDF(pr2_urdf, basePosition=[-0.8,-0.4,0], useFixedBase=True)


# for i in range(p.getNumJoints(pr2)):
#     print(i, p.getJointInfo(pr2,i)[1].decode())

# ---- find joints ----

right_arm_joint_names = [
"r_shoulder_pan_joint",
"r_shoulder_lift_joint",
"r_upper_arm_roll_joint",
"r_elbow_flex_joint",
"r_forearm_roll_joint",
"r_wrist_flex_joint",
"r_wrist_roll_joint"
]

end_effector_name = "r_gripper_tool_joint"

right_arm_joint_indices = []
movable_joints = []
ee_index = None

for i in range(p.getNumJoints(pr2)):
    
    info = p.getJointInfo(pr2,i)
    name = info[1].decode()
    
    if info[2] != p.JOINT_FIXED:
        movable_joints.append(i)

    if name in right_arm_joint_names:
        right_arm_joint_indices.append(i)

    if name == end_effector_name:
        ee_index = i

# IK mapping
right_arm_ik_indices = [movable_joints.index(j) for j in right_arm_joint_indices]

# ---- reach function ----

def reach(target_pos):

    orn = p.getQuaternionFromEuler([0,0,0])

    ik = p.calculateInverseKinematics(
        pr2,
        ee_index,
        target_pos,
        orn
    )

    ik = np.array(ik)

    joint_angles = [ik[i] for i in right_arm_ik_indices]

    for j,a in zip(right_arm_joint_indices,joint_angles):

        p.setJointMotorControl2(
            pr2,
            j,
            p.POSITION_CONTROL,
            targetPosition=a,
            force=500
        )

# ---- simple agent ----

def agent():

    return [0.4,-0.2,0.9]

target = agent()

for i in range(2000):

    reach(target)

    p.stepSimulation()
    time.sleep(1/240)