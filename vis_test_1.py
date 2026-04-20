import pybullet as p
import pybullet_data
import numpy as np
import time
import os
import cv2
import ollama
import base64

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

# ---------------- LEFT ARM PARK ----------------
left_joint_names = [
    "l_shoulder_pan_joint",
    "l_shoulder_lift_joint",
    "l_upper_arm_roll_joint",
    "l_elbow_flex_joint",
    "l_forearm_roll_joint",
    "l_wrist_flex_joint",
    "l_wrist_roll_joint",
]

left_positions = [1.5, 2.0, 0, 0, 0, 0, 0]

left_joints = []
for name in left_joint_names:
    for i in range(p.getNumJoints(robot)):
        if p.getJointInfo(robot, i)[1].decode() == name:
            left_joints.append(i)
            break

for j, pos in zip(left_joints, left_positions):
    p.resetJointState(robot, j, pos)
    p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, pos, force=500)

# ---------------- JOINTS ----------------
ee_index = None
head_pan = None
head_tilt = None
gripper = []

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
        gripper.append(i)

print("EE:", ee_index)

# ---------------- CUP ----------------
cup = p.createMultiBody(
    baseMass=0.15,
    baseCollisionShapeIndex=p.createCollisionShape(p.GEOM_MESH, fileName=CUP_PATH, meshScale=[0.06]*3),
    baseVisualShapeIndex=p.createVisualShape(p.GEOM_MESH, fileName=CUP_PATH, meshScale=[0.06]*3),
    basePosition=[0.6, 0, 0.7],
)

# ---------------- GRIPPER ----------------
def open_gripper():
    for j in gripper:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.04, force=50)

def close_gripper():
    for j in gripper:
        p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, 0.0, force=200)

open_gripper()

# ---------------- ATTACH ----------------
def attach():
    return p.createConstraint(
        robot, ee_index,
        cup, -1,
        p.JOINT_FIXED,
        [0, 0, 0],
        [0, 0, 0],
        [0, 0.05, 0],
        childFrameOrientation=p.getQuaternionFromEuler([-np.pi/2, 0, 0])
    )

# ---------------- CAMERA ----------------
def get_camera():
    cam = 24
    pos, orn = p.getLinkState(robot, cam)[:2]

    rot = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)

    forward = rot @ np.array([0, 0, 1])
    up = rot @ np.array([0, -1, 0])

    view = p.computeViewMatrix(pos, pos + forward, up)
    proj = p.computeProjectionMatrixFOV(60, 1, 0.01, 5)

    _, _, rgb, _, _ = p.getCameraImage(256, 256, view, proj)
    return np.reshape(rgb, (256, 256, 4))[:, :, :3]

# ---------------- HEAD CONTROL ----------------
def look_at(target):
    cam_pos, _ = p.getLinkState(robot, 24)[:2]
    cam_pos = np.array(cam_pos)
    target = np.array(target)

    d = target - cam_pos
    dx, dy, dz = d

    yaw = np.arctan2(dy, dx)
    dist = np.sqrt(dx**2 + dy**2)
    pitch = -np.arctan2(dz, dist)

    p.setJointMotorControl2(robot, head_pan, p.POSITION_CONTROL, yaw, force=200)
    p.setJointMotorControl2(robot, head_tilt, p.POSITION_CONTROL, pitch, force=200)

# ---------------- TOOL FUNCTIONS ----------------
def reach(x, y, z):
    ik = p.calculateInverseKinematics(robot, ee_index, [x, y, z])
    for i in range(7):
        p.setJointMotorControl2(robot, i, p.POSITION_CONTROL, ik[i], force=500)

# ---------------- VISION ENCODING ----------------
def encode(img):
    _, buf = cv2.imencode(".jpg", img)
    return base64.b64encode(buf).decode()

# ---------------- QWEN-VL AGENT ----------------
def agent_step(img):
    b64 = encode(img)

    response = ollama.chat(
        model="qwen3-vl:8b",
        messages=[
            {
                "role": "system",
                "content": """
You are a PR2 assistive robot.

You can output ONLY JSON:

Actions:
- look_at(x,y,z)
- reach(x,y,z)
- open_gripper
- close_gripper
- inspect

Always:
1. understand scene
2. decide action
3. output JSON only
"""
            },
            {
                "role": "user",
                "content": "What should the robot do next?",
                "images": [b64]
            }
        ]
    )

    return response["message"]["content"]

# ---------------- INIT ----------------
for _ in range(100):
    p.stepSimulation()
    time.sleep(1/240)

cid = attach()
close_gripper()

print("Cup attached")

# ---------------- LOOP ----------------
for i in range(1000):

    img = get_camera()

    cv2.imshow("PR2 Camera", img)
    cv2.waitKey(1)

    output = agent_step(img)

    print(output)

    # NOTE: you would parse JSON here in real system
    # kept minimal for clarity

    cup_pos, _ = p.getBasePositionAndOrientation(cup)
    look_at(cup_pos)

    p.stepSimulation()
    time.sleep(1/240)