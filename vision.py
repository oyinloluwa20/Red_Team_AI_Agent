# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os
# import cv2

# # ------------------ SETUP ------------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# pr2 = p.loadURDF(pr2_urdf, basePosition=[-0.8, -0.4, 0], useFixedBase=True)

# # ------------------ LOAD OBJECT (CUP) ------------------
# cup_id = p.loadURDF("cube_small.urdf", [0.5, 0, 0.75])  # placeholder cup

# # ------------------ FIND JOINTS ------------------
# right_arm_joint_names = [
#     "r_shoulder_pan_joint",
#     "r_shoulder_lift_joint",
#     "r_upper_arm_roll_joint",
#     "r_elbow_flex_joint",
#     "r_forearm_roll_joint",
#     "r_wrist_flex_joint",
#     "r_wrist_roll_joint"
# ]

# end_effector_name = "r_gripper_tool_frame"

# right_arm_joint_indices = []
# movable_joints = []
# ee_index = None

# head_pan_joint = None
# head_tilt_joint = None

# for i in range(p.getNumJoints(pr2)):
#     info = p.getJointInfo(pr2, i)
#     name = info[1].decode()

#     if info[2] != p.JOINT_FIXED:
#         movable_joints.append(i)

#     if name in right_arm_joint_names:
#         right_arm_joint_indices.append(i)

#     if name == end_effector_name:
#         ee_index = i

#     if name == "head_pan_joint":
#         head_pan_joint = i

#     if name == "head_tilt_joint":
#         head_tilt_joint = i

# right_arm_ik_indices = [movable_joints.index(j) for j in right_arm_joint_indices]

# # ------------------ ARM CONTROL ------------------
# def reach(target_pos):
#     orn = p.getQuaternionFromEuler([0, 0, 0])

#     ik = p.calculateInverseKinematics(pr2, ee_index, target_pos, orn)
#     ik = np.array(ik)

#     joint_angles = [ik[i] for i in right_arm_ik_indices]

#     for j, a in zip(right_arm_joint_indices, joint_angles):
#         p.setJointMotorControl2(
#             pr2, j, p.POSITION_CONTROL,
#             targetPosition=a,
#             force=500
#         )

# # ------------------ HEAD LOOK-AT ------------------
# def look_at(target_pos):
#     cam_link = 24  # high_def_optical_frame

#     link_state = p.getLinkState(pr2, cam_link)
#     cam_pos = np.array(link_state[0])
#     target_pos = np.array(target_pos)

#     direction = target_pos - cam_pos
#     dx, dy, dz = direction

#     yaw = np.arctan2(dy, dx)
#     dist_xy = np.sqrt(dx**2 + dy**2)
#     pitch = -np.arctan2(dz, dist_xy)

#     p.setJointMotorControl2(
#         pr2, head_pan_joint,
#         p.POSITION_CONTROL,
#         targetPosition=yaw,
#         force=200
#     )

#     p.setJointMotorControl2(
#         pr2, head_tilt_joint,
#         p.POSITION_CONTROL,
#         targetPosition=pitch,
#         force=200
#     )

# # ------------------ CAMERA ------------------
# def get_camera(link_index):
#     link_state = p.getLinkState(pr2, link_index)
#     pos, orn = link_state[0], link_state[1]

#     rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

#     # optical frame fix
#     forward = rot @ np.array([0, 0, 1])
#     up = rot @ np.array([0, -1, 0])

#     view = p.computeViewMatrix(
#         cameraEyePosition=pos,
#         cameraTargetPosition=pos + forward,
#         cameraUpVector=up
#     )

#     proj = p.computeProjectionMatrixFOV(
#         fov=60,
#         aspect=1.0,
#         nearVal=0.01,
#         farVal=5
#     )

#     w, h, rgb, depth, seg = p.getCameraImage(256, 256, view, proj)
#     img = np.reshape(rgb, (h, w, 4))[:, :, :3]

#     return img

# # ------------------ SIMPLE AGENT ------------------
# def agent(step):
#     # simple up-down motion for demo
#     base = np.array([0.5, 0, 0.9])

#     offset = 0.1 * np.sin(step * 0.05)

#     return base + np.array([0, 0, offset])

# # ------------------ WAIT FOR STABILITY ------------------
# for _ in range(100):
#     p.stepSimulation()
#     time.sleep(1/240)

# # ------------------ GRASP OBJECT ------------------
# ee_pos = p.getLinkState(pr2, ee_index)[0]

# cid = p.createConstraint(
#     parentBodyUniqueId=pr2,
#     parentLinkIndex=ee_index,
#     childBodyUniqueId=cup_id,
#     childLinkIndex=-1,
#     jointType=p.JOINT_FIXED,
#     jointAxis=[0, 0, 0],
#     parentFramePosition=[0, 0, 0],
#     childFramePosition=[0, 0, 0]
# )

# print("Grasped object.")

# # ------------------ MAIN LOOP ------------------
# for i in range(1000):

#     target = agent(i)
#     reach(target)

#     # look at gripper (object)
#     ee_pos = p.getLinkState(pr2, ee_index)[0]
#     look_at(ee_pos)

#     # cameras
#     head_img = get_camera(24)
#     wrist_img = get_camera(63)

#     cv2.imshow("Head Camera", head_img)
#     cv2.imshow("Wrist Camera", wrist_img)
#     cv2.waitKey(1)

#     p.stepSimulation()
#     time.sleep(1/240)



# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os

# # ---------------- SETUP ----------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# pr2 = p.loadURDF(pr2_urdf, basePosition=[0, 0, 0], useFixedBase=True)

# # FIX VIEW
# p.resetDebugVisualizerCamera(20, 50, -30, [0, 0, 0.5])

# # ---------------- FIND EE ----------------
# ee_index = None

# for i in range(p.getNumJoints(pr2)):
#     info = p.getJointInfo(pr2, i)
#     link_name = info[12].decode()

#     if link_name == "r_gripper_tool_frame":
#         ee_index = i

# print("EE index:", ee_index)

# # ---------------- TEST LOOP ----------------
# for i in range(1000):
#     # if ee_index is not None:
#     #     pos = p.getLinkState(pr2, ee_index)[0]
#         # print("EE pos:", pos)

#     p.stepSimulation()
#     time.sleep(1/240)



# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os
# import cv2

# # ---------------- SETUP ----------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# pr2 = p.loadURDF(pr2_urdf, basePosition=[0, 0, 0], useFixedBase=True)

# # Fix view so you can see robot
# p.resetDebugVisualizerCamera(2, 50, -30, [0, 0, 0.5])

# # Add an object to look at
# cube = p.loadURDF("cube_small.urdf", [0.8, 0, 0.7])

# # ---------------- CAMERA FUNCTION ----------------
# def get_head_camera():
#     link_index = 24  # head camera

#     link_state = p.getLinkState(pr2, link_index)
#     pos = link_state[0]
#     orn = link_state[1]

#     # rotation
#     rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

#     # IMPORTANT: optical frame fix
#     forward = rot @ np.array([0, 0, 1])
#     up = rot @ np.array([0, -1, 0])

#     view = p.computeViewMatrix(
#         cameraEyePosition=pos,
#         cameraTargetPosition=pos + forward,
#         cameraUpVector=up
#     )

#     proj = p.computeProjectionMatrixFOV(
#         fov=60,
#         aspect=1.0,
#         nearVal=0.01,
#         farVal=5
#     )

#     width, height, rgb, _, _ = p.getCameraImage(256, 256, view, proj)

#     img = np.reshape(rgb, (height, width, 4))[:, :, :3]

#     return img

# # ---------------- LOOP ----------------
# while True:
#     img = get_head_camera()

#     cv2.imshow("Robot Camera View", img)
#     cv2.waitKey(1)

#     p.stepSimulation()
#     time.sleep(1/240)



# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os
# import cv2

# # ---------------- SETUP ----------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# pr2 = p.loadURDF(pr2_urdf, basePosition=[0, 0, 0], useFixedBase=True)

# # Better viewing angle
# p.resetDebugVisualizerCamera(2, 50, -30, [0, 0, 0.5])

# # Object to look at
# cube = p.loadURDF("cube_small.urdf", [0.8, 0, 0.7])

# # ---------------- FIND HEAD JOINTS ----------------
# head_pan_joint = None
# head_tilt_joint = None

# for i in range(p.getNumJoints(pr2)):
#     info = p.getJointInfo(pr2, i)
#     name = info[1].decode()

#     if name == "head_pan_joint":
#         head_pan_joint = i
#     if name == "head_tilt_joint":
#         head_tilt_joint = i

# print("Head pan joint:", head_pan_joint)
# print("Head tilt joint:", head_tilt_joint)

# # ---------------- SLIDERS (REAL JOINT CONTROL) ----------------
# pan_slider = p.addUserDebugParameter("Head Pan (Yaw)", -2.5, 2.5, 0)
# tilt_slider = p.addUserDebugParameter("Head Tilt (Pitch)", -1.5, 1.0, 0)

# # ---------------- CAMERA FUNCTION ----------------
# def get_head_camera():
#     link_index = 24  # high_def_optical_frame

#     link_state = p.getLinkState(pr2, link_index)
#     pos = link_state[0]
#     orn = link_state[1]

#     rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

#     # optical frame correction
#     forward = rot @ np.array([0, 0, 1])
#     up = rot @ np.array([0, -1, 0])

#     view = p.computeViewMatrix(
#         cameraEyePosition=pos,
#         cameraTargetPosition=pos + forward,
#         cameraUpVector=up
#     )

#     proj = p.computeProjectionMatrixFOV(
#         fov=60,
#         aspect=1.0,
#         nearVal=0.01,
#         farVal=5
#     )

#     w, h, rgb, _, _ = p.getCameraImage(256, 256, view, proj)
#     img = np.reshape(rgb, (h, w, 4))[:, :, :3]

#     return img

# # ---------------- MAIN LOOP ----------------
# while True:
#     # Read slider values
#     pan = p.readUserDebugParameter(pan_slider)
#     tilt = p.readUserDebugParameter(tilt_slider)

#     # Apply to robot joints (THIS is the key difference)
#     p.setJointMotorControl2(
#         pr2, head_pan_joint,
#         p.POSITION_CONTROL,
#         targetPosition=pan,
#         force=200
#     )

#     p.setJointMotorControl2(
#         pr2, head_tilt_joint,
#         p.POSITION_CONTROL,
#         targetPosition=tilt,
#         force=200
#     )

#     # Get camera image (now follows head movement)
#     img = get_head_camera()

#     cv2.imshow("Head Camera (Real Movement)", img)
#     cv2.waitKey(1)

#     p.stepSimulation()
#     time.sleep(1/240)


# import pybullet as p
# import pybullet_data
# import numpy as np
# import time
# import os
# import cv2

# # ---------------- SETUP ----------------
# p.connect(p.GUI)
# p.setAdditionalSearchPath(pybullet_data.getDataPath())
# p.setGravity(0, 0, -9.8)

# p.loadURDF("plane.urdf")

# ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
# pr2_urdf = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")

# robot = p.loadURDF(pr2_urdf, basePosition=[0, 0, 0], useFixedBase=True)

# p.resetDebugVisualizerCamera(2, 50, -30, [0, 0, 0.5])

# # ---------------- LOAD CUP ----------------
# cup = p.loadURDF("cube_small.urdf", [0.6, 0, 0.7])

# # ---------------- FIND JOINTS ----------------
# ee_index = None
# head_pan_joint = None
# head_tilt_joint = None

# for i in range(p.getNumJoints(robot)):
#     info = p.getJointInfo(robot, i)
#     name = info[1].decode()
#     link = info[12].decode()

#     if link == "r_gripper_tool_frame":
#         ee_index = i

#     if name == "head_pan_joint":
#         head_pan_joint = i

#     if name == "head_tilt_joint":
#         head_tilt_joint = i

# print("EE:", ee_index)
# print("Head pan:", head_pan_joint)
# print("Head tilt:", head_tilt_joint)

# # ---------------- ARM IK ----------------
# def reach(pos):
#     orn = p.getQuaternionFromEuler([0, 0, 0])

#     ik = p.calculateInverseKinematics(robot, ee_index, pos, orn)

#     # apply only first few joints (safe for PR2)
#     for j in range(7):
#         p.setJointMotorControl2(
#             robot, j,
#             p.POSITION_CONTROL,
#             targetPosition=ik[j],
#             force=500
#         )

# # ---------------- ATTACH CUP ----------------
# def attach(cup_id):
#     return p.createConstraint(
#         parentBodyUniqueId=robot,
#         parentLinkIndex=ee_index,
#         childBodyUniqueId=cup_id,
#         childLinkIndex=-1,
#         jointType=p.JOINT_FIXED,
#         jointAxis=[0, 0, 0],
#         parentFramePosition=[0, 0, 0],
#         childFramePosition=[0, 0.06, 0],
#         parentFrameOrientation=[0, 0, 0, 1],
#         childFrameOrientation=p.getQuaternionFromEuler([-np.pi/2, 0, 0])
#     )

# # ---------------- HEAD LOOK AT ----------------
# def look_at(target):
#     cam_link = 24

#     cam_pos, cam_orn = p.getLinkState(robot, cam_link)[:2]

#     cam_pos = np.array(cam_pos)
#     target = np.array(target)

#     direction = target - cam_pos
#     dx, dy, dz = direction

#     yaw = np.arctan2(dy, dx)
#     dist = np.sqrt(dx**2 + dy**2)
#     pitch = -np.arctan2(dz, dist)

#     p.setJointMotorControl2(
#         robot, head_pan_joint,
#         p.POSITION_CONTROL,
#         targetPosition=yaw,
#         force=200
#     )

#     p.setJointMotorControl2(
#         robot, head_tilt_joint,
#         p.POSITION_CONTROL,
#         targetPosition=pitch,
#         force=200
#     )

# # ---------------- CAMERA ----------------
# def camera():
#     link = 24

#     pos, orn = p.getLinkState(robot, link)[:2]

#     rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

#     forward = rot @ np.array([0, 0, 1])
#     up = rot @ np.array([0, -1, 0])

#     view = p.computeViewMatrix(
#         cameraEyePosition=pos,
#         cameraTargetPosition=pos + forward,
#         cameraUpVector=up
#     )

#     proj = p.computeProjectionMatrixFOV(
#         fov=60,
#         aspect=1.0,
#         nearVal=0.01,
#         farVal=5
#     )

#     w, h, rgb, _, _ = p.getCameraImage(256, 256, view, proj)

#     img = np.reshape(rgb, (h, w, 4))[:, :, :3]
#     return img

# # ---------------- WAIT ----------------
# for _ in range(100):
#     p.stepSimulation()
#     time.sleep(1/240)

# # ---------------- GRASP CUP ----------------
# constraint = attach(cup)
# print("Cup attached")

# # ---------------- MAIN LOOP ----------------
# for i in range(1000):

#     # simple stable arm pose (no oscillation here)
#     reach([0.4, 0, 0.8])

#     # cup position
#     cup_pos, _ = p.getBasePositionAndOrientation(cup)

#     # head tracks cup
#     look_at(cup_pos)

#     # camera view
#     img = camera()

#     cv2.imshow("PR2 Head Camera", img)
#     cv2.waitKey(1)

#     p.stepSimulation()
#     time.sleep(1/240)




import pybullet as p
import pybullet_data
import numpy as np
import time
import os
import cv2

# ---------------- SETUP ----------------
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

p.loadURDF("plane.urdf")

ASSET_ROOT = "C:/Users/Oyinloluwa Olatunji/Desktop/red_team/assets"
PR2_URDF = os.path.join(ASSET_ROOT, "PR2", "pr2_no_torso_lift_tall.urdf")
CUP_PATH = os.path.join(ASSET_ROOT, "dinnerware", "plastic_coffee_cup.obj")

robot = p.loadURDF(PR2_URDF, basePosition=[0, 0, 0], useFixedBase=True)

p.resetDebugVisualizerCamera(2, 50, -30, [0, 0, 0.5])

# ---------------- LEFT ARM DOWN ----------------
left_joint_names = [
    "l_shoulder_pan_joint",
    "l_shoulder_lift_joint",
    "l_upper_arm_roll_joint",
    "l_elbow_flex_joint",
    "l_forearm_roll_joint",
    "l_wrist_flex_joint",
    "l_wrist_roll_joint",
]

left_arm_down = [1.5, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0]

left_joints = []
for name in left_joint_names:
    for i in range(p.getNumJoints(robot)):
        joint_name = p.getJointInfo(robot, i)[1].decode()
        if joint_name == name:
            left_joints.append(i)
            break

for j, pos in zip(left_joints, left_arm_down):
    p.resetJointState(robot, j, pos)
    p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, pos, force=500)

# ---------------- FIND IMPORTANT JOINTS ----------------
ee_index = None
head_pan = None
head_tilt = None
gripper_fingers = []

for i in range(p.getNumJoints(robot)):
    info = p.getJointInfo(robot, i)
    name = info[1].decode()
    link = info[12].decode()

    if link == "r_gripper_tool_frame":
        ee_index = i

    if name == "head_pan_joint":
        head_pan = i

    if name == "head_tilt_joint":
        head_tilt = i

    if "r_gripper" in name and "finger" in name:
        gripper_fingers.append(i)

print("EE:", ee_index)

# ---------------- LOAD CUP (REAL MESH) ----------------
cup_visual = p.createVisualShape(
    shapeType=p.GEOM_MESH,
    fileName=CUP_PATH,
    meshScale=[0.06, 0.06, 0.06],
    rgbaColor=[0, 0, 1, 1]
)

cup_collision = p.createCollisionShape(
    shapeType=p.GEOM_MESH,
    fileName=CUP_PATH,
    meshScale=[0.06, 0.06, 0.06]
)

cup = p.createMultiBody(
    baseMass=0.15,
    baseCollisionShapeIndex=cup_collision,
    baseVisualShapeIndex=cup_visual,
    basePosition=[0.6, 0, 0.7]
)

# ---------------- GRIPPER OPENING ----------------
def open_gripper():
    for j in gripper_fingers:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.04, force=50)

def close_gripper():
    for j in gripper_fingers:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.0, force=200)

open_gripper()

# ---------------- ATTACH CUP ----------------
def attach_cup():
    return p.createConstraint(
        robot, ee_index,
        cup, -1,
        p.JOINT_FIXED,
        [0, 0, 0],
        [0, 0, 0],
        [0, 0.05, 0],  # slight offset so it sits in gripper
        childFrameOrientation=p.getQuaternionFromEuler([-np.pi/2, 0, 0])
    )

# ---------------- HEAD LOOK ----------------
def look_at(target):
    cam_link = 24

    pos, orn = p.getLinkState(robot, cam_link)[:2]

    pos = np.array(pos)
    target = np.array(target)

    d = target - pos
    dx, dy, dz = d

    yaw = np.arctan2(dy, dx)
    dist = np.sqrt(dx**2 + dy**2)
    pitch = -np.arctan2(dz, dist)

    p.setJointMotorControl2(robot, head_pan, p.POSITION_CONTROL, yaw, force=200)
    p.setJointMotorControl2(robot, head_tilt, p.POSITION_CONTROL, pitch, force=200)

# ---------------- CAMERA ----------------
def camera():
    link = 24
    pos, orn = p.getLinkState(robot, link)[:2]

    rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

    forward = rot @ np.array([0, 0, 1])
    up = rot @ np.array([0, -1, 0])

    view = p.computeViewMatrix(pos, pos + forward, up)
    proj = p.computeProjectionMatrixFOV(60, 1.0, 0.01, 5)

    _, _, rgb, _, _ = p.getCameraImage(256, 256, view, proj)

    return np.reshape(rgb, (256, 256, 4))[:, :, :3]

# ---------------- SIMPLE OBJECT "RECOGNITION" ----------------
def detect_object(img):
    # simple placeholder "recognition"
    # (replace later with CLIP / YOLO / etc.)
    mean_color = np.mean(img)

    if mean_color > 50:
        return "cup_detected"
    return "unknown"

# ---------------- WAIT ----------------
for _ in range(100):
    p.stepSimulation()
    time.sleep(1/240)

# ---------------- GRASP SEQUENCE ----------------
time.sleep(1)

constraint = attach_cup()
close_gripper()

print("Cup attached")

# ---------------- MAIN LOOP ----------------
for i in range(1000):

    cup_pos, _ = p.getBasePositionAndOrientation(cup)

    # move head to cup
    look_at(cup_pos)

    # camera
    img = camera()

    # object recognition step (simple placeholder)
    label = detect_object(img)
    print("Vision:", label)

    cv2.imshow("Head Camera", img)
    cv2.waitKey(1)

    p.stepSimulation()
    time.sleep(1/240)